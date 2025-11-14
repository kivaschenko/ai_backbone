"""
Error handling and retry logic utilities.
"""

import time
import logging
from typing import Callable, Any, Type
from functools import wraps

logger = logging.getLogger(__name__)


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Decorator to retry a function on exception.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch

    Example:
        @retry_on_exception(max_retries=3, delay=1, backoff=2)
        def fetch_data():
            # Function that might fail
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries: {str(e)}"
                        )
                        raise

                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries}): {str(e)}. "
                        f"Retrying in {current_delay}s..."
                    )

                    time.sleep(current_delay)
                    current_delay *= backoff

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


class ErrorHandler:
    """Centralized error handling."""

    @staticmethod
    def handle_api_error(error: Exception, context: str = "") -> dict:
        """
        Handle API errors and return standardized error response.

        Args:
            error: Exception that occurred
            context: Additional context about the error

        Returns:
            Standardized error dictionary
        """
        error_msg = str(error)
        error_type = type(error).__name__

        logger.error(f"API Error [{error_type}] {context}: {error_msg}")

        return {
            "error": True,
            "error_type": error_type,
            "message": error_msg,
            "context": context,
        }

    @staticmethod
    def handle_validation_error(field: str, message: str) -> dict:
        """
        Handle validation errors.

        Args:
            field: Field name that failed validation
            message: Validation error message

        Returns:
            Standardized validation error dictionary
        """
        return {
            "error": True,
            "error_type": "ValidationError",
            "field": field,
            "message": message,
        }

    @staticmethod
    def handle_connector_error(connector_name: str, error: Exception) -> dict:
        """
        Handle data connector errors.

        Args:
            connector_name: Name of the connector that failed
            error: Exception that occurred

        Returns:
            Standardized connector error dictionary
        """
        logger.error(f"Connector Error [{connector_name}]: {str(error)}")

        return {
            "error": True,
            "error_type": "ConnectorError",
            "connector": connector_name,
            "message": str(error),
        }
