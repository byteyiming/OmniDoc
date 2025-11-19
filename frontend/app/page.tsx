'use client';

import { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { createProject, createBrickAndMortarProject } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import { type ViewMode } from '@/lib/documentRanking';
import { DOCUMENT_TEMPLATES } from '@/lib/documentTemplates';
import { ArrowRight, Sparkles, Zap, CheckCircle2, Layout } from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { AgentAvatar } from '@/components/ui/AgentAvatar';
import TemplateSelector from '@/components/TemplateSelector';
import OptionsSelector from '@/components/OptionsSelector';
import { PlaceholdersAndVanishInput } from '@/components/PlaceholdersAndVanishInput';

export default function Home() {
  const router = useRouter();
  const { t, language } = useI18n();
  const [userIdea, setUserIdea] = useState('');
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // UI State for the wizard flow
  const [step, setStep] = useState(1); // 1: Idea, 2: Templates/Docs

  // Multi-language placeholders
  const placeholders = {
    en: ['Describe your project idea in detail...', 'What problem does it solve?', 'Who is the target audience?'],
    zh: ['详细描述您的项目想法...', '您的项目要解决什么问题？', '您的目标用户是谁？'],
    ja: ['プロジェクトのアイデアを詳しく説明してください...', 'どのような問題を解決しますか？', 'ターゲットは誰ですか？'],
    ko: ['프로젝트 아이디어를 자세히 설명하세요...', '해결하려는 문제는 무엇인가요?', '타겟 고객은 누구인가요?'],
    es: ['Describe tu idea de proyecto...', '¿Qué problema resuelve?', '¿Quién es tu audiencia?'],
  };

  const currentPlaceholders = placeholders[language] || placeholders.en;

  // Detect if brick-and-mortar template is selected
  const isBrickAndMortarTemplate = useMemo(() => {
    if (selectedDocuments.length === 0) return false;
    const template = DOCUMENT_TEMPLATES.find((t) => t.id === 'brick_and_mortar');
    if (!template) return false;
    const selectedSet = new Set(selectedDocuments);
    const templateDocIds = template.documentIds;
    return templateDocIds.length > 0 && templateDocIds.every((id) => selectedSet.has(id));
  }, [selectedDocuments]);

  const handleSubmit = async () => {
    setError(null);
    if (!userIdea.trim()) {
      setError(t('project.idea.placeholder'));
      return;
    }
    if (!isBrickAndMortarTemplate && selectedDocuments.length === 0) {
      setError(t('documents.select'));
      return;
    }

    setIsSubmitting(true);
    try {
      let response;
      if (isBrickAndMortarTemplate) {
        response = await createBrickAndMortarProject({ user_idea: userIdea.trim() });
      } else {
        response = await createProject({
          user_idea: userIdea.trim(),
          selected_documents: selectedDocuments,
        });
      }
      router.push(`/project/${response.project_id}`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : t('error.createProject');
      setError(errorMessage);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center min-h-[calc(100vh-80px)] py-12 px-4 sm:px-6 lg:px-8">
      
      {/* Hero Text */}
      <div className="text-center max-w-4xl mx-auto mb-16 animate-in fade-in slide-in-from-bottom-4 duration-700">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 mb-8 backdrop-blur-md">
          <Sparkles size={14} />
          <span className="text-sm font-medium tracking-wide uppercase">AI-Powered Documentation Suite</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-6 leading-tight">
          Turn chaos into <br/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 animate-pulse">
            Structured Clarity.
          </span>
        </h1>
        
        <p className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
          OmniDoc deploys a squad of specialized AI agents to architect, write, and review your project documentation in seconds.
        </p>
      </div>

      {/* Floating Agents Preview */}
      <div className="flex gap-4 md:gap-8 mb-16 animate-float pointer-events-none">
        {[
          { role: 'architect', name: 'Atlas', title: 'Architect' },
          { role: 'writer', name: 'Lyra', title: 'Writer' },
          { role: 'critic', name: 'Vex', title: 'QA' }
        ].map((agent, idx) => (
          <GlassCard key={idx} className="flex items-center gap-3 py-3 px-5 bg-white/5 border-white/10 backdrop-blur-sm">
            <AgentAvatar role={agent.role as any} size="sm" />
            <div className="text-left">
              <div className="text-white font-bold text-xs">{agent.name}</div>
              <div className="text-gray-400 text-[10px] uppercase">{agent.title}</div>
            </div>
          </GlassCard>
        ))}
      </div>

      {/* Wizard Container */}
      <div className="w-full max-w-5xl mx-auto">
        <GlassCard className="p-1 sm:p-2 shadow-2xl shadow-indigo-900/20 border-white/10 bg-black/40">
          <div className="flex flex-col md:flex-row min-h-[500px]">
            
            {/* Wizard Sidebar (Steps) */}
            <div className="w-full md:w-64 p-6 border-b md:border-b-0 md:border-r border-white/10 bg-white/5 flex flex-col">
               <div className="space-y-6">
                 <button 
                   onClick={() => setStep(1)}
                   className={`flex items-center gap-3 w-full text-left transition-all duration-300 ${step === 1 ? 'opacity-100' : 'opacity-50 hover:opacity-80'}`}
                 >
                   <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${step === 1 ? 'border-indigo-500 text-white bg-indigo-500/20' : 'border-gray-600 text-gray-500'}`}>1</div>
                   <div className="font-medium text-white">Project Idea</div>
                 </button>
                 
                 <div className="h-8 w-0.5 bg-white/10 ml-4"></div>
                 
                 <button 
                    onClick={() => userIdea && setStep(2)}
                    disabled={!userIdea}
                    className={`flex items-center gap-3 w-full text-left transition-all duration-300 ${step === 2 ? 'opacity-100' : 'opacity-50'} ${!userIdea && 'cursor-not-allowed'}`}
                 >
                   <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${step === 2 ? 'border-indigo-500 text-white bg-indigo-500/20' : 'border-gray-600 text-gray-500'}`}>2</div>
                   <div className="font-medium text-white">Scope & Specs</div>
                 </button>
               </div>
               {/* Active Agent Preview in Sidebar */}
               <div className="mt-auto pt-8">
                  <div className="text-xs text-gray-500 uppercase tracking-wider mb-3">Active Squad</div>
                  <div className="flex -space-x-3">
                    {['architect', 'writer', 'security'].map((r, i) => (
                      <AgentAvatar key={i} role={r as any} size="sm" className="border-2 border-black rounded-full" />
                    ))}
                    <div className="w-8 h-8 rounded-full bg-gray-800 border-2 border-black flex items-center justify-center text-xs text-gray-400">+3</div>
                  </div>
               </div>
            </div>

            {/* Wizard Content Area */}
            <div className="flex-1 p-6 md:p-10">
              {step === 1 && (
                <div className="h-full flex flex-col animate-in slide-in-from-right-4 fade-in duration-300">
                  <h2 className="text-2xl font-bold text-white mb-2">What are we building?</h2>
                  <p className="text-gray-400 mb-8">Describe your project vision. Our agents will handle the structure.</p>
                  
                  <div className="flex-1">
                    <PlaceholdersAndVanishInput
                      placeholders={currentPlaceholders}
                      value={userIdea}
                      onChange={(e) => setUserIdea(e.target.value)}
                      onSubmit={(e) => { e.preventDefault(); setStep(2); }}
                      disabled={isSubmitting}
                      className="h-full min-h-[200px]"
                    />
                  </div>
                  <div className="flex justify-end mt-8">
                    <button 
                      onClick={() => setStep(2)}
                      disabled={!userIdea.trim()}
                      className="group px-6 py-3 bg-white text-black hover:bg-indigo-50 rounded-xl font-bold flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next Step <ArrowRight className="group-hover:translate-x-1 transition-transform" size={18} />
                    </button>
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="h-full flex flex-col animate-in slide-in-from-right-4 fade-in duration-300">
                  <h2 className="text-2xl font-bold text-white mb-2">Assemble Documentation</h2>
                  <p className="text-gray-400 mb-6">Choose a template or select specific documents.</p>
                  
                  <div className="space-y-6 overflow-y-auto max-h-[400px] pr-2 custom-scrollbar">
                    <TemplateSelector
                      selectedDocuments={selectedDocuments}
                      onSelectionChange={setSelectedDocuments}
                    />
                    <OptionsSelector
                      selectedDocuments={selectedDocuments}
                      onSelectionChange={setSelectedDocuments}
                      viewMode={'all'}
                      onViewModeChange={() => {}}
                      organizationMode={'category'}
                      onOrganizationModeChange={() => {}}
                    />
                  </div>
                  <div className="flex justify-between mt-8 pt-4 border-t border-white/10">
                    <button 
                      onClick={() => setStep(1)}
                      className="text-gray-400 hover:text-white px-4 font-medium transition-colors"
                    >
                      Back
                    </button>
                    <button 
                      onClick={handleSubmit}
                      disabled={isSubmitting || (!isBrickAndMortarTemplate && selectedDocuments.length === 0)}
                      className="group relative px-8 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-indigo-600/20 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden"
                    >
                      {isSubmitting ? (
                        <span className="flex items-center gap-2"><Zap className="animate-spin" size={18} /> Processing...</span>
                      ) : (
                        <>
                          <span className="relative z-10">Generate Suite</span>
                          <Sparkles className="relative z-10 group-hover:text-yellow-300 transition-colors" size={18} />
                          <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                        </>
                      )}
                    </button>
                  </div>
                  {error && (
                    <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
                      {error}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
