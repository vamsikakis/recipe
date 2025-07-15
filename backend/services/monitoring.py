import os
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.tracer import Tracer
from opencensus.trace.samplers import ProbabilitySampler

logger = logging.getLogger(__name__)

def setup_monitoring():
    """Setup Azure Application Insights monitoring"""
    try:
        # Get Application Insights instrumentation key
        instrumentation_key = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
        
        if instrumentation_key:
            # Setup Azure Log Handler
            azure_handler = AzureLogHandler(
                connection_string=instrumentation_key
            )
            azure_handler.setLevel(logging.INFO)
            
            # Add handler to root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(azure_handler)
            
            # Setup Azure Trace Exporter
            azure_exporter = AzureExporter(
                connection_string=instrumentation_key
            )
            
            # Setup tracer
            tracer = Tracer(
                exporter=azure_exporter,
                sampler=ProbabilitySampler(1.0)
            )
            
            logger.info("Azure Application Insights monitoring configured")
            
        else:
            logger.warning("APPLICATIONINSIGHTS_CONNECTION_STRING not found, monitoring disabled")
            
    except Exception as e:
        logger.error(f"Failed to setup monitoring: {e}")

def log_recipe_generation(user_id: str, preferences: dict, success: bool, error_message: str = None):
    """Log recipe generation events"""
    try:
        if success:
            logger.info(f"Recipe generated successfully for user: {user_id}", extra={
                'custom_dimensions': {
                    'user_id': user_id,
                    'cuisine': preferences.get('cuisine'),
                    'spice_level': preferences.get('spice_level'),
                    'meal_type': preferences.get('meal_type'),
                    'cooking_time': preferences.get('max_cooking_time'),
                    'dietary_restrictions': preferences.get('dietary_restrictions'),
                    'ingredients_count': len(preferences.get('available_ingredients', [])),
                    'event_type': 'recipe_generation_success'
                }
            })
        else:
            logger.error(f"Recipe generation failed for user: {user_id}", extra={
                'custom_dimensions': {
                    'user_id': user_id,
                    'error_message': error_message,
                    'event_type': 'recipe_generation_failure'
                }
            })
    except Exception as e:
        logger.error(f"Failed to log recipe generation event: {e}")

def log_api_request(endpoint: str, method: str, status_code: int, response_time: float):
    """Log API request metrics"""
    try:
        logger.info(f"API request: {method} {endpoint}", extra={
            'custom_dimensions': {
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code,
                'response_time_ms': response_time * 1000,
                'event_type': 'api_request'
            }
        })
    except Exception as e:
        logger.error(f"Failed to log API request: {e}")

def log_ai_service_call(service_name: str, success: bool, response_time: float, error_message: str = None):
    """Log AI service call metrics"""
    try:
        if success:
            logger.info(f"AI service call successful: {service_name}", extra={
                'custom_dimensions': {
                    'service_name': service_name,
                    'response_time_ms': response_time * 1000,
                    'event_type': 'ai_service_success'
                }
            })
        else:
            logger.error(f"AI service call failed: {service_name}", extra={
                'custom_dimensions': {
                    'service_name': service_name,
                    'error_message': error_message,
                    'event_type': 'ai_service_failure'
                }
            })
    except Exception as e:
        logger.error(f"Failed to log AI service call: {e}")

def log_database_operation(operation: str, success: bool, response_time: float, error_message: str = None):
    """Log database operation metrics"""
    try:
        if success:
            logger.info(f"Database operation successful: {operation}", extra={
                'custom_dimensions': {
                    'operation': operation,
                    'response_time_ms': response_time * 1000,
                    'event_type': 'database_success'
                }
            })
        else:
            logger.error(f"Database operation failed: {operation}", extra={
                'custom_dimensions': {
                    'operation': operation,
                    'error_message': error_message,
                    'event_type': 'database_failure'
                }
            })
    except Exception as e:
        logger.error(f"Failed to log database operation: {e}")

def log_user_interaction(user_id: str, action: str, details: dict = None):
    """Log user interaction events"""
    try:
        log_data = {
            'user_id': user_id,
            'action': action,
            'event_type': 'user_interaction'
        }
        
        if details:
            log_data.update(details)
        
        logger.info(f"User interaction: {action}", extra={
            'custom_dimensions': log_data
        })
    except Exception as e:
        logger.error(f"Failed to log user interaction: {e}")

def log_performance_metric(metric_name: str, value: float, unit: str = "ms"):
    """Log custom performance metrics"""
    try:
        logger.info(f"Performance metric: {metric_name}", extra={
            'custom_dimensions': {
                'metric_name': metric_name,
                'value': value,
                'unit': unit,
                'event_type': 'performance_metric'
            }
        })
    except Exception as e:
        logger.error(f"Failed to log performance metric: {e}")

def log_business_metric(metric_name: str, value: float, category: str = "general"):
    """Log business metrics"""
    try:
        logger.info(f"Business metric: {metric_name}", extra={
            'custom_dimensions': {
                'metric_name': metric_name,
                'value': value,
                'category': category,
                'event_type': 'business_metric'
            }
        })
    except Exception as e:
        logger.error(f"Failed to log business metric: {e}") 