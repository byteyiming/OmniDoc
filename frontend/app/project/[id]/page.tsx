'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter, useParams } from 'next/navigation';
import ProgressTimeline from '@/components/ProgressTimeline';
import GeneratingAnimation from '@/components/GeneratingAnimation';
import { useProjectStatus } from '@/lib/useProjectStatus';
import { getWebSocketUrl } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import { logger } from '@/lib/logger';

interface ProgressEvent {
  type: string;
  project_id?: string;
  document_id?: string;
  name?: string;
  index?: string;
  total?: string;
  status?: string;
  message?: string;
  timestamp?: string;
  files_count?: number;
}

export default function ProjectStatusPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const { t } = useI18n();

  const [events, setEvents] = useState<ProgressEvent[]>([]);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);
  const maxReconnectAttempts = 10;
  const isMountedRef = useRef<boolean>(true);

  // Fallback polling with SWR
  const { status, isLoading } = useProjectStatus(projectId, {
    refreshInterval: wsConnected ? 0 : 2000, // Only poll if WS is not connected
    enabled: !!projectId,
  });

  // WebSocket connection with exponential backoff
  useEffect(() => {
    if (!projectId) return;
    
    isMountedRef.current = true;
    reconnectAttemptsRef.current = 0;

    const connectWebSocket = () => {
      if (!isMountedRef.current) return;
      
      // Check max reconnect attempts
      if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
        logger.warn('Max WebSocket reconnect attempts reached, falling back to polling', {
          projectId,
          attempts: reconnectAttemptsRef.current,
          maxAttempts: maxReconnectAttempts,
        });
        setWsConnected(false);
        return;
      }

      try {
        const wsUrl = getWebSocketUrl(projectId);
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          if (!isMountedRef.current) {
            ws.close();
            return;
          }
          setWsConnected(true);
          reconnectAttemptsRef.current = 0; // Reset on successful connection
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
          }
          logger.websocketEvent('connected', projectId, { attempts: reconnectAttemptsRef.current });
        };

        ws.onmessage = (event) => {
          if (!isMountedRef.current) return;
          
          try {
            const data: ProgressEvent = JSON.parse(event.data);
            logger.websocketEvent('message', projectId, { type: data.type, document_id: data.document_id });
            
            // Prevent duplicate events
            setEvents((prev) => {
              // Create unique ID for this event
              const eventId = `${data.type}-${data.document_id || data.project_id || ''}`;
              const existingIds = new Set(
                prev.map(e => `${e.type}-${e.document_id || e.project_id || ''}`)
              );
              
              // Special handling for 'complete' events - only allow one
              if (data.type === 'complete') {
                if (prev.some(e => e.type === 'complete')) {
                  return prev; // Skip duplicate complete events
                }
              }
              
              // Skip if event already exists
              if (existingIds.has(eventId)) {
                return prev;
              }
              
              return [...prev, data];
            });

            // Navigate to results when complete
            if (data.type === 'complete') {
              logger.info('Document generation completed, navigating to results', { projectId });
              setTimeout(() => {
                if (isMountedRef.current) {
                  router.push(`/project/${projectId}/results`);
                }
              }, 2000);
            }
          } catch (err) {
            logger.error('Failed to parse WebSocket message', err, { projectId, message: event.data });
          }
        };

        ws.onerror = () => {
          if (!isMountedRef.current) return;
          logger.warn('WebSocket error', { projectId, attempts: reconnectAttemptsRef.current });
          setWsConnected(false);
          // Don't show error to user - polling will handle updates gracefully
        };

        ws.onclose = (event) => {
          if (!isMountedRef.current) return;
          logger.websocketEvent('closed', projectId, { code: event.code, reason: event.reason, wasClean: event.wasClean });
          
          setWsConnected(false);
          
          // Only attempt to reconnect if it wasn't a normal closure
          // and we haven't already scheduled a reconnect
          if (event.code !== 1000 && !reconnectTimeoutRef.current && isMountedRef.current) {
            reconnectAttemptsRef.current += 1;
            
            // Exponential backoff: 1s, 2s, 4s, 8s, 16s, 30s (max)
            const baseDelay = 1000;
            const maxDelay = 30000;
            const delay = Math.min(baseDelay * Math.pow(2, reconnectAttemptsRef.current - 1), maxDelay);
            
            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectTimeoutRef.current = null;
              if (isMountedRef.current) {
                connectWebSocket();
              }
            }, delay);
          }
        };

        wsRef.current = ws;
      } catch (err) {
        logger.error('Failed to create WebSocket', err, { projectId, url: getWebSocketUrl(projectId) });
        setWsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      isMountedRef.current = false;
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
    };
  }, [projectId, router]);

  // Update events from polling status (fallback when WebSocket is not connected)
  useEffect(() => {
    if (!status) return;
    
    // Always sync from status, but avoid duplicates
    setEvents((prev) => {
      const statusEvents: ProgressEvent[] = [];
      const existingIds = new Set(
        prev.map(e => `${e.type}-${e.document_id || e.project_id || ''}`)
      );
      
      // Add start event if in progress (only if not already exists)
      // Check both 'start-' and 'plan-' to avoid duplicates
      if ((status.status === 'in_progress' || status.status === 'complete') && 
          !existingIds.has('start-') && 
          !prev.some(e => e.type === 'start' || e.type === 'plan')) {
        statusEvents.push({
          type: 'start',
          project_id: status.project_id,
          timestamp: status.updated_at,
        });
      }
      
      // Add plan event with total count (only if not already exists)
      if ((status.status === 'in_progress' || status.status === 'complete') && 
          !existingIds.has('plan-') && 
          !prev.some(e => e.type === 'plan') &&
          status.selected_documents?.length) {
        statusEvents.push({
          type: 'plan',
          project_id: status.project_id,
          total: String(status.selected_documents.length),
          timestamp: status.updated_at,
        });
      }
      
      // Add completed documents
      if (status.completed_documents?.length) {
        status.completed_documents.forEach((docId, index) => {
          const eventId = `document_completed-${docId}`;
          if (!existingIds.has(eventId)) {
            statusEvents.push({
              type: 'document_completed',
              document_id: docId,
              index: String(index + 1),
              total: String(status.selected_documents?.length || 0),
              timestamp: status.updated_at,
            });
          }
        });
      }
      
      if (status.status === 'complete' && 
          !existingIds.has('complete-') && 
          !prev.some(e => e.type === 'complete')) {
        statusEvents.push({
          type: 'complete',
          project_id: status.project_id,
          files_count: status.completed_documents?.length || 0,
          timestamp: status.updated_at,
        });
      } else if (status.status === 'failed' && !existingIds.has('error-')) {
        statusEvents.push({
          type: 'error',
          project_id: status.project_id,
          message: status.error || 'Generation failed',
          timestamp: status.updated_at,
        });
      }

      return statusEvents.length > 0 ? [...prev, ...statusEvents] : prev;
    });
  }, [status, wsConnected]); // Sync from status polling

  const handleViewResults = () => {
    router.push(`/project/${projectId}/results`);
  };

  const isComplete =
    status?.status === 'complete' ||
    events.some((e) => e.type === 'complete');

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-4xl px-4 py-12">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">{t('status.title')}</h1>
          <p className="mt-2 text-sm text-gray-600">{t('status.projectId')}: {projectId}</p>
        </div>

        {/* Connection Status */}
        <div className="mb-6 rounded-lg bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div
                className={`h-3 w-3 rounded-full ${
                  wsConnected ? 'bg-green-500' : 'bg-yellow-500'
                }`}
              />
              <span className="text-sm text-gray-700">
                {wsConnected
                  ? t('status.connected')
                  : t('status.polling')}
              </span>
            </div>
            {status && (
              <span
                className={`rounded-full px-3 py-1 text-sm font-medium ${
                  status.status === 'complete'
                    ? 'bg-green-100 text-green-800'
                    : status.status === 'failed'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-blue-100 text-blue-800'
                }`}
              >
                {status.status}
              </span>
            )}
          </div>
        </div>

        {/* Progress Timeline */}
        <div className="rounded-lg bg-white p-6 shadow-sm">
          {isLoading && events.length === 0 ? (
            <div className="flex items-center justify-center p-8">
              <div className="text-gray-500">{t('status.loading')}</div>
            </div>
          ) : (
            <>
              {/* Show timeline if there are events */}
              {events.length > 0 ? (
                <>
                  <ProgressTimeline
                    events={events}
                    total={status?.selected_documents.length}
                  />
                  {/* Show generating animation below timeline if still in progress */}
                  {status?.status === 'in_progress' && 
                   !events.some(e => e.type === 'complete') && (
                    <div className="mt-6 border-t border-gray-200 pt-6">
                      <GeneratingAnimation />
                    </div>
                  )}
                </>
              ) : (
                /* Show generating animation if in progress but no events yet */
                status?.status === 'in_progress' && <GeneratingAnimation />
              )}
            </>
          )}
        </div>

        {/* Action Buttons */}
        {isComplete && (
          <div className="mt-6 flex justify-end">
            <button
              onClick={handleViewResults}
              className="rounded-lg bg-blue-600 px-6 py-3 font-medium text-white hover:bg-blue-700"
            >
              {t('button.viewResults')} →
            </button>
          </div>
        )}

        {status?.error && (
          <div className="mt-6 rounded-lg bg-red-50 p-4 text-red-800">
            <div className="font-medium">{t('status.error')}:</div>
            <div className="mt-1 text-sm">{status.error}</div>
          </div>
        )}
      </div>
    </div>
  );
}

