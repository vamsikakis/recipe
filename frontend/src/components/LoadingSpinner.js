import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="flex flex-col items-center justify-center">
      <div className="loading-spinner"></div>
      <div className="mt-4 text-center">
        <div className="flex space-x-1 justify-center">
          <div className="w-2 h-2 bg-yippee-orange rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-yippee-orange rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-yippee-orange rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>
    </div>
  );
};

export default LoadingSpinner; 