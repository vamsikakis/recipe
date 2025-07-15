from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class CuisineType(str, Enum):
    INDIAN = "Indian"
    ITALIAN = "Italian"
    ASIAN = "Asian"
    MEXICAN = "Mexican"
    MEDITERRANEAN = "Mediterranean"
    AMERICAN = "American"
    THAI = "Thai"
    CHINESE = "Chinese"
    JAPANESE = "Japanese"
    KOREAN = "Korean"

class SpiceLevel(str, Enum):
    MILD = "Mild"
    MEDIUM = "Medium"
    SPICY = "Spicy"
    EXTRA_SPICY = "Extra Spicy"

class MealType(str, Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    DINNER = "Dinner"
    SNACK = "Snack"

class CookingTime(str, Enum):
    QUICK_15 = "15 mins"
    QUICK_30 = "30 mins"
    MEDIUM_45 = "45 mins"
    LONG_60_PLUS = "60+ mins"

class DietaryRestriction(str, Enum):
    VEGETARIAN = "Vegetarian"
    VEGAN = "Vegan"
    GLUTEN_FREE = "Gluten-Free"
    DAIRY_FREE = "Dairy-Free"
    NUT_FREE = "Nut-Free"
    HALAL = "Halal"
    KOSHER = "Kosher"

class UserPreferences(BaseModel):
    cuisine: CuisineType = Field(..., description="Preferred cuisine type")
    spice_level: SpiceLevel = Field(..., description="Preferred spice level")
    meal_type: List[MealType] = Field(..., description="Preferred meal types")
    max_cooking_time: CookingTime = Field(..., description="Maximum cooking time")
    dietary_restrictions: List[DietaryRestriction] = Field(default=[], description="Dietary restrictions")
    available_ingredients: List[str] = Field(default=[], description="Available ingredients")

class RecipeGenerationRequest(BaseModel):
    preferences: UserPreferences = Field(..., description="User preferences")
    user_id: Optional[str] = Field(None, description="User ID for personalization")

class RecipeIngredient(BaseModel):
    name: str = Field(..., description="Ingredient name")
    quantity: str = Field(..., description="Quantity and unit")
    notes: Optional[str] = Field(None, description="Additional notes")

class RecipeInstruction(BaseModel):
    step_number: int = Field(..., description="Step number")
    instruction: str = Field(..., description="Cooking instruction")
    time_minutes: Optional[int] = Field(None, description="Time required for this step")

class GeneratedRecipe(BaseModel):
    id: str = Field(..., description="Unique recipe ID")
    title: str = Field(..., description="Recipe title")
    description: Optional[str] = Field(None, description="Recipe description")
    ingredients: List[RecipeIngredient] = Field(..., description="List of ingredients")
    instructions: List[RecipeInstruction] = Field(..., description="Cooking instructions")
    cooking_time: int = Field(..., description="Total cooking time in minutes")
    difficulty: str = Field(..., description="Difficulty level")
    cuisine: str = Field(..., description="Cuisine type")
    spice_level: str = Field(..., description="Spice level")
    image_url: Optional[str] = Field(None, description="Generated image URL")
    nutrition_info: Optional[Dict[str, Any]] = Field(None, description="Nutritional information")
    tags: List[str] = Field(default=[], description="Recipe tags")
    created_at: str = Field(..., description="Creation timestamp")
    user_id: Optional[str] = Field(None, description="User ID who generated this recipe")

class RecipeGenerationResponse(BaseModel):
    recipe: GeneratedRecipe = Field(..., description="Generated recipe")
    recommendations: List[GeneratedRecipe] = Field(default=[], description="Recommended recipes")
    nlp_insights: Optional[Dict[str, Any]] = Field(None, description="NLP analysis insights")

class UserProfile(BaseModel):
    user_id: str = Field(..., description="Unique user ID")
    preferences: UserPreferences = Field(..., description="User preferences")
    saved_recipes: List[str] = Field(default=[], description="List of saved recipe IDs")
    disliked_ingredients: List[str] = Field(default=[], description="Ingredients user dislikes")
    cooking_history: List[str] = Field(default=[], description="List of previously generated recipe IDs")
    created_at: str = Field(..., description="Profile creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp") 