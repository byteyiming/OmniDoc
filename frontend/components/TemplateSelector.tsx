'use client';

import { useMemo } from 'react';
import { DocumentTemplate, getDocumentTemplates } from '../lib/api';
import { useI18n } from '../lib/i18n';
import { DOCUMENT_TEMPLATES } from '../lib/documentTemplates';
import { useEffect, useState } from 'react';

interface TemplateSelectorProps {
  selectedDocuments: string[];
  onSelectionChange: (selected: string[]) => void;
}

export default function TemplateSelector({
  selectedDocuments,
  onSelectionChange,
}: TemplateSelectorProps) {
  const [templates, setTemplates] = useState<DocumentTemplate[]>([]);
  const { t } = useI18n();

  useEffect(() => {
    async function loadTemplates() {
      try {
        const response = await getDocumentTemplates();
        setTemplates(response.documents);
      } catch (err) {
        console.error('Error loading document templates:', err);
      }
    }
    loadTemplates();
  }, []);

  // Detect which template is currently selected based on selectedDocuments
  const currentTemplate = useMemo(() => {
    if (selectedDocuments.length === 0) return null;
    const selectedSet = new Set(selectedDocuments);
    for (const template of DOCUMENT_TEMPLATES) {
      const templateDocIds = template.documentIds.filter((id) =>
        templates.some((t) => t.id === id)
      );
      // Check if all template documents are selected and they match exactly
      if (
        templateDocIds.length > 0 &&
        templateDocIds.every((id) => selectedSet.has(id)) &&
        templateDocIds.length === selectedDocuments.length
      ) {
        return template.id;
      }
    }
    return null;
  }, [selectedDocuments, templates]);

  const applyTemplate = (templateId: string) => {
    const template = DOCUMENT_TEMPLATES.find((t) => t.id === templateId);
    if (template) {
      // Filter template document IDs to only include those that exist in templates
      const validDocIds = template.documentIds.filter((id) =>
        templates.some((t) => t.id === id)
      );
      onSelectionChange(validDocIds);
    }
  };

  const clearTemplate = () => {
    onSelectionChange([]);
  };

  return (
    <div className="w-full">
      <div className="rounded-lg border-2 border-indigo-200 bg-indigo-50 shadow-sm">
        <div className="border-b border-indigo-200 bg-indigo-100 p-3">
          <h3 className="flex items-center gap-2 font-semibold text-indigo-900">
            <span className="text-xl">📋</span>
            <span suppressHydrationWarning>{t('documents.templates')}</span>
          </h3>
          <p className="mt-1 text-xs text-indigo-700" suppressHydrationWarning>
            {t('documents.templates.description')}
          </p>
        </div>
        <div className="p-4">
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {DOCUMENT_TEMPLATES.map((template) => {
              const isSelected = currentTemplate === template.id;
              const templateDocCount = template.documentIds.filter((id) =>
                templates.some((t) => t.id === id)
              ).length;

              return (
                <button
                  key={template.id}
                  onClick={() => {
                    if (isSelected) {
                      clearTemplate();
                    } else {
                      applyTemplate(template.id);
                    }
                  }}
                  className={`flex items-start gap-3 rounded-lg border-2 p-3 text-left transition-all ${
                    isSelected
                      ? 'border-indigo-500 bg-indigo-100 shadow-md'
                      : 'border-gray-200 bg-white hover:border-indigo-300 hover:bg-indigo-50'
                  }`}
                  suppressHydrationWarning
                >
                  <span className="text-2xl">{template.icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-900" suppressHydrationWarning>
                      {template.name}
                    </div>
                    <div className="mt-1 text-xs text-gray-600" suppressHydrationWarning>
                      {template.description}
                    </div>
                    <div className="mt-2 text-xs font-medium text-indigo-700" suppressHydrationWarning>
                      {templateDocCount} {t('documents.selected')}
                    </div>
                  </div>
                  {isSelected && <span className="text-indigo-600">✓</span>}
                </button>
              );
            })}
          </div>
          {currentTemplate && (
            <div className="mt-4 flex items-center justify-between rounded-lg bg-indigo-100 p-3">
              <span className="text-sm font-medium text-indigo-900" suppressHydrationWarning>
                {t('documents.templates.apply')}:{' '}
                {DOCUMENT_TEMPLATES.find((t) => t.id === currentTemplate)?.name}
              </span>
              <button
                onClick={clearTemplate}
                className="rounded bg-white px-3 py-1 text-sm font-medium text-indigo-700 hover:bg-indigo-50 transition-colors"
                suppressHydrationWarning
              >
                {t('documents.templates.clear')}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

