from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
import uuid
from datetime import datetime
from typing import Optional

from models.recipe import (
    RecipeGenerationRequest, 
    RecipeGenerationResponse, 
    GeneratedRecipe,
    RecipeIngredient,
    RecipeInstruction
)
from services.database import store_generated_recipe, get_base_recipes
from services.user_profile import get_user_profile, update_user_profile
from services.ai_integrations import (
    call_azure_ai_language,
    call_azure_openai_generative_ai,
    call_azure_openai_dalle
)
from services.recommendation import get_recommended_recipes

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate-recipe", response_model=RecipeGenerationResponse)
async def generate_recipe(request: RecipeGenerationRequest):
    """
    Generate a personalized recipe based on user preferences and available ingredients.
    """
    try:
        logger.info(f"Received recipe generation request for user: {request.user_id}")
        
        # Step 1: Get user profile for personalization
        user_profile = None
        if request.user_id:
            user_profile = await get_user_profile(request.user_id)
            logger.info(f"Retrieved user profile for user: {request.user_id}")
        
        # Step 2: Process user input with NLP
        user_input_text = f"""
        Cuisine: {request.preferences.cuisine}
        Spice Level: {request.preferences.spice_level}
        Meal Types: {', '.join(request.preferences.meal_type)}
        Cooking Time: {request.preferences.max_cooking_time}
        Dietary Restrictions: {', '.join(request.preferences.dietary_restrictions)}
        Available Ingredients: {', '.join(request.preferences.available_ingredients)}
        """
        
        nlp_insights = await call_azure_ai_language(user_input_text)
        logger.info("NLP processing completed")
        
        # Step 3: Get base recipes for recommendations
        base_recipes = await get_base_recipes()
        
        # Step 4: Get recipe recommendations
        recommendations = await get_recommended_recipes(
            user_preferences=request.preferences,
            dietary_restrictions=request.preferences.dietary_restrictions,
            available_ingredients=request.preferences.available_ingredients,
            user_profile=user_profile,
            all_base_recipes=base_recipes
        )
        logger.info(f"Generated {len(recommendations)} recommendations")
        
        # Step 5: Generate recipe with AI
        recipe_prompt = construct_recipe_prompt(request.preferences, nlp_insights, user_profile)
        generated_recipe_text = await call_azure_openai_generative_ai(recipe_prompt)
        
        # Step 6: Parse the generated recipe
        parsed_recipe = parse_generated_recipe(generated_recipe_text)
        
        # Step 7: Generate recipe image
        image_prompt = f"Delicious {parsed_recipe['title']} with Yippee noodles, professional food photography, appetizing presentation"
        image_url = await call_azure_openai_dalle(image_prompt)
        
        # Step 8: Create final recipe object
        recipe_id = str(uuid.uuid4())
        final_recipe = GeneratedRecipe(
            id=recipe_id,
            title=parsed_recipe['title'],
            description=parsed_recipe.get('description'),
            ingredients=parsed_recipe['ingredients'],
            instructions=parsed_recipe['instructions'],
            cooking_time=parsed_recipe['cooking_time'],
            difficulty=parsed_recipe.get('difficulty', 'Medium'),
            cuisine=request.preferences.cuisine.value,
            spice_level=request.preferences.spice_level.value,
            image_url=image_url,
            tags=parsed_recipe.get('tags', []),
            created_at=datetime.utcnow().isoformat(),
            user_id=request.user_id
        )
        
        # Step 9: Store the generated recipe
        await store_generated_recipe(final_recipe.dict())
        
        # Step 10: Update user profile with new recipe
        if request.user_id:
            await update_user_profile(request.user_id, {
                'cooking_history': [recipe_id],
                'preferences': request.preferences.dict()
            })
        
        logger.info(f"Successfully generated recipe: {recipe_id}")
        
        return RecipeGenerationResponse(
            recipe=final_recipe,
            recommendations=recommendations,
            nlp_insights=nlp_insights
        )
        
    except Exception as e:
        logger.error(f"Error generating recipe: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recipe: {str(e)}")

