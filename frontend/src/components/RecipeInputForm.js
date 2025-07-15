import React, { useState } from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { ChefHat, Clock, Utensils, Heart } from 'lucide-react';

const cuisineOptions = [
  { value: 'Indian', label: 'Indian' },
  { value: 'Italian', label: 'Italian' },
  { value: 'Asian', label: 'Asian' },
  { value: 'Mexican', label: 'Mexican' },
  { value: 'Mediterranean', label: 'Mediterranean' },
  { value: 'American', label: 'American' },
  { value: 'Thai', label: 'Thai' },
  { value: 'Chinese', label: 'Chinese' },
  { value: 'Japanese', label: 'Japanese' },
  { value: 'Korean', label: 'Korean' }
];

const spiceLevelOptions = [
  { value: 'Mild', label: 'Mild' },
  { value: 'Medium', label: 'Medium' },
  { value: 'Spicy', label: 'Spicy' },
  { value: 'Extra Spicy', label: 'Extra Spicy' }
];

const mealTypeOptions = [
  { value: 'Breakfast', label: 'Breakfast' },
  { value: 'Lunch', label: 'Lunch' },
  { value: 'Dinner', label: 'Dinner' },
  { value: 'Snack', label: 'Snack' }
];

const cookingTimeOptions = [
  { value: '15 mins', label: '15 minutes' },
  { value: '30 mins', label: '30 minutes' },
  { value: '45 mins', label: '45 minutes' },
  { value: '60+ mins', label: '60+ minutes' }
];

const dietaryRestrictionOptions = [
  { value: 'Vegetarian', label: 'Vegetarian' },
  { value: 'Vegan', label: 'Vegan' },
  { value: 'Gluten-Free', label: 'Gluten-Free' },
  { value: 'Dairy-Free', label: 'Dairy-Free' },
  { value: 'Nut-Free', label: 'Nut-Free' },
  { value: 'Halal', label: 'Halal' },
  { value: 'Kosher', label: 'Kosher' }
];

const validationSchema = Yup.object({
  cuisine: Yup.string().required('Please select a cuisine preference'),
  spiceLevel: Yup.string().required('Please select a spice level'),
  mealType: Yup.array().min(1, 'Please select at least one meal type').required('Please select meal types'),
  maxCookingTime: Yup.string().required('Please select maximum cooking time'),
  dietaryRestrictions: Yup.array(),
  availableIngredients: Yup.string().required('Please enter your available ingredients')
});

