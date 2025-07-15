import logging
from typing import List, Dict, Any, Optional
from models.recipe import UserPreferences, GeneratedRecipe

logger = logging.getLogger(__name__)

async def get_recommended_recipes(
    user_preferences: UserPreferences,
    dietary_restrictions: List[str],
    available_ingredients: List[str],
    user_profile: Optional[Dict[str, Any]],
    all_base_recipes: List[Dict[str, Any]]
) -> List[GeneratedRecipe]:
    """
    Get recipe recommendations based on user preferences and available ingredients.
    """
    try:
        logger.info("Generating recipe recommendations")
        
        # Score each base recipe
        scored_recipes = []
        
        for recipe in all_base_recipes:
            score = calculate_recipe_score(
                recipe=recipe,
                user_preferences=user_preferences,
                dietary_restrictions=dietary_restrictions,
                available_ingredients=available_ingredients,
                user_profile=user_profile
            )
            
            if score > 0:  # Only include recipes with positive scores
                scored_recipes.append((recipe, score))
        
        # Sort by score (highest first) and take top 3-5
        scored_recipes.sort(key=lambda x: x[1], reverse=True)
        top_recipes = scored_recipes[:5]
        
        # Convert to GeneratedRecipe objects
        recommendations = []
        for recipe, score in top_recipes:
            try:
                generated_recipe = convert_to_generated_recipe(recipe)
                recommendations.append(generated_recipe)
            except Exception as e:
                logger.warning(f"Failed to convert recipe {recipe.get('id')}: {e}")
                continue
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return []

def calculate_recipe_score(
    recipe: Dict[str, Any],
    user_preferences: UserPreferences,
    dietary_restrictions: List[str],
    available_ingredients: List[str],
    user_profile: Optional[Dict[str, Any]]
) -> float:
    """
    Calculate a score for a recipe based on various factors.
    """
    score = 0.0
    
    try:
        # 1. Cuisine preference match (weight: 0.3)
        recipe_cuisine = recipe.get('cuisine', '').lower()
        user_cuisine = user_preferences.cuisine.value.lower()
        if recipe_cuisine == user_cuisine:
            score += 0.3
        elif recipe_cuisine in user_cuisine or user_cuisine in recipe_cuisine:
            score += 0.15
        
        # 2. Meal type preference match (weight: 0.2)
        recipe_tags = [tag.lower() for tag in recipe.get('tags', [])]
        user_meal_types = [mt.value.lower() for mt in user_preferences.meal_type]
        
        for meal_type in user_meal_types:
            if meal_type in recipe_tags or any(meal_type in tag for tag in recipe_tags):
                score += 0.1
                break
        
        # 3. Cooking time preference match (weight: 0.15)
        recipe_cooking_time = recipe.get('cooking_time', 30)
        user_max_time = parse_cooking_time(user_preferences.max_cooking_time.value)
        
        if recipe_cooking_time <= user_max_time:
            score += 0.15
        elif recipe_cooking_time <= user_max_time + 15:  # Allow 15 min buffer
            score += 0.075
        
        # 4. Ingredient availability match (weight: 0.25)
        recipe_ingredients = [ing.lower() for ing in recipe.get('ingredients', [])]
        available_ingredients_lower = [ing.lower() for ing in available_ingredients]
        
        matching_ingredients = 0
        for recipe_ing in recipe_ingredients:
            for avail_ing in available_ingredients_lower:
                if recipe_ing in avail_ing or avail_ing in recipe_ing:
                    matching_ingredients += 1
                    break
        
        if recipe_ingredients:
            ingredient_match_ratio = matching_ingredients / len(recipe_ingredients)
            score += 0.25 * ingredient_match_ratio
        
        # 5. Dietary restrictions compliance (weight: 0.2)
        if not violates_dietary_restrictions(recipe, dietary_restrictions):
            score += 0.2
        else:
            return 0.0  # Disqualify if violates dietary restrictions
        
        # 6. User profile preferences (weight: 0.1)
        if user_profile:
            # Check if user has liked similar recipes
            saved_recipes = user_profile.get('saved_recipes', [])
            disliked_ingredients = [ing.lower() for ing in user_profile.get('disliked_ingredients', [])]
            
            # Check for disliked ingredients
            for recipe_ing in recipe_ingredients:
                for disliked_ing in disliked_ingredients:
                    if recipe_ing in disliked_ing or disliked_ing in recipe_ing:
                        return 0.0  # Disqualify if contains disliked ingredients
            
            # Bonus for recipes similar to saved ones
            if recipe.get('id') in saved_recipes:
                score += 0.1
        
        # 7. Spice level preference (weight: 0.1)
        recipe_spice_level = extract_spice_level(recipe)
        user_spice_level = user_preferences.spice_level.value.lower()
        
        if recipe_spice_level == user_spice_level:
            score += 0.1
        elif spice_levels_compatible(recipe_spice_level, user_spice_level):
            score += 0.05
        
        # 8. Difficulty level bonus (weight: 0.05)
        difficulty = recipe.get('difficulty', 'Medium').lower()
        if difficulty == 'easy':
            score += 0.05
        
        return score
        
    except Exception as e:
        logger.error(f"Error calculating recipe score: {e}")
        return 0.0

