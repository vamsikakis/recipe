import os
import logging
import httpx
from typing import Dict, Any, List, Optional
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
import asyncio

logger = logging.getLogger(__name__)

# Azure AI Language client
text_analytics_client = None

# Azure OpenAI client
openai_client = None

def init_ai_clients():
    """Initialize Azure AI service clients"""
    global text_analytics_client, openai_client
    
    try:
        # Initialize Azure AI Language client
        language_endpoint = os.getenv('AZURE_LANGUAGE_ENDPOINT')
        language_key = os.getenv('AZURE_LANGUAGE_KEY')
        
        if language_endpoint and language_key:
            text_analytics_client = TextAnalyticsClient(
                endpoint=language_endpoint,
                credential=AzureKeyCredential(language_key)
            )
            logger.info("Azure AI Language client initialized")
        else:
            logger.warning("Azure AI Language credentials not found, using mock mode")
        
        # Initialize Azure OpenAI client
        openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        openai_key = os.getenv('AZURE_OPENAI_KEY')
        openai_api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2023-12-01-preview')
        
        if openai_endpoint and openai_key:
            openai_client = AzureOpenAI(
                azure_endpoint=openai_endpoint,
                api_key=openai_key,
                api_version=openai_api_version
            )
            logger.info("Azure OpenAI client initialized")
        else:
            logger.warning("Azure OpenAI credentials not found, using mock mode")
            
    except Exception as e:
        logger.error(f"Failed to initialize AI clients: {e}")

async def call_azure_ai_language(text_input: str) -> Dict[str, Any]:
    """Call Azure AI Language for NLP processing"""
    try:
        if text_analytics_client:
            # Process text with Azure AI Language
            documents = [text_input]
            
            # Named Entity Recognition
            entity_result = text_analytics_client.recognize_entities(documents)
            entities = []
            for doc in entity_result:
                for entity in doc.entities:
                    entities.append({
                        'text': entity.text,
                        'category': entity.category,
                        'confidence_score': entity.confidence_score
                    })
            
            # Key Phrase Extraction
            key_phrase_result = text_analytics_client.extract_key_phrases(documents)
            key_phrases = []
            for doc in key_phrase_result:
                key_phrases.extend(doc.key_phrases)
            
            # Sentiment Analysis
            sentiment_result = text_analytics_client.analyze_sentiment(documents)
            sentiment = "neutral"
            for doc in sentiment_result:
                sentiment = doc.document_sentiment
                break
            
            result = {
                'entities': entities,
                'key_phrases': key_phrases,
                'sentiment': sentiment
            }
            
            logger.info(f"NLP processing completed: {len(entities)} entities, {len(key_phrases)} key phrases")
            return result
            
        else:
            # Mock response for development
            mock_entities = [
                {'text': 'chicken', 'category': 'Food', 'confidence_score': 0.95},
                {'text': 'bell peppers', 'category': 'Food', 'confidence_score': 0.92},
                {'text': 'spicy', 'category': 'Attribute', 'confidence_score': 0.88}
            ]
            
            mock_key_phrases = ['chicken', 'bell peppers', 'spicy dinner', 'cooking preferences']
            
            result = {
                'entities': mock_entities,
                'key_phrases': mock_key_phrases,
                'sentiment': 'positive'
            }
            
            logger.info("Using mock NLP response")
            return result
            
    except Exception as e:
        logger.error(f"Error in Azure AI Language processing: {e}")
        # Return safe fallback
        return {
            'entities': [],
            'key_phrases': [],
            'sentiment': 'neutral'
        }

async def call_azure_openai_generative_ai(prompt: str) -> str:
    """Call Azure OpenAI Service for recipe generation"""
    try:
        if openai_client:
            # Get deployment name from environment
            deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-35-turbo')
            
            # Create messages for chat completion
            messages = [
                {
                    "role": "system",
                    "content": "You are a creative chef specializing in Yippee! noodles and pasta recipes. Generate unique, delicious, and practical recipes."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Call Azure OpenAI
            response = openai_client.chat.completions.create(
                model=deployment_name,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=0.9
            )
            
            generated_text = response.choices[0].message.content
            logger.info("Recipe generated successfully with Azure OpenAI")
            return generated_text
            
        else:
            # Mock response for development
            mock_recipe = """
Title: Yippee! Spicy Chicken Stir Fry
Description: A delicious fusion of Indian spices with Asian stir-fry technique using Yippee noodles
Cooking Time: 25 minutes
Difficulty: Medium
Tags: spicy, fusion, chicken, quick

Ingredients:
- Yippee noodles: 2 packets
- Chicken breast: 300g, sliced
- Bell peppers: 2, sliced
- Onions: 1, sliced
- Ginger: 1 inch, minced
- Garlic: 4 cloves, minced
- Soy sauce: 2 tbsp
- Red chili powder: 1 tsp
- Garam masala: 1/2 tsp
- Oil: 2 tbsp
- Salt: to taste

Instructions:
1. Boil Yippee noodles according to package instructions and set aside (Time: 5 minutes)
2. Heat oil in a wok and add ginger-garlic paste (Time: 2 minutes)
3. Add chicken and cook until golden brown (Time: 8 minutes)
4. Add vegetables and stir-fry for 3 minutes (Time: 3 minutes)
5. Add spices and soy sauce, mix well (Time: 2 minutes)
6. Add cooked noodles and toss everything together (Time: 3 minutes)
7. Serve hot with garnishes (Time: 2 minutes)
"""
            
            logger.info("Using mock recipe generation")
            return mock_recipe
            
    except Exception as e:
        logger.error(f"Error in Azure OpenAI recipe generation: {e}")
        # Return safe fallback
        return """
Title: Yippee! Classic Masala
Description: A simple and delicious Yippee noodles recipe
Cooking Time: 15 minutes
Difficulty: Easy
Tags: classic, vegetarian, quick

Ingredients:
- Yippee noodles: 1 packet
- Onions: 1, chopped
- Tomatoes: 1, chopped
- Oil: 1 tbsp
- Salt: to taste

Instructions:
1. Boil noodles according to package instructions (Time: 5 minutes)
2. Heat oil and sauté onions (Time: 3 minutes)
3. Add tomatoes and cook (Time: 3 minutes)
4. Add noodles and mix well (Time: 2 minutes)
5. Serve hot (Time: 2 minutes)
"""

async def call_azure_openai_dalle(image_prompt: str) -> str:
    """Call Azure OpenAI Service (DALL-E 3) for image generation"""
    try:
        if openai_client:
            # Get DALL-E deployment name from environment
            dalle_deployment_name = os.getenv('AZURE_OPENAI_DALLE_DEPLOYMENT_NAME', 'dall-e-3')
            
            # Call DALL-E 3
            response = openai_client.images.generate(
                model=dalle_deployment_name,
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            logger.info("Image generated successfully with DALL-E 3")
            return image_url
            
        else:
            # Mock image URL for development
            mock_image_url = "https://via.placeholder.com/1024x1024/FF6B35/FFFFFF?text=Yippee+Recipe"
            logger.info("Using mock image generation")
            return mock_image_url
            
    except Exception as e:
        logger.error(f"Error in DALL-E image generation: {e}")
        # Return safe fallback
        return "https://via.placeholder.com/1024x1024/FF6B35/FFFFFF?text=Recipe+Image"

async def call_azure_openai_with_retry(func, *args, max_retries=3, **kwargs):
    """Retry wrapper for Azure OpenAI calls"""
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Final attempt failed for {func.__name__}: {e}")
                raise
            else:
                logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

# Initialize clients on module import
init_ai_clients() 