def construct_recipe_prompt(preferences, nlp_insights, user_profile):
    """
    Construct a detailed prompt for the generative AI based on user preferences and NLP insights.
    """
    prompt = f"""
    You are a creative chef specializing in Yippee! noodles and pasta recipes. Generate a unique, delicious recipe based on the following requirements:

    CUISINE: {preferences.cuisine.value}
    SPICE LEVEL: {preferences.spice_level.value}
    MEAL TYPE: {', '.join([mt.value for mt in preferences.meal_type])}
    MAX COOKING TIME: {preferences.max_cooking_time.value}
    DIETARY RESTRICTIONS: {', '.join([dr.value for dr in preferences.dietary_restrictions]) if preferences.dietary_restrictions else 'None'}
    
    AVAILABLE INGREDIENTS: {', '.join(preferences.available_ingredients)}
    
    NLP INSIGHTS:
    - Recognized entities: {nlp_insights.get('entities', [])}
    - Key phrases: {nlp_insights.get('key_phrases', [])}
    - Sentiment: {nlp_insights.get('sentiment', 'neutral')}
    
    USER PROFILE: {user_profile.dict() if user_profile else 'New user'}
    
    REQUIREMENTS:
    1. The recipe MUST use Yippee! noodles or pasta as the main ingredient
    2. Be creative and innovative while staying within the Yippee! brand essence
    3. Ensure the recipe is practical and achievable
    4. Include precise measurements and clear instructions
    5. Consider the user's spice preference and dietary restrictions
    6. Make use of the available ingredients when possible
    
    OUTPUT FORMAT:
    Title: [Recipe Title]
    Description: [Brief description]
    Cooking Time: [Total minutes]
    Difficulty: [Easy/Medium/Hard]
    Tags: [comma-separated tags]
    
    Ingredients:
    - [Ingredient name]: [Quantity and unit] [Optional notes]
    
    Instructions:
    1. [Step 1 instruction] (Time: X minutes)
    2. [Step 2 instruction] (Time: X minutes)
    ...
    
    Please generate a complete recipe following this exact format.
    """
    
    return prompt

def parse_generated_recipe(recipe_text: str) -> dict:
    """
    Parse the generated recipe text into structured data.
    """
    lines = recipe_text.strip().split('\n')
    recipe_data = {
        'title': '',
        'description': '',
        'cooking_time': 30,
        'difficulty': 'Medium',
        'tags': [],
        'ingredients': [],
        'instructions': []
    }
    
    current_section = None
    step_number = 1
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('Title:'):
            recipe_data['title'] = line.replace('Title:', '').strip()
        elif line.startswith('Description:'):
            recipe_data['description'] = line.replace('Description:', '').strip()
        elif line.startswith('Cooking Time:'):
            time_str = line.replace('Cooking Time:', '').strip()
            try:
                recipe_data['cooking_time'] = int(time_str.split()[0])
            except:
                recipe_data['cooking_time'] = 30
        elif line.startswith('Difficulty:'):
            recipe_data['difficulty'] = line.replace('Difficulty:', '').strip()
        elif line.startswith('Tags:'):
            tags_str = line.replace('Tags:', '').strip()
            recipe_data['tags'] = [tag.strip() for tag in tags_str.split(',')]
        elif line.startswith('Ingredients:'):
            current_section = 'ingredients'
        elif line.startswith('Instructions:'):
            current_section = 'instructions'
        elif current_section == 'ingredients' and line.startswith('-'):
            ingredient_line = line[1:].strip()
            if ':' in ingredient_line:
                name, rest = ingredient_line.split(':', 1)
                quantity_notes = rest.strip().split(' ', 1)
                quantity = quantity_notes[0]
                notes = quantity_notes[1] if len(quantity_notes) > 1 else None
                
                recipe_data['ingredients'].append(RecipeIngredient(
                    name=name.strip(),
                    quantity=quantity.strip(),
                    notes=notes
                ))
        elif current_section == 'instructions' and line[0].isdigit():
            instruction_text = line.split('.', 1)[1] if '.' in line else line
            time_match = None
            if '(Time:' in instruction_text:
                instruction_text, time_part = instruction_text.split('(Time:', 1)
                time_str = time_part.split(')')[0].strip()
                try:
                    time_match = int(time_str.split()[0])
                except:
                    pass
            
            recipe_data['instructions'].append(RecipeInstruction(
                step_number=step_number,
                instruction=instruction_text.strip(),
                time_minutes=time_match
            ))
            step_number += 1
    
    # Ensure we have a title
    if not recipe_data['title']:
        recipe_data['title'] = f"Yippee! {recipe_data.get('cuisine', 'Fusion')} Delight"
    
    return recipe_data

@router.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: str):
    """
    Retrieve a specific recipe by ID.
    """
    try:
        # This would typically fetch from the database
        # For now, return a mock response
        raise HTTPException(status_code=404, detail="Recipe not found")
    except Exception as e:
        logger.error(f"Error retrieving recipe {recipe_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve recipe: {str(e)}")

@router.get("/user/{user_id}/recipes")
async def get_user_recipes(user_id: str, limit: int = 10):
    """
    Retrieve recipes generated by a specific user.
    """
    try:
        # This would typically fetch from the database
        # For now, return a mock response
        return {"recipes": [], "user_id": user_id}
    except Exception as e:
        logger.error(f"Error retrieving recipes for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user recipes: {str(e)}") 