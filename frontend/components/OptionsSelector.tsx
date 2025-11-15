'use client';

import { useState } from 'react';
import { useI18n } from '../lib/i18n';
import { type ViewMode } from '../lib/documentRanking';
import DocumentSelector from './DocumentSelector';

interface OptionsSelectorProps {
  selectedDocuments: string[];
  onSelectionChange: (selected: string[]) => void;
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
  organizationMode: 'category' | 'level';
  onOrganizationModeChange: (mode: 'category' | 'level') => void;
}

export default function OptionsSelector({
  selectedDocuments,
  onSelectionChange,
  viewMode,
  onViewModeChange,
  organizationMode,
  onOrganizationModeChange,
}: OptionsSelectorProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const { t } = useI18n();

  return (
    <div className="w-full">
      <div className="rounded-lg border border-gray-200 bg-white">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between p-3 text-left hover:bg-gray-50 transition-colors rounded-lg"
          suppressHydrationWarning
        >
          <span className="text-sm font-medium text-gray-700" suppressHydrationWarning>
            {t('documents.select')} ({t('documents.view.category')} / {t('documents.view.level')})
          </span>
          <span className="text-gray-500 text-lg">{isExpanded ? '▼' : '▶'}</span>
        </button>

        {isExpanded && (
          <div className="border-t border-gray-200 p-3 space-y-4">
            {/* View Mode Selector */}
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700" suppressHydrationWarning>
                {t('documents.title')}:
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => onViewModeChange('all')}
                  className={`rounded px-3 py-1 text-sm transition-colors ${
                    viewMode === 'all'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  suppressHydrationWarning
                >
                  {t('documents.all')}
                </button>
                <button
                  onClick={() => onViewModeChange('team')}
                  className={`rounded px-3 py-1 text-sm transition-colors ${
                    viewMode === 'team'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  suppressHydrationWarning
                >
                  {t('documents.team')}
                </button>
                <button
                  onClick={() => onViewModeChange('solo')}
                  className={`rounded px-3 py-1 text-sm transition-colors ${
                    viewMode === 'solo'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  suppressHydrationWarning
                >
                  {t('documents.solo')}
                </button>
              </div>
            </div>

            {/* Organization Mode Selector */}
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700" suppressHydrationWarning>
                {t('documents.select')}:
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => onOrganizationModeChange('category')}
                  className={`rounded px-3 py-1 text-sm transition-colors ${
                    organizationMode === 'category'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  suppressHydrationWarning
                >
                  {t('documents.view.category')}
                </button>
                <button
                  onClick={() => onOrganizationModeChange('level')}
                  className={`rounded px-3 py-1 text-sm transition-colors ${
                    organizationMode === 'level'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  suppressHydrationWarning
                >
                  {t('documents.view.level')}
                </button>
              </div>
            </div>

            {/* Document Selector */}
            <div className="rounded-lg bg-white border border-gray-200 p-4 max-h-[600px] overflow-y-auto">
              <DocumentSelector
                selectedDocuments={selectedDocuments}
                onSelectionChange={onSelectionChange}
                viewMode={viewMode}
                organizationMode={organizationMode}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

