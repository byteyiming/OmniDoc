'use client';

import { useState, useEffect, useMemo, lazy, Suspense } from 'react';
import { useRouter } from 'next/navigation';
import { PlaceholdersAndVanishInput } from '@/components/PlaceholdersAndVanishInput';
import HeroSection from '@/components/HeroSection';
import HowItWorks from '@/components/HowItWorks';
import { createProject, createBrickAndMortarProject } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import { type ViewMode } from '@/lib/documentRanking';
import { DOCUMENT_TEMPLATES } from '@/lib/documentTemplates';

// Lazy load heavy components for better code splitting
const TemplateSelector = lazy(() => import('@/components/TemplateSelector'));
const OptionsSelector = lazy(() => import('@/components/OptionsSelector'));

export default function Home() {
  const router = useRouter();
  const { t, language } = useI18n();
  const [userIdea, setUserIdea] = useState('');
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('all');
  const [organizationMode, setOrganizationMode] = useState<'category' | 'level'>('category');
  

  // Multi-language placeholders based on current language
  const placeholders = {
    en: [
      'Describe your project idea in detail...',
      'What problem does your project solve?',
      'Who is your target audience?',
      'What are the key features you want?',
      'Describe your business model...',
    ],
    zh: [
      '详细描述您的项目想法...',
      '您的项目要解决什么问题？',
      '您的目标用户是谁？',
      '您想要哪些核心功能？',
      '描述您的商业模式...',
    ],
    ja: [
      'プロジェクトのアイデアを詳しく説明してください...',
      'プロジェクトはどのような問題を解決しますか？',
      'ターゲットオーディエンスは誰ですか？',
      'どのような主要機能が必要ですか？',
      'ビジネスモデルを説明してください...',
    ],
    ko: [
      '프로젝트 아이디어를 자세히 설명하세요...',
      '프로젝트가 해결하는 문제는 무엇인가요?',
      '타겟 고객은 누구인가요?',
      '원하는 주요 기능은 무엇인가요?',
      '비즈니스 모델을 설명하세요...',
    ],
    es: [
      'Describe tu idea de proyecto en detalle...',
      '¿Qué problema resuelve tu proyecto?',
      '¿Quién es tu audiencia objetivo?',
      '¿Qué características clave deseas?',
      'Describe tu modelo de negocio...',
    ],
  };

  const currentPlaceholders = placeholders[language] || placeholders.en;

  // Start with empty selection - users must explicitly select documents
  // Don't load from localStorage - always start fresh

  // Save selections to localStorage (for potential future use, but don't auto-load)
  useEffect(() => {
    if (typeof window !== 'undefined' && selectedDocuments.length > 0) {
      localStorage.setItem(
        'omniDoc_selectedDocuments',
        JSON.stringify(selectedDocuments)
      );
    } else if (typeof window !== 'undefined' && selectedDocuments.length === 0) {
      // Clear localStorage when no documents are selected
      localStorage.removeItem('omniDoc_selectedDocuments');
    }
  }, [selectedDocuments]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    if (value.length <= 5000) {
      setUserIdea(value);
    }
  };

  // Detect if brick-and-mortar template is selected
  const isBrickAndMortarTemplate = useMemo(() => {
    if (selectedDocuments.length === 0) return false;
    const brickAndMortarTemplate = DOCUMENT_TEMPLATES.find((t) => t.id === 'brick_and_mortar');
    if (!brickAndMortarTemplate) return false;
    
    const selectedSet = new Set(selectedDocuments);
    const templateDocIds = brickAndMortarTemplate.documentIds;
    
    // Check if all brick-and-mortar documents are selected and they match exactly
    return (
      templateDocIds.length > 0 &&
      templateDocIds.every((id) => selectedSet.has(id)) &&
      templateDocIds.length === selectedDocuments.length
    );
  }, [selectedDocuments]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!userIdea.trim()) {
      setError(t('project.idea.placeholder'));
      return;
    }

    // For brick-and-mortar template, we don't need to check selectedDocuments
    // because the API will automatically select all 12 documents
    if (!isBrickAndMortarTemplate && selectedDocuments.length === 0) {
      setError(t('documents.select'));
      return;
    }

    setIsSubmitting(true);

    try {
      let response;
      
      if (isBrickAndMortarTemplate) {
        // Use the specialized brick-and-mortar endpoint
        response = await createBrickAndMortarProject({
          user_idea: userIdea.trim(),
        });
      } else {
        // Use the regular project creation endpoint
        response = await createProject({
          user_idea: userIdea.trim(),
          selected_documents: selectedDocuments,
        });
      }

      // Navigate to project status page
      router.push(`/project/${response.project_id}`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : t('error.createProject');
      console.error('Error creating project:', err);
      setError(errorMessage);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <HeroSection />

      {/* How It Works Section */}
      <HowItWorks />

      {/* Main Form Section - Vertical Layout: Template -> Options (with Document Selector) -> Input */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 py-6 sm:py-12">
        <div className="flex flex-col space-y-4 sm:space-y-6">
          {/* Row 1: Template Selector - Lazy loaded */}
          <div className="w-full">
            <Suspense fallback={<div className="h-32 bg-gray-100 animate-pulse rounded-lg" />}>
              <TemplateSelector
                selectedDocuments={selectedDocuments}
                onSelectionChange={setSelectedDocuments}
              />
            </Suspense>
          </div>

          {/* Row 2: Options Selector (Collapsible, contains Document Selector) - Lazy loaded */}
          <div className="w-full">
            <Suspense fallback={<div className="h-48 bg-gray-100 animate-pulse rounded-lg" />}>
              <OptionsSelector
                selectedDocuments={selectedDocuments}
                onSelectionChange={setSelectedDocuments}
                viewMode={viewMode}
                onViewModeChange={setViewMode}
                organizationMode={organizationMode}
                onOrganizationModeChange={setOrganizationMode}
              />
            </Suspense>
          </div>

          {/* Row 3: Input Area */}
          <div className="w-full">
            <PlaceholdersAndVanishInput
              placeholders={currentPlaceholders}
              value={userIdea}
              onChange={handleChange}
              onSubmit={handleSubmit}
              disabled={isSubmitting}
              maxLength={5000}
              minHeight="120px"
              isSubmitting={isSubmitting}
            />
            {/* Character Count */}
            <div className="mt-2 flex justify-end">
              <span className={`text-xs sm:text-sm ${
                userIdea.length >= 5000 
                  ? 'text-red-600 font-medium' 
                  : userIdea.length >= 4500 
                    ? 'text-yellow-600' 
                    : 'text-gray-500'
              }`}>
                {userIdea.length} / 5000
              </span>
            </div>
            {error && (
              <div className="mt-2 text-xs sm:text-sm text-red-600 text-center px-2" suppressHydrationWarning>
                {error}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
