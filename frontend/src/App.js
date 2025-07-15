import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import RecipeInputForm from './components/RecipeInputForm';
import RecipeDisplay from './components/RecipeDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import { generateRecipe } from './services/api';

function App() {
  const [recipeData, setRecipeData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerateRecipe = async (formData) => {
    setIsLoading(true);
    setError(null);
    setRecipeData(null);

    try {
      const response = await generateRecipe(formData);
      setRecipeData(response);
    } catch (err) {
      setError(err.message || 'Failed to generate recipe. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setRecipeData(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-yippee-light">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
      
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {!recipeData ? (
            <div className="space-y-8">
              <div className="text-center">
                <h1 className="text-4xl font-bold text-gradient mb-4">
                  AI-Powered Recipe Generator
                </h1>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  Create delicious Yippee! recipes tailored to your preferences, dietary needs, and available ingredients.
                </p>
              </div>
              
              <RecipeInputForm onSubmit={handleGenerateRecipe} />
              
              {isLoading && (
                <div className="text-center py-12">
                  <LoadingSpinner />
                  <p className="mt-4 text-gray-600">Generating your personalized recipe...</p>
                </div>
              )}
              
              {error && (
                <div className="card bg-red-50 border-red-200">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">Error</h3>
                      <p className="mt-1 text-sm text-red-700">{error}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-8">
              <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold text-gradient">Your Recipe</h1>
                <button
                  onClick={handleReset}
                  className="btn-outline"
                >
                  Generate New Recipe
                </button>
              </div>
              
              <RecipeDisplay recipeData={recipeData} />
            </div>
          )}
        </div>
      </main>
      
      <footer className="bg-yippee-blue text-white py-8 mt-16">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 ITC Yippee! Recipe Generator. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default App; 