const RecipeInputForm = ({ onSubmit }) => {
  const [ingredientInput, setIngredientInput] = useState('');
  const [ingredients, setIngredients] = useState([]);

  const formik = useFormik({
    initialValues: {
      cuisine: '',
      spiceLevel: '',
      mealType: [],
      maxCookingTime: '',
      dietaryRestrictions: [],
      availableIngredients: ''
    },
    validationSchema,
    onSubmit: (values) => {
      const formData = {
        preferences: {
          cuisine: values.cuisine,
          spiceLevel: values.spiceLevel,
          mealType: values.mealType,
          maxCookingTime: values.maxCookingTime,
          dietaryRestrictions: values.dietaryRestrictions,
          availableIngredients: ingredients
        }
      };
      onSubmit(formData);
    }
  });

  const addIngredient = () => {
    if (ingredientInput.trim() && !ingredients.includes(ingredientInput.trim())) {
      setIngredients([...ingredients, ingredientInput.trim()]);
      setIngredientInput('');
    }
  };

  const removeIngredient = (index) => {
    setIngredients(ingredients.filter((_, i) => i !== index));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addIngredient();
    }
  };

  return (
    <div className="card max-w-2xl mx-auto">
      <form onSubmit={formik.handleSubmit} className="space-y-6">
        {/* Cuisine Preference */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <ChefHat className="inline w-4 h-4 mr-2" />
            Cuisine Preference
          </label>
          <select
            name="cuisine"
            value={formik.values.cuisine}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            className="select-field"
          >
            <option value="">Select cuisine</option>
            {cuisineOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {formik.touched.cuisine && formik.errors.cuisine && (
            <p className="mt-1 text-sm text-red-600">{formik.errors.cuisine}</p>
          )}
        </div>

        {/* Spice Level */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Utensils className="inline w-4 h-4 mr-2" />
            Spice Level
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {spiceLevelOptions.map(option => (
              <label key={option.value} className="flex items-center">
                <input
                  type="radio"
                  name="spiceLevel"
                  value={option.value}
                  checked={formik.values.spiceLevel === option.value}
                  onChange={formik.handleChange}
                  className="mr-2 text-yippee-orange focus:ring-yippee-orange"
                />
                <span className="text-sm">{option.label}</span>
              </label>
            ))}
          </div>
          {formik.touched.spiceLevel && formik.errors.spiceLevel && (
            <p className="mt-1 text-sm text-red-600">{formik.errors.spiceLevel}</p>
          )}
        </div>

        {/* Meal Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Clock className="inline w-4 h-4 mr-2" />
            Meal Type
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {mealTypeOptions.map(option => (
              <label key={option.value} className="flex items-center">
                <input
                  type="checkbox"
                  name="mealType"
                  value={option.value}
                  checked={formik.values.mealType.includes(option.value)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      formik.setFieldValue('mealType', [...formik.values.mealType, option.value]);
                    } else {
                      formik.setFieldValue('mealType', formik.values.mealType.filter(type => type !== option.value));
                    }
                  }}
                  className="mr-2 text-yippee-orange focus:ring-yippee-orange"
                />
                <span className="text-sm">{option.label}</span>
              </label>
            ))}
          </div>
          {formik.touched.mealType && formik.errors.mealType && (
            <p className="mt-1 text-sm text-red-600">{formik.errors.mealType}</p>
          )}
        </div>

        {/* Cooking Time */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Clock className="inline w-4 h-4 mr-2" />
            Maximum Cooking Time
          </label>
          <select
            name="maxCookingTime"
            value={formik.values.maxCookingTime}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            className="select-field"
          >
            <option value="">Select cooking time</option>
            {cookingTimeOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {formik.touched.maxCookingTime && formik.errors.maxCookingTime && (
            <p className="mt-1 text-sm text-red-600">{formik.errors.maxCookingTime}</p>
          )}
        </div>

        {/* Dietary Restrictions */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <Heart className="inline w-4 h-4 mr-2" />
            Dietary Restrictions (Optional)
          </label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {dietaryRestrictionOptions.map(option => (
              <label key={option.value} className="flex items-center">
                <input
                  type="checkbox"
                  name="dietaryRestrictions"
                  value={option.value}
                  checked={formik.values.dietaryRestrictions.includes(option.value)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      formik.setFieldValue('dietaryRestrictions', [...formik.values.dietaryRestrictions, option.value]);
                    } else {
                      formik.setFieldValue('dietaryRestrictions', formik.values.dietaryRestrictions.filter(restriction => restriction !== option.value));
                    }
                  }}
                  className="mr-2 text-yippee-orange focus:ring-yippee-orange"
                />
                <span className="text-sm">{option.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Available Ingredients */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Available Ingredients
          </label>
          <div className="space-y-3">
            <div className="flex space-x-2">
              <input
                type="text"
                value={ingredientInput}
                onChange={(e) => setIngredientInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter an ingredient and press Enter"
                className="input-field flex-1"
              />
              <button
                type="button"
                onClick={addIngredient}
                className="btn-secondary px-4"
              >
                Add
              </button>
            </div>
            
            {ingredients.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {ingredients.map((ingredient, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-yippee-orange text-white"
                  >
                    {ingredient}
                    <button
                      type="button"
                      onClick={() => removeIngredient(index)}
                      className="ml-2 text-white hover:text-gray-200"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-4">
          <button
            type="submit"
            disabled={formik.isSubmitting}
            className="btn-primary w-full text-lg py-4"
          >
            {formik.isSubmitting ? 'Generating Recipe...' : 'Generate Recipe'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default RecipeInputForm; 