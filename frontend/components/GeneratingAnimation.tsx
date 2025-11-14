'use client';

export default function GeneratingAnimation() {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative mb-6">
        {/* Pulsing circles - more dynamic */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-20 w-20 animate-ping rounded-full bg-blue-400 opacity-20"></div>
        </div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-16 w-16 animate-ping rounded-full bg-purple-400 opacity-30" style={{ animationDelay: '0.2s' }}></div>
        </div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-12 w-12 animate-ping rounded-full bg-green-400 opacity-40" style={{ animationDelay: '0.4s' }}></div>
        </div>
        <div className="relative flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-blue-100 via-purple-100 to-green-100 shadow-lg">
          <div className="text-5xl animate-pulse">🤖</div>
        </div>
      </div>
      
      {/* Animated dots with text */}
      <div className="flex flex-col items-center space-y-3">
        <div className="flex space-x-2">
          <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500" style={{ animationDelay: '0s' }}></div>
          <div className="h-2 w-2 animate-bounce rounded-full bg-purple-500" style={{ animationDelay: '0.2s' }}></div>
          <div className="h-2 w-2 animate-bounce rounded-full bg-green-500" style={{ animationDelay: '0.4s' }}></div>
        </div>
        <p className="text-sm font-medium text-gray-600 animate-pulse">
          Customized agents are working...
        </p>
      </div>
      
      {/* Data nodes animation */}
      <div className="mt-8 flex items-center space-x-4">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-3 w-3 rounded-full bg-gradient-to-r from-blue-400 to-purple-400 opacity-60"
            style={{
              animation: `pulse 1.5s ease-in-out infinite`,
              animationDelay: `${i * 0.2}s`,
            }}
          />
        ))}
      </div>
    </div>
  );
}

