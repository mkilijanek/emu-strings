"""
Retry utilities with exponential backoff.

This module provides retry decorators for handling transient failures
in Docker operations and other external services.
"""

import functools
import logging
import time
from typing import Callable, Optional, Tuple, Type

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    backoff_seconds: float = 1.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable:
    """
    Decorator that retries a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        backoff_seconds: Initial backoff time in seconds (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
        exceptions: Tuple of exceptions to catch and retry on
        on_retry: Optional callback function called on each retry
                 Receives (exception, attempt_number)

    Returns:
        Decorated function with retry logic

    Example:
        @retry_with_backoff(max_retries=3, backoff_seconds=1)
        def start_container():
            # This will retry up to 3 times with delays of 1s, 2s, 4s
            return docker_client.containers.run(...)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries - 1:
                        # Final attempt failed, re-raise
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} attempts: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(backoff_seconds * (2 ** attempt), max_delay)

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} for {func.__name__} failed: {e}. "
                        f"Retrying in {delay}s..."
                    )

                    # Call on_retry callback if provided
                    if on_retry:
                        try:
                            on_retry(e, attempt + 1)
                        except Exception:
                            pass

                    time.sleep(delay)

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            return None

        # Attach retry metadata for introspection
        wrapper._retry_config = {
            "max_retries": max_retries,
            "backoff_seconds": backoff_seconds,
            "max_delay": max_delay,
        }

        return wrapper

    return decorator


def is_retryable_docker_error(error: Exception) -> bool:
    """
    Check if a Docker error is retryable.

    Some Docker errors are transient and can be retried:
    - Connection errors
    - Timeout errors
    - Temporary daemon errors

    Args:
        error: The exception to check

    Returns:
        True if the error is retryable
    """
    error_str = str(error).lower()
    retryable_patterns = [
        "connection",
        "timeout",
        "temporary",
        "503",
        "service unavailable",
        "no such container",
    ]
    return any(pattern in error_str for pattern in retryable_patterns)
