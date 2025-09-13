"""Cache management for kdx-pi-cam.

This module handles caching of video clips and photos with size limits,
compression, and cleanup.
"""

import asyncio
import logging
import os
import shutil
import time
from typing import List

from config import get_config

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages cache directory with size limits and cleanup."""

    def __init__(self):
        """Initialize the cache manager."""
        config = get_config()
        self.cache_dir = config.cache_dir
        self.max_size_mb = config.cache_max_size_mb
        self.compression_enabled = config.cache_compression_enabled
        self.cleanup_interval = config.cache_cleanup_interval

        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.join(self.cache_dir, 'logs'), exist_ok=True)

        # Start cleanup task
        self.cleanup_task: asyncio.Task = None
        self.running = False

    async def start_cleanup(self):
        """Start the periodic cleanup task."""
        if self.running:
            return
        self.running = True
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_cleanup(self):
        """Stop the periodic cleanup task."""
        self.running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

    async def _cleanup_loop(self):
        """Periodic cleanup loop."""
        while self.running:
            try:
                self._cleanup_old_files()
                await asyncio.sleep(self.cleanup_interval)
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")
                await asyncio.sleep(60)

    def _cleanup_old_files(self):
        """Remove old files if cache size exceeds limit."""
        try:
            # Get all files in cache
            files = []
            for root, dirs, filenames in os.walk(self.cache_dir):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    files.append((filepath, os.path.getmtime(filepath)))

            # Sort by modification time (oldest first)
            files.sort(key=lambda x: x[1])

            # Calculate total size
            total_size = sum(os.path.getsize(f[0]) for f in files)

            # Remove oldest files until under limit
            max_size_bytes = self.max_size_mb * 1024 * 1024
            while total_size > max_size_bytes and files:
                filepath, _ = files.pop(0)
                size = os.path.getsize(filepath)
                try:
                    os.remove(filepath)
                    total_size -= size
                    logger.info(f"Removed old cache file: {filepath}")
                except OSError as e:
                    logger.error(f"Failed to remove cache file {filepath}: {e}")

        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")

    def get_cache_size_mb(self) -> float:
        """Get current cache size in MB."""
        total_size = 0
        for root, dirs, filenames in os.walk(self.cache_dir):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                total_size += os.path.getsize(filepath)
        return total_size / (1024 * 1024)

    def clear_cache(self):
        """Clear all files in cache directory."""
        try:
            for root, dirs, filenames in os.walk(self.cache_dir):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    try:
                        os.remove(filepath)
                    except OSError:
                        pass
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")


# Global cache manager instance
_cache_manager: CacheManager = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager