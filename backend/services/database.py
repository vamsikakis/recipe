import os
import logging
from typing import List, Dict, Any, Optional
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError
import json

logger = logging.getLogger(__name__)

# Global Cosmos DB client
cosmos_client = None
database = None
recipes_container = None
generated_recipes_container = None
user_profiles_container = None

async def init_cosmos_db():
    """Initialize Cosmos DB connection and containers"""
    global cosmos_client, database, recipes_container, generated_recipes_container, user_profiles_container
    
    try:
        # Get connection string from environment
        connection_string = os.getenv('COSMOS_DB_CONNECTION_STRING')
        if not connection_string:
            logger.warning("COSMOS_DB_CONNECTION_STRING not found, using mock mode")
            return
        
        # Initialize Cosmos client
        cosmos_client = CosmosClient.from_connection_string(connection_string)
        
        # Get database
        database_name = os.getenv('COSMOS_DB_NAME', 'yippee-recipes')
        database = cosmos_client.get_database_client(database_name)
        
        # Get containers
        recipes_container = database.get_container_client('recipes')
        generated_recipes_container = database.get_container_client('generated_recipes')
        user_profiles_container = database.get_container_client('user_profiles')
        
        logger.info("Cosmos DB initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Cosmos DB: {e}")
        # Continue with mock mode for development
        pass

async def store_generated_recipe(recipe_data: Dict[str, Any]) -> str:
    """Store a generated recipe in Cosmos DB"""
    try:
        if generated_recipes_container:
            # Add metadata
            recipe_data['type'] = 'generated_recipe'
            recipe_data['created_at'] = recipe_data.get('created_at', '')
            
            # Store in Cosmos DB
            response = generated_recipes_container.create_item(recipe_data)
            logger.info(f"Stored generated recipe: {recipe_data['id']}")
            return recipe_data['id']
        else:
            # Mock mode
            logger.info(f"Mock: Stored generated recipe: {recipe_data['id']}")
            return recipe_data['id']
            
    except CosmosHttpResponseError as e:
        logger.error(f"Cosmos DB error storing recipe: {e}")
        raise
    except Exception as e:
        logger.error(f"Error storing generated recipe: {e}")
        raise

async def get_base_recipes() -> List[Dict[str, Any]]:
    """Retrieve base recipes from Cosmos DB"""
    try:
        if recipes_container:
            # Query base recipes
            query = "SELECT * FROM c WHERE c.type = 'base_recipe'"
            items = list(recipes_container.query_items(query, enable_cross_partition_query=True))
            logger.info(f"Retrieved {len(items)} base recipes from Cosmos DB")
            return items
        else:
            # Return mock base recipes for development
            mock_recipes = [
                {
                    "id": "base-1",
                    "title": "Classic Yippee Masala",
                    "cuisine": "Indian",
                    "difficulty": "Easy",
                    "cooking_time": 15,
                    "tags": ["quick", "vegetarian", "indian"],
                    "ingredients": ["Yippee noodles", "onions", "tomatoes", "spices"],
                    "type": "base_recipe"
                },
                {
                    "id": "base-2", 
                    "title": "Yippee Stir Fry",
                    "cuisine": "Asian",
                    "difficulty": "Medium",
                    "cooking_time": 20,
                    "tags": ["asian", "quick", "vegetarian"],
                    "ingredients": ["Yippee noodles", "vegetables", "soy sauce", "ginger"],
                    "type": "base_recipe"
                }
            ]
            logger.info("Using mock base recipes")
            return mock_recipes
            
    except CosmosHttpResponseError as e:
        logger.error(f"Cosmos DB error retrieving base recipes: {e}")
        return []
    except Exception as e:
        logger.error(f"Error retrieving base recipes: {e}")
        return []

async def get_recipe_by_id(recipe_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a specific recipe by ID"""
    try:
        if generated_recipes_container:
            # Try generated recipes first
            try:
                item = generated_recipes_container.read_item(recipe_id, recipe_id)
                return item
            except CosmosHttpResponseError:
                pass
            
        if recipes_container:
            # Try base recipes
            try:
                item = recipes_container.read_item(recipe_id, recipe_id)
                return item
            except CosmosHttpResponseError:
                pass
                
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving recipe {recipe_id}: {e}")
        return None

async def get_user_recipes(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve recipes generated by a specific user"""
    try:
        if generated_recipes_container:
            query = f"SELECT * FROM c WHERE c.user_id = '{user_id}' AND c.type = 'generated_recipe' ORDER BY c.created_at DESC OFFSET 0 LIMIT {limit}"
            items = list(generated_recipes_container.query_items(query, enable_cross_partition_query=True))
            logger.info(f"Retrieved {len(items)} recipes for user {user_id}")
            return items
        else:
            # Mock response
            return []
            
    except CosmosHttpResponseError as e:
        logger.error(f"Cosmos DB error retrieving user recipes: {e}")
        return []
    except Exception as e:
        logger.error(f"Error retrieving user recipes: {e}")
        return []

async def create_container_if_not_exists(container_name: str, partition_key: str = "/id"):
    """Create a Cosmos DB container if it doesn't exist"""
    try:
        if not database:
            logger.warning("Database not initialized, skipping container creation")
            return
            
        try:
            database.get_container_client(container_name)
            logger.info(f"Container {container_name} already exists")
        except CosmosHttpResponseError:
            # Container doesn't exist, create it
            database.create_container(
                id=container_name,
                partition_key=PartitionKey(path=partition_key)
            )
            logger.info(f"Created container: {container_name}")
            
    except Exception as e:
        logger.error(f"Error creating container {container_name}: {e}")
        raise 