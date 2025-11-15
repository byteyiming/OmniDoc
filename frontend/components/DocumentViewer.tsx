'use client';

import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { GeneratedDocument, getDocumentDownloadUrl } from '../lib/api';

interface DocumentViewerProps {
  documents: GeneratedDocument[];
  projectId: string;
}

export default function DocumentViewer({
  documents,
  projectId,
}: DocumentViewerProps) {
  const [selectedDocId, setSelectedDocId] = useState<string | null>(
    documents.length > 0 ? documents[0].id : null
  );
  const contentScrollRef = useRef<HTMLDivElement>(null);

  const selectedDoc = documents.find((doc) => doc.id === selectedDocId);

  // Reset scroll position when document changes
  useEffect(() => {
    if (contentScrollRef.current) {
      contentScrollRef.current.scrollTop = 0;
    }
  }, [selectedDocId]);

  const handleDownload = (docId: string) => {
    const url = getDocumentDownloadUrl(projectId, docId);
    window.open(url, '_blank');
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  return (
    <div className="flex h-full w-full" style={{ height: '100%', overflow: 'hidden' }}>
      {/* Document List Sidebar - Scrollable */}
      <div 
        className="w-64 flex-shrink-0 border-r border-gray-200 bg-gray-50 flex flex-col"
        style={{ height: '100%', overflow: 'hidden' }}
      >
        <div className="p-4 flex-shrink-0 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Documents</h3>
          <div className="mt-2 text-sm text-gray-500">
            {documents.length} document{documents.length !== 1 ? 's' : ''}
          </div>
        </div>
        <div 
          className="flex-1"
          style={{ 
            overflowY: 'auto',
            overflowX: 'hidden',
            minHeight: 0,
            height: 0 // Force flex child to respect parent height
          }}
        >
          <div className="space-y-1 p-2">
            {documents.map((doc) => (
              <button
                key={doc.id}
                onClick={() => setSelectedDocId(doc.id)}
                className={`w-full rounded-lg p-3 text-left transition-colors ${
                  selectedDocId === doc.id
                    ? 'bg-blue-50 text-gray-900'
                    : 'text-gray-900 hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 truncate font-medium text-gray-900">{doc.name}</div>
                  <span
                    className={`ml-2 rounded-full px-2 py-0.5 text-xs flex-shrink-0 ${
                      doc.status === 'complete'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {doc.status}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Document Content */}
      <div 
        className="flex-1 flex-shrink-0 flex flex-col bg-white"
        style={{ height: '100%', overflow: 'hidden' }}
      >
        {selectedDoc ? (
          <>
            {/* Header - Sticky */}
            <div className="flex-shrink-0 border-b border-gray-200 bg-white p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">{selectedDoc.name}</h2>
                </div>
                <div className="flex space-x-2">
                  {selectedDoc.content && (
                    <button
                      onClick={() => copyToClipboard(selectedDoc.content!)}
                      className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                      Copy
                    </button>
                  )}
                  {selectedDoc.file_path && (
                    <button
                      onClick={() => handleDownload(selectedDoc.id)}
                      className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                    >
                      Download
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Content - Scrollable */}
            <div 
              ref={contentScrollRef}
              className="flex-1"
              style={{ 
                overflowY: 'auto',
                overflowX: 'hidden',
                minHeight: 0,
                height: 0 // Force flex child to respect parent height
              }}
            >
              <div className="p-6">
                {selectedDoc.content ? (
                  <div className="prose max-w-none text-gray-900">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {selectedDoc.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <div className="flex items-center justify-center p-12 text-gray-500">
                    <div className="text-center">
                      <div className="text-lg font-medium">No content available</div>
                      <div className="mt-2 text-sm">
                        {selectedDoc.status === 'pending'
                          ? 'Document is still being generated...'
                          : 'Document content is not available'}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="flex h-full items-center justify-center text-gray-500">
            <div className="text-center">
              <div className="text-lg font-medium">No document selected</div>
              <div className="mt-2 text-sm">
                Select a document from the list to view its content
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

