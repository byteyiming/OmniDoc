'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import DocumentViewer from '@/components/DocumentViewer';
import { getProjectDocuments, GeneratedDocument } from '@/lib/api';

export default function ProjectResultsPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [documents, setDocuments] = useState<GeneratedDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [shareCopied, setShareCopied] = useState(false);

  useEffect(() => {
    async function loadDocuments() {
      if (!projectId) return;

      try {
        const response = await getProjectDocuments(projectId);
        setDocuments(response.documents);
        setLoading(false);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Failed to load documents'
        );
        setLoading(false);
      }
    }

    loadDocuments();
  }, [projectId]);

  const handleShare = async () => {
    const url = window.location.href;
    try {
      if (navigator.share) {
        // Use native share API if available
        await navigator.share({
          title: 'OmniDoc Generated Documents',
          text: 'Check out these generated project documents',
          url: url,
        });
      } else {
        // Fallback to clipboard
        await navigator.clipboard.writeText(url);
        setShareCopied(true);
        setTimeout(() => setShareCopied(false), 2000);
      }
    } catch (err) {
      // User cancelled share or clipboard failed - try fallback
      try {
        await navigator.clipboard.writeText(url);
        setShareCopied(true);
        setTimeout(() => setShareCopied(false), 2000);
      } catch (clipboardErr) {
        console.error('Failed to copy to clipboard:', clipboardErr);
        // Show error message
        alert('Failed to copy link. Please copy the URL manually: ' + url);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="text-gray-500">Loading documents...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="rounded-lg bg-red-50 p-6 text-red-800">
          <div className="font-medium">Error loading documents</div>
          <div className="mt-2 text-sm">{error}</div>
          <button
            onClick={() => router.push(`/project/${projectId}`)}
            className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-white hover:bg-red-700"
          >
            Back to Status
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-full flex-col bg-gray-50">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Generated Documents
            </h1>
            <p className="mt-1 text-sm text-gray-600">
              Project ID: {projectId}
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleShare}
              className="flex items-center space-x-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
            >
              <span>{shareCopied ? '✓' : '🔗'}</span>
              <span>{shareCopied ? 'Copied!' : 'Share'}</span>
            </button>
            <button
              onClick={() => router.push(`/project/${projectId}`)}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              ← Back to Status
            </button>
            <button
              onClick={() => router.push('/')}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              New Project
            </button>
          </div>
        </div>
      </div>

      {/* Document Viewer */}
      <div className="flex-1 overflow-hidden">
        {documents.length > 0 ? (
          <DocumentViewer documents={documents} projectId={projectId} />
        ) : (
          <div className="flex h-full items-center justify-center">
            <div className="text-center text-gray-500">
              <div className="text-lg font-medium">No documents generated yet</div>
              <div className="mt-2 text-sm">
                Documents may still be generating. Check back in a moment.
              </div>
              <button
                onClick={() => router.push(`/project/${projectId}`)}
                className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
              >
                View Status
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

