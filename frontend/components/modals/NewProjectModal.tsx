'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import Step1_ProjectIdea from './Step1_ProjectIdea';
import Step2_AssembleTeam from './Step2_AssembleTeam';
import Step3_ReviewLaunch from './Step3_ReviewLaunch';

const NewProjectModal = ({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }) => {
  const [step, setStep] = useState(1);

  const STEPS = [
    { number: 1, title: "What are we building?" },
    { number: 2, title: "Assemble Your Team" },
    { number: 3, title: "Review & Launch" },
  ];

  const CurrentStepComponent = () => {
    switch (step) {
      case 1:
        return <Step1_ProjectIdea onNext={() => setStep(2)} />;
      case 2:
        return <Step2_AssembleTeam onNext={() => setStep(3)} onBack={() => setStep(1)} />;
      case 3:
        return <Step3_ReviewLaunch onBack={() => setStep(2)} />;
      default:
        return <Step1_ProjectIdea onNext={() => setStep(2)} />;
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-card border-border p-0 max-w-2xl">
        <div className="p-8">
          {/* Progress Bar */}
          <div className="flex items-center space-x-2 mb-6">
            {STEPS.map((s) => (
              <div key={s.number} className="flex-1 h-1 rounded-full bg-border">
                <div
                  className={`h-1 rounded-full transition-all duration-300 ${step >= s.number ? 'bg-primary' : ''}`}
                />
              </div>
            ))}
          </div>
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-white">{STEPS[step - 1].title}</DialogTitle>
          </DialogHeader>
          <div className="mt-4">
            <CurrentStepComponent />
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default NewProjectModal;
