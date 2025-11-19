import { Sparkles } from 'lucide-react';

const Step3_ReviewLaunch = ({ onBack }: { onBack: () => void }) => {
  return (
    <div>
      <p className="text-gray-400 mb-6">Ready to generate the suite? This will cost 12 Credits.</p>
      <div className="bg-background p-6 rounded-lg border border-border">
          <h4 className="flex items-center font-semibold text-white mb-3">
            <Sparkles size={18} className="text-accent-yellow mr-2" />
            Estimated Output
          </h4>
          <ul className="list-disc list-inside text-gray-400 space-y-2">
              <li>System Architecture Diagram (Mermaid.js)</li>
              <li>API Reference (OpenAPI 3.0)</li>
              <li>User Onboarding Guide</li>
              <li>Security Audit Report</li>
          </ul>
      </div>
      <div className="flex justify-between mt-6">
        <button onClick={onBack} className="text-gray-400 hover:text-white font-semibold px-6 py-2.5 rounded-lg transition-colors">
          Back
        </button>
        <button className="flex items-center space-x-2 bg-white hover:bg-gray-200 text-background font-bold px-6 py-2.5 rounded-lg transition-colors">
          <Sparkles size={18} />
          <span>Generate Suite</span>
        </button>
      </div>
    </div>
  );
};

export default Step3_ReviewLaunch;
