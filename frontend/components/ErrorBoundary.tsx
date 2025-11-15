'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { useI18n } from '@/lib/i18n';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    // Log error to backend (optional)
    this.logErrorToBackend(error, errorInfo);

    this.setState({
      error,
      errorInfo,
    });
  }

  logErrorToBackend = async (error: Error, errorInfo: ErrorInfo) => {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
      await fetch(`${apiBase}/api/errors`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: error.message,
          stack: error.stack,
          componentStack: errorInfo.componentStack,
          timestamp: new Date().toISOString(),
        }),
      });
    } catch (err) {
      // Silently fail - don't break the error boundary
      console.warn('Failed to log error to backend:', err);
    }
  };

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return <ErrorFallback error={this.state.error} onReset={this.handleReset} />;
    }

    return this.props.children;
  }
}

function ErrorFallback({ error, onReset }: { error: Error | null; onReset: () => void }) {
  const { t } = useI18n();

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full mb-4">
          <svg
            className="w-6 h-6 text-red-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-gray-900 text-center mb-2" suppressHydrationWarning>
          {t('error.boundary.title') || 'Something went wrong'}
        </h2>
        <p className="text-gray-600 text-center mb-4" suppressHydrationWarning>
          {t('error.boundary.message') || 'We encountered an unexpected error. Please try again.'}
        </p>
        {process.env.NODE_ENV === 'development' && error && (
          <details className="mb-4">
            <summary className="text-sm text-gray-500 cursor-pointer mb-2">
              Error details (development only)
            </summary>
            <pre className="text-xs bg-gray-100 p-3 rounded overflow-auto max-h-40">
              {error.message}
              {error.stack && `\n\n${error.stack}`}
            </pre>
          </details>
        )}
        <div className="flex gap-3">
          <button
            onClick={onReset}
            className="flex-1 rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 transition-colors"
            suppressHydrationWarning
          >
            {t('error.boundary.retry') || 'Try Again'}
          </button>
          <button
            onClick={() => (window.location.href = '/')}
            className="flex-1 rounded-lg bg-gray-200 px-4 py-2 font-medium text-gray-700 hover:bg-gray-300 transition-colors"
            suppressHydrationWarning
          >
            {t('error.boundary.home') || 'Go Home'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ErrorBoundary;

