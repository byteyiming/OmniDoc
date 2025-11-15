'use client';

import { getDocumentIcon } from '@/lib/documentRanking';
import { useI18n, getDocumentName } from '@/lib/i18n';

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
}

interface ProgressTimelineProps {
  events: ProgressEvent[];
  total?: number;
}

export default function ProgressTimeline({
  events,
  total,
}: ProgressTimelineProps) {
  const { t } = useI18n();
  const getEventIcon = (event: ProgressEvent) => {
    // For document_completed events, use the document's level icon
    if (event.type === 'document_completed' && event.document_id) {
      return getDocumentIcon(event.document_id);
    }
    
    // For other event types, use default icons
    switch (event.type) {
      case 'start':
      case 'plan':
        return '🚀';
      case 'document_started':
        return '⏳';
      case 'complete':
        return '🎉';
      case 'error':
        return '❌';
      default:
        return '📝';
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'start':
      case 'plan':
        return 'bg-blue-500';
      case 'document_started':
        return 'bg-yellow-500';
      case 'document_completed':
        return 'bg-green-500';
      case 'complete':
        return 'bg-purple-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getEventMessage = (event: ProgressEvent) => {
    switch (event.type) {
      case 'start':
        return t('status.generationStarted');
      case 'plan':
        return `${t('status.planning')} ${event.total || '?'} ${t('status.documents')}`;
      case 'document_started':
        return `${t('status.generating')}: ${getDocumentName(event.document_id || '') || event.name || event.document_id}`;
      case 'document_completed':
        return `${t('status.completed')}: ${getDocumentName(event.document_id || '') || event.name || event.document_id}`;
      case 'quality_review_started':
        return `${t('status.reviewing')}: ${getDocumentName(event.document_id || '') || event.name || event.document_id}`;
      case 'quality_review_completed':
        return `${t('status.reviewCompleted')}: ${getDocumentName(event.document_id || '') || event.name || event.document_id}`;
      case 'improvement_started':
        return `${t('status.improving')}: ${getDocumentName(event.document_id || '') || event.name || event.document_id}`;
      case 'improvement_completed':
        return `${t('status.improvementCompleted')}: ${getDocumentName(event.document_id || '') || event.name || event.document_id}`;
      case 'complete':
        return `${t('status.allDone')} ${(event as any).files_count || 0} ${t('status.documents')}`;
      case 'error':
        return `${t('status.error')}: ${event.message || 'Unknown error'}`;
      case 'heartbeat':
        // Don't show heartbeat messages
        return null;
      default:
        // For unknown types, try to show document name if available
        if (event.document_id) {
          return getDocumentName(event.document_id) || event.name || event.document_id;
        }
        return event.message || event.type;
    }
  };

  // Always show progress header even if no events yet
  // if (events.length === 0) {
  //   return (
  //     <div className="flex items-center justify-center p-8 text-gray-500">
  //       {t('status.waiting')}
  //     </div>
  //   );
  // }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">{t('status.progress')}</h3>
        {total && (
          <span className="text-sm font-medium text-gray-900">
            {events.filter((e) => e.type === 'document_completed').length}/
            {total} {t('status.completed')}
          </span>
        )}
      </div>

      <div className="relative">
        {/* Timeline line */}
        {events.length > 0 && (
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />
        )}

        <div className="space-y-4">
          {events.length === 0 ? (
            <div className="flex items-center justify-center p-8 text-gray-500">
              {t('status.waiting')}
            </div>
          ) : (
            events
              .filter((event) => {
                // Filter out heartbeat and other non-user-facing events
                const message = getEventMessage(event);
                return message !== null && event.type !== 'heartbeat' && event.type !== 'connected';
              })
              .map((event, index) => {
              const message = getEventMessage(event);
              if (!message) return null;
              
              return (
                <div key={index} className="relative flex items-start space-x-4">
                  {/* Icon */}
                  <div
                    className={`relative z-10 flex h-8 w-8 items-center justify-center rounded-full ${
                      event.type === 'document_completed' 
                        ? 'bg-green-500' 
                        : getEventColor(event.type)
                    } text-white`}
                  >
                    <span className="text-sm">{getEventIcon(event)}</span>
                  </div>

                  {/* Content */}
                  <div className="flex-1 rounded-lg bg-white p-3 shadow-sm">
                    <div className="flex items-center justify-between">
                      <div className="font-medium text-gray-900">
                        {message}
                      </div>
                      {event.timestamp && (
                        <div className="text-xs text-gray-500">
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </div>
                      )}
                    </div>
                    {event.type === 'document_completed' && event.index && event.total && (
                      <div className="mt-2">
                        <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
                          <div
                            className="h-full bg-blue-500 transition-all duration-300"
                            style={{
                              width: '100%', // Always 100% for completed documents
                            }}
                          />
                        </div>
                      </div>
                    )}
                    {event.type !== 'document_completed' && event.index && event.total && (
                      <div className="mt-2">
                        <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
                          <div
                            className="h-full bg-blue-500 transition-all duration-300"
                            style={{
                              width: `${
                                (parseInt(event.index) / parseInt(event.total)) *
                                100
                              }%`,
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

