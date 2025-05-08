"""
Retry strategy for CrewKB.

This module provides a retry strategy for API calls with exponential backoff.
"""

import asyncio
import logging
import random
from typing import Callable, Any, TypeVar, Optional, Type, List

# Type variable for the return type of the function
T = TypeVar("T")

# Set up logging
logger = logging.getLogger(__name__)


class RetryStrategy:
    """
    Retry strategy for API calls.
    
    This class provides a retry strategy for API calls with exponential backoff.
    It will retry failed calls with increasing delays between retries.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
        jitter: bool = True,
        max_backoff: float = 60.0,
        retry_exceptions: Optional[List[Type[Exception]]] = None
    ):
        """
        Initialize the retry strategy.
        
        Args:
            max_retries: The maximum number of retries.
            backoff_factor: The factor to multiply the delay by after each retry.
            jitter: Whether to add random jitter to the delay.
            max_backoff: The maximum backoff time in seconds.
            retry_exceptions: The exceptions to retry on. If None, retry on all exceptions.
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.max_backoff = max_backoff
        self.retry_exceptions = retry_exceptions or [Exception]
    
    async def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute a function with retry logic.
        
        Args:
            func: The function to execute.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
            
        Returns:
            The result of the function.
            
        Raises:
            Exception: If the function fails after all retries.
        """
        retries = 0
        last_exception = None
        
        while retries <= self.max_retries:
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except tuple(self.retry_exceptions) as e:
                last_exception = e
                retries += 1
                
                if retries > self.max_retries:
                    logger.error(
                        f"Failed after {self.max_retries} retries: {str(e)}"
                    )
                    raise
                
                # Calculate backoff time
                backoff = min(
                    self.backoff_factor ** (retries - 1),
                    self.max_backoff
                )
                
                # Add jitter if enabled
                if self.jitter:
                    backoff = backoff * (0.5 + random.random())
                
                logger.warning(
                    f"Retry {retries}/{self.max_retries} after {backoff:.2f}s: {str(e)}"
                )
                
                # Wait before retrying
                await asyncio.sleep(backoff)
        
        # This should never happen, but just in case
        if last_exception:
            raise last_exception
        
        raise Exception("Unexpected error in retry logic")
    
    async def execute_with_fallback(
        self,
        func: Callable[..., T],
        fallback: Callable[..., T],
        *args,
        **kwargs
    ) -> T:
        """
        Execute a function with retry logic and fallback.
        
        Args:
            func: The function to execute.
            fallback: The fallback function to execute if all retries fail.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
            
        Returns:
            The result of the function or fallback.
        """
        try:
            return await self.execute(func, *args, **kwargs)
        except Exception as e:
            logger.warning(
                f"Falling back after failure: {str(e)}"
            )
            
            if asyncio.iscoroutinefunction(fallback):
                return await fallback(*args, **kwargs)
            else:
                return fallback(*args, **kwargs)
