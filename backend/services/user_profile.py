import os
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
import redis.asyncio as redis
from azure.cosmos.exceptions import CosmosHttpResponseError

from services.database import user_profiles_container

logger = logging.getLogger(__name__)

# Redis client for caching
redis_client = None

async def init_redis():
    """Initialize Redis connection for caching"""
    global redis_client
    
    try:
        redis_connection_string = os.getenv('REDIS_CONNECTION_STRING')
        if redis_connection_string:
            redis_client = redis.from_url(redis_connection_string)
            await redis_client.ping()
            logger.info("Redis connection established")
        else:
            logger.warning("REDIS_CONNECTION_STRING not found, caching disabled")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        redis_client = None

async def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve user profile from cache first, then from Cosmos DB"""
    try:
        # Try cache first
        if redis_client:
            try:
                cached_profile = await redis_client.get(f"user_profile:{user_id}")
                if cached_profile:
                    profile_data = json.loads(cached_profile)
                    logger.info(f"Retrieved user profile from cache: {user_id}")
                    return profile_data
            except Exception as e:
                logger.warning(f"Cache retrieval failed: {e}")
        
        # Fallback to Cosmos DB
        if user_profiles_container:
            try:
                profile_data = user_profiles_container.read_item(user_id, user_id)
                logger.info(f"Retrieved user profile from Cosmos DB: {user_id}")
                
                # Cache the result
                if redis_client:
                    try:
                        await redis_client.setex(
                            f"user_profile:{user_id}",
                            3600,  # 1 hour cache
                            json.dumps(profile_data)
                        )
                    except Exception as e:
                        logger.warning(f"Failed to cache user profile: {e}")
                
                return profile_data
            except CosmosHttpResponseError:
                logger.info(f"User profile not found: {user_id}")
                return None
        else:
            # Mock mode - return default profile
            default_profile = {
                "user_id": user_id,
                "preferences": {
                    "cuisine": "Indian",
                    "spice_level": "Medium",
                    "meal_type": ["Lunch", "Dinner"],
                    "max_cooking_time": "30 mins",
                    "dietary_restrictions": [],
                    "available_ingredients": []
                },
                "saved_recipes": [],
                "disliked_ingredients": [],
                "cooking_history": [],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            logger.info(f"Using mock user profile for: {user_id}")
            return default_profile
            
    except Exception as e:
        logger.error(f"Error retrieving user profile {user_id}: {e}")
        return None

async def update_user_profile(user_id: str, new_data: Dict[str, Any]) -> bool:
    """Update user profile in both cache and Cosmos DB"""
    try:
        # Get existing profile or create new one
        existing_profile = await get_user_profile(user_id)
        
        if existing_profile:
            # Update existing profile
            existing_profile.update(new_data)
            existing_profile['updated_at'] = datetime.utcnow().isoformat()
            profile_data = existing_profile
        else:
            # Create new profile
            profile_data = {
                "user_id": user_id,
                "preferences": new_data.get('preferences', {}),
                "saved_recipes": new_data.get('saved_recipes', []),
                "disliked_ingredients": new_data.get('disliked_ingredients', []),
                "cooking_history": new_data.get('cooking_history', []),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        
        # Update Cosmos DB
        if user_profiles_container:
            try:
                user_profiles_container.upsert_item(profile_data)
                logger.info(f"Updated user profile in Cosmos DB: {user_id}")
            except Exception as e:
                logger.error(f"Failed to update user profile in Cosmos DB: {e}")
                return False
        
        # Update cache
        if redis_client:
            try:
                await redis_client.setex(
                    f"user_profile:{user_id}",
                    3600,  # 1 hour cache
                    json.dumps(profile_data)
                )
                logger.info(f"Updated user profile in cache: {user_id}")
            except Exception as e:
                logger.warning(f"Failed to update user profile in cache: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating user profile {user_id}: {e}")
        return False

async def add_recipe_to_history(user_id: str, recipe_id: str) -> bool:
    """Add a recipe to user's cooking history"""
    try:
        profile = await get_user_profile(user_id)
        if not profile:
            profile = {
                "user_id": user_id,
                "preferences": {},
                "saved_recipes": [],
                "disliked_ingredients": [],
                "cooking_history": [],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        
        # Add recipe to history if not already present
        if recipe_id not in profile.get('cooking_history', []):
            profile['cooking_history'].insert(0, recipe_id)  # Add to beginning
            # Keep only last 50 recipes
            profile['cooking_history'] = profile['cooking_history'][:50]
            profile['updated_at'] = datetime.utcnow().isoformat()
            
            return await update_user_profile(user_id, profile)
        
        return True
        
    except Exception as e:
        logger.error(f"Error adding recipe to history: {e}")
        return False

async def save_recipe(user_id: str, recipe_id: str) -> bool:
    """Save a recipe to user's favorites"""
    try:
        profile = await get_user_profile(user_id)
        if not profile:
            profile = {
                "user_id": user_id,
                "preferences": {},
                "saved_recipes": [],
                "disliked_ingredients": [],
                "cooking_history": [],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        
        # Add recipe to saved recipes if not already present
        if recipe_id not in profile.get('saved_recipes', []):
            profile['saved_recipes'].append(recipe_id)
            profile['updated_at'] = datetime.utcnow().isoformat()
            
            return await update_user_profile(user_id, profile)
        
        return True
        
    except Exception as e:
        logger.error(f"Error saving recipe: {e}")
        return False

async def add_disliked_ingredient(user_id: str, ingredient: str) -> bool:
    """Add an ingredient to user's disliked list"""
    try:
        profile = await get_user_profile(user_id)
        if not profile:
            profile = {
                "user_id": user_id,
                "preferences": {},
                "saved_recipes": [],
                "disliked_ingredients": [],
                "cooking_history": [],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        
        # Add ingredient to disliked list if not already present
        if ingredient.lower() not in [i.lower() for i in profile.get('disliked_ingredients', [])]:
            profile['disliked_ingredients'].append(ingredient)
            profile['updated_at'] = datetime.utcnow().isoformat()
            
            return await update_user_profile(user_id, profile)
        
        return True
        
    except Exception as e:
        logger.error(f"Error adding disliked ingredient: {e}")
        return False

async def clear_user_cache(user_id: str) -> bool:
    """Clear user profile from cache"""
    try:
        if redis_client:
            await redis_client.delete(f"user_profile:{user_id}")
            logger.info(f"Cleared user profile cache: {user_id}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error clearing user cache: {e}")
        return False 