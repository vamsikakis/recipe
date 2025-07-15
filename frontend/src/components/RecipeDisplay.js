import React, { useState } from 'react';
import { Clock, Users, Star, Heart, Share2, Bookmark } from 'lucide-react';

const RecipeDisplay = ({ recipeData }) => {
  const [isSaved, setIsSaved] = useState(false);
  const [showRecommendations, setShowRecommendations] = useState(false);

  const handleSaveRecipe = () => {
    setIsSaved(!isSaved);
    // TODO: Implement save functionality with backend
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: recipeData.recipe.title,
        text: `Check out this delicious recipe: ${recipeData.recipe.title}`,
        url: window.location.href
      });
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
    }
  };

  const formatTime = (minutes) => {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  return (
    <div className="space-y-8">
      {/* Main Recipe Card */}
      <div className="card">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Recipe Image */}
          <div className="space-y-4">
            {recipeData.recipe.imageUrl ? (
              <img
                src={recipeData.recipe.imageUrl}
                alt={recipeData.recipe.title}
                className="w-full h-64 md:h-80 object-cover rounded-lg shadow-lg"
              />
            ) : (
              <div className="w-full h-64 md:h-80 bg-gray-200 rounded-lg flex items-center justify-center">
                <span className="text-gray-500">Recipe Image</span>
              </div>
            )}
            
            {/* Recipe Stats */}
            <div className="flex items-center justify-between text-sm text-gray-600">
              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  <span>{formatTime(recipeData.recipe.cooking_time)}</span>
                </div>
                <div className="flex items-center">
                  <Users className="w-4 h-4 mr-1" />
                  <span>{recipeData.recipe.difficulty}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleSaveRecipe}
                  className={`p-2 rounded-full transition-colors ${
                    isSaved ? 'text-red-500 bg-red-50' : 'text-gray-400 hover:text-red-500 hover:bg-red-50'
                  }`}
                >
                  <Heart className="w-5 h-5" fill={isSaved ? 'currentColor' : 'none'} />
                </button>
                <button
                  onClick={handleShare}
                  className="p-2 rounded-full text-gray-400 hover:text-yippee-orange hover:bg-orange-50 transition-colors"
                >
                  <Share2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>

          {/* Recipe Details */}
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {recipeData.recipe.title}
              </h1>
              {recipeData.recipe.description && (
                <p className="text-gray-600 mb-4">{recipeData.recipe.description}</p>
              )}
              
              {/* Recipe Tags */}
              <div className="flex flex-wrap gap-2 mb-4">
                {recipeData.recipe.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-yippee-orange text-white text-sm rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Recipe Info */}
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-yippee-orange">{recipeData.recipe.cuisine}</div>
                <div className="text-sm text-gray-600">Cuisine</div>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-yippee-orange">{recipeData.recipe.spice_level}</div>
                <div className="text-sm text-gray-600">Spice Level</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Ingredients and Instructions */}
      <div className="grid md:grid-cols-2 gap-8">
        {/* Ingredients */}
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Ingredients</h2>
          <ul className="space-y-3">
            {recipeData.recipe.ingredients.map((ingredient, index) => (
              <li key={index} className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-yippee-orange rounded-full mt-2 flex-shrink-0"></div>
                <div>
                  <span className="font-medium">{ingredient.name}</span>
                  <span className="text-gray-600 ml-2">- {ingredient.quantity}</span>
                  {ingredient.notes && (
                    <p className="text-sm text-gray-500 mt-1">{ingredient.notes}</p>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>

        {/* Instructions */}
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Instructions</h2>
          <ol className="space-y-4">
            {recipeData.recipe.instructions.map((instruction, index) => (
              <li key={index} className="flex space-x-4">
                <div className="flex-shrink-0 w-8 h-8 bg-yippee-orange text-white rounded-full flex items-center justify-center font-bold text-sm">
                  {instruction.step_number}
                </div>
                <div className="flex-1">
                  <p className="text-gray-900">{instruction.instruction}</p>
                  {instruction.time_minutes && (
                    <p className="text-sm text-gray-500 mt-1">
                      Time: {instruction.time_minutes} minutes
                    </p>
                  )}
                </div>
              </li>
            ))}
          </ol>
        </div>
      </div>

      {/* Recommendations */}
      {recipeData.recommendations && recipeData.recommendations.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Recommended Recipes</h2>
            <button
              onClick={() => setShowRecommendations(!showRecommendations)}
              className="text-yippee-orange hover:text-orange-600 font-medium"
            >
              {showRecommendations ? 'Hide' : 'Show'} Recommendations
            </button>
          </div>
          
          {showRecommendations && (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recipeData.recommendations.map((recipe, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <h3 className="font-semibold text-gray-900 mb-2">{recipe.title}</h3>
                  <p className="text-sm text-gray-600 mb-3">{recipe.description}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{recipe.cuisine}</span>
                    <span>{formatTime(recipe.cooking_time)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* NLP Insights (if available) */}
      {recipeData.nlp_insights && (
        <div className="card bg-blue-50 border-blue-200">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">AI Analysis</h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div>
              <h4 className="font-medium text-blue-800 mb-2">Recognized Ingredients</h4>
              <div className="space-y-1">
                {recipeData.nlp_insights.entities?.map((entity, index) => (
                  <div key={index} className="text-blue-700">
                    {entity.text} ({entity.category})
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-medium text-blue-800 mb-2">Key Phrases</h4>
              <div className="space-y-1">
                {recipeData.nlp_insights.key_phrases?.map((phrase, index) => (
                  <div key={index} className="text-blue-700">{phrase}</div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-medium text-blue-800 mb-2">Sentiment</h4>
              <div className="text-blue-700 capitalize">
                {recipeData.nlp_insights.sentiment}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecipeDisplay; 