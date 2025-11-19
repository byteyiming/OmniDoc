const Step1_ProjectIdea = ({ onNext }: { onNext: () => void }) => {
  return (
    <div>
      <p className="text-gray-400 mb-6">Describe your project. Our agents will handle the structure.</p>
      <textarea
        className="w-full h-40 bg-background border-2 border-border rounded-lg p-4 focus:border-primary focus:outline-none transition-colors"
        placeholder="e.g. A decentralized voting platform using Ethereum smart contracts..."
      />
      <div className="flex justify-end mt-6">
        <button onClick={onNext} className="bg-primary hover:bg-primary-hover text-white font-semibold px-6 py-2.5 rounded-lg transition-colors">
          Next Step
        </button>
      </div>
    </div>
  );
};

export default Step1_ProjectIdea;
