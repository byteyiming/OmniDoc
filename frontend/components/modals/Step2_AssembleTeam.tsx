import { AgentAvatar } from '@/components/ui/AgentAvatar';

const AGENTS = [
    { id: 'atlas', name: 'Atlas', role: 'System Architect', type: 'architect' },
    { id: 'lyra', name: 'Lyra', role: 'Technical Writer', type: 'writer' },
    { id: 'vex', name: 'Vex', role: 'Quality Assurance', type: 'critic' },
];

const Step2_AssembleTeam = ({ onNext, onBack }: { onNext: () => void; onBack: () => void }) => {
    return (
        <div>
            <p className="text-gray-400 mb-6">Select the specialists needed for this documentation.</p>
            <div className="space-y-3">
                {AGENTS.map(agent => (
                    <label key={agent.id} className="flex items-center space-x-4 p-4 bg-background rounded-lg border-2 border-border hover:border-primary transition-colors cursor-pointer">
                        <input type="radio" name="agent" className="form-radio h-5 w-5 text-primary bg-background border-border focus:ring-primary" />
                        <AgentAvatar role={agent.type as any} size="md" />
                        <div>
                            <p className="font-semibold text-white">{agent.name}</p>
                            <p className="text-sm text-gray-400">{agent.role}</p>
                        </div>
                    </label>
                ))}
            </div>
            <div className="flex justify-between mt-6">
                <button onClick={onBack} className="text-gray-400 hover:text-white font-semibold px-6 py-2.5 rounded-lg transition-colors">
                    Back
                </button>
                <button onClick={onNext} className="bg-primary hover:bg-primary-hover text-white font-semibold px-6 py-2.5 rounded-lg transition-colors">
                    Next Step
                </button>
            </div>
        </div>
    );
};

export default Step2_AssembleTeam;
