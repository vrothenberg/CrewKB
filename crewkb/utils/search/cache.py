"""
Search cache for CrewKB.

This module provides a cache for search results to reduce API calls and improve
performance.
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Any, Dict


class SearchCache:
    """
    Cache for search results.
    
    This class provides a disk-based cache for search results to reduce API calls
    and improve performance. It uses a simple key-value store with JSON files.
    """
    
    def __init__(self, cache_dir: str = "cache/search"):
        """
        Initialize the cache.
        
        Args:
            cache_dir: The directory to store cache files.
        """
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
        self._memory_cache: Dict[str, Any] = {}
    
    def _ensure_cache_dir(self) -> None:
        """Ensure the cache directory exists."""
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> str:
        """
        Get the path to the cache file for a key.
        
        Args:
            key: The cache key.
            
        Returns:
            The path to the cache file.
        """
        # Create a hash of the key to use as the filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{key_hash}.json")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a cached result.
        
        Args:
            key: The cache key.
            
        Returns:
            The cached result, or None if not found.
        """
        # Check memory cache first
        if key in self._memory_cache:
            return self._memory_cache[key]
        
        # Check disk cache
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f:
                    result = json.load(f)
                
                # Store in memory cache for faster access next time
                self._memory_cache[key] = result
                return result
            except (json.JSONDecodeError, IOError):
                # If there's an error reading the cache, return None
                return None
        
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a cached result.
        
        Args:
            key: The cache key.
            value: The value to cache.
        """
        # Store in memory cache
        self._memory_cache[key] = value
        
        # Store on disk
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, "w") as f:
                json.dump(value, f)
        except IOError:
            # If there's an error writing to the cache, just log it and continue
            print(f"Error writing to cache: {cache_path}")
    
    def clear(self, key: Optional[str] = None) -> None:
        """
        Clear the cache.
        
        Args:
            key: The cache key to clear, or None to clear all.
        """
        if key is not None:
            # Clear specific key
            if key in self._memory_cache:
                del self._memory_cache[key]
            
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                except IOError:
                    print(f"Error removing cache file: {cache_path}")
        else:
            # Clear all
            self._memory_cache = {}
            
            try:
                for file in os.listdir(self.cache_dir):
                    if file.endswith(".json"):
                        os.remove(os.path.join(self.cache_dir, file))
            except IOError:
                print(f"Error clearing cache directory: {self.cache_dir}")
    
    def get_size(self) -> int:
        """
        Get the size of the cache.
        
        Returns:
            The number of items in the cache.
        """
        try:
            return len([f for f in os.listdir(self.cache_dir) if f.endswith(".json")])
        except IOError:
            return 0