def parse_cooking_time(time_str: str) -> int:
    """Parse cooking time string to minutes"""
    try:
        if '15' in time_str:
            return 15
        elif '30' in time_str:
            return 30
        elif '45' in time_str:
            return 45
        elif '60' in time_str:
            return 60
        else:
            return 30  # Default
    except:
        return 30

def violates_dietary_restrictions(recipe: Dict[str, Any], dietary_restrictions: List[str]) -> bool:
    """Check if recipe violates any dietary restrictions"""
    if not dietary_restrictions:
        return False
    
    recipe_ingredients = [ing.lower() for ing in recipe.get('ingredients', [])]
    recipe_tags = [tag.lower() for tag in recipe.get('tags', [])]
    
    for restriction in dietary_restrictions:
        restriction_lower = restriction.lower()
        
        if restriction_lower == 'vegetarian':
            non_veg_ingredients = ['chicken', 'beef', 'pork', 'lamb', 'fish', 'meat', 'egg']
            if any(ing in recipe_ingredients for ing in non_veg_ingredients):
                return True
        
        elif restriction_lower == 'vegan':
            non_vegan_ingredients = ['milk', 'cheese', 'butter', 'cream', 'yogurt', 'egg', 'honey']
            if any(ing in recipe_ingredients for ing in non_vegan_ingredients):
                return True
        
        elif restriction_lower == 'gluten-free':
            gluten_ingredients = ['wheat', 'flour', 'bread', 'pasta']
            if any(ing in recipe_ingredients for ing in gluten_ingredients):
                return True
        
        elif restriction_lower == 'dairy-free':
            dairy_ingredients = ['milk', 'cheese', 'butter', 'cream', 'yogurt']
            if any(ing in recipe_ingredients for ing in dairy_ingredients):
                return True
        
        elif restriction_lower == 'nut-free':
            nut_ingredients = ['peanut', 'almond', 'cashew', 'walnut', 'pistachio']
            if any(ing in recipe_ingredients for ing in nut_ingredients):
                return True
    
    return False

def extract_spice_level(recipe: Dict[str, Any]) -> str:
    """Extract spice level from recipe"""
    recipe_tags = [tag.lower() for tag in recipe.get('tags', [])]
    title = recipe.get('title', '').lower()
    
    if 'spicy' in title or 'spicy' in recipe_tags:
        return 'spicy'
    elif 'mild' in title or 'mild' in recipe_tags:
        return 'mild'
    elif 'medium' in title or 'medium' in recipe_tags:
        return 'medium'
    else:
        return 'medium'  # Default

def spice_levels_compatible(recipe_spice: str, user_spice: str) -> bool:
    """Check if spice levels are compatible"""
    spice_hierarchy = ['mild', 'medium', 'spicy', 'extra spicy']
    
    try:
        recipe_index = spice_hierarchy.index(recipe_spice)
        user_index = spice_hierarchy.index(user_spice)
        
        # Allow one level difference
        return abs(recipe_index - user_index) <= 1
    except ValueError:
        return True  # If spice level not found, assume compatible

def convert_to_generated_recipe(recipe: Dict[str, Any]) -> GeneratedRecipe:
    """Convert base recipe to GeneratedRecipe format"""
    from models.recipe import RecipeIngredient, RecipeInstruction
    
    # Create basic ingredients list
    ingredients = []
    for ing in recipe.get('ingredients', []):
        ingredients.append(RecipeIngredient(
            name=ing,
            quantity="as needed",
            notes=None
        ))
    
    # Create basic instructions
    instructions = [
        RecipeInstruction(
            step_number=1,
            instruction=f"Prepare {recipe.get('title', 'recipe')} according to your preference",
            time_minutes=recipe.get('cooking_time', 30)
        )
    ]
    
    return GeneratedRecipe(
        id=recipe.get('id', ''),
        title=recipe.get('title', 'Yippee Recipe'),
        description=f"A delicious {recipe.get('cuisine', 'fusion')} recipe",
        ingredients=ingredients,
        instructions=instructions,
        cooking_time=recipe.get('cooking_time', 30),
        difficulty=recipe.get('difficulty', 'Medium'),
        cuisine=recipe.get('cuisine', 'Fusion'),
        spice_level='Medium',
        image_url=None,
        tags=recipe.get('tags', []),
        created_at="",
        user_id=None
    ) 