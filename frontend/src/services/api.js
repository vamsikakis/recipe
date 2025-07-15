import axios from 'axios';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds timeout for recipe generation
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    // Handle different types of errors
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'Server error occurred';
      return Promise.reject(new Error(message));
    } else if (error.request) {
      // Request was made but no response received
      return Promise.reject(new Error('No response from server. Please check your connection.'));
    } else {
      // Something else happened
      return Promise.reject(new Error('An unexpected error occurred.'));
    }
  }
);

/**
 * Generate a recipe based on user preferences
 * @param {Object} formData - User preferences and ingredients
 * @returns {Promise<Object>} Generated recipe data
 */
export const generateRecipe = async (formData) => {
  try {
    const response = await api.post('/api/generate-recipe', formData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Save a recipe to user's favorites
 * @param {string} recipeId - Recipe ID to save
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Save result
 */
export const saveRecipe = async (recipeId, userId) => {
  try {
    const response = await api.post('/api/save-recipe', {
      recipe_id: recipeId,
      user_id: userId
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get user's saved recipes
 * @param {string} userId - User ID
 * @returns {Promise<Array>} List of saved recipes
 */
export const getSavedRecipes = async (userId) => {
  try {
    const response = await api.get(`/api/user/${userId}/recipes`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Get a specific recipe by ID
 * @param {string} recipeId - Recipe ID
 * @returns {Promise<Object>} Recipe data
 */
export const getRecipe = async (recipeId) => {
  try {
    const response = await api.get(`/api/recipes/${recipeId}`);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Health check endpoint
 * @returns {Promise<Object>} Health status
 */
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw error;
  }
};

export default api; 