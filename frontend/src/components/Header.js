import React from 'react';

const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-yippee-orange rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">Y</span>
              </div>
              <span className="text-xl font-bold text-yippee-blue">Yippee!</span>
            </div>
            <span className="text-gray-500 hidden md:block">|</span>
            <span className="text-gray-600 hidden md:block">Recipe Generator</span>
          </div>
          
          <nav className="hidden md:flex items-center space-x-6">
            <a href="#features" className="text-gray-600 hover:text-yippee-orange transition-colors">
              Features
            </a>
            <a href="#about" className="text-gray-600 hover:text-yippee-orange transition-colors">
              About
            </a>
            <a href="#contact" className="text-gray-600 hover:text-yippee-orange transition-colors">
              Contact
            </a>
          </nav>
          
          <div className="flex items-center space-x-4">
            <button className="btn-primary text-sm px-4 py-2">
              Get Started
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header; 