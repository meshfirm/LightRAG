import asyncio
import os
from typing import Dict, Optional
import time

from lightrag import LightRAG
from lightrag.namespace import make_namespace
from lightrag.utils import logger

class LightRAGManager:
    """
    Manages LightRAG instances for multiple users.
    
    This class creates and caches LightRAG instances with user-specific namespaces,
    ensuring that each user's data is isolated from others.
    """
    
    def __init__(self, rag_factory_func, max_instances: int = 100, cleanup_interval: int = 3600):
        """
        Initialize the LightRAG manager.
        
        Args:
            rag_factory_func: A function that creates a new LightRAG instance without user prefix
            max_instances: Maximum number of instances to keep in memory (defaults to 100)
            cleanup_interval: Time in seconds between cleanup tasks (defaults to 1 hour)
        """
        self.rag_factory_func = rag_factory_func
        self.max_instances = max_instances
        self.cleanup_interval = cleanup_interval
        self.instances: Dict[str, LightRAG] = {}
        self.last_accessed: Dict[str, float] = {}
        self.lock = asyncio.Lock()
        self._cleanup_task = None
    
    def _start_cleanup_task(self):
        """Start a background task to clean up unused instances."""
        if self._cleanup_task is not None:
            # Task already started
            return
            
        async def cleanup_task():
            while True:
                await asyncio.sleep(self.cleanup_interval)
                await self.cleanup_old_instances()
                
        # Create the task
        self._cleanup_task = asyncio.create_task(cleanup_task())
        
    async def cleanup_old_instances(self):
        """Remove old instances if we exceed the maximum number."""
        async with self.lock:
            if len(self.instances) <= self.max_instances:
                return
                
            # Sort by last accessed time
            sorted_items = sorted(self.last_accessed.items(), key=lambda x: x[1])
            
            # Remove oldest instances until we're below max
            count_to_remove = len(self.instances) - self.max_instances
            for user_id, _ in sorted_items[:count_to_remove]:
                if user_id in self.instances:
                    # Properly clean up the instance before removing
                    try:
                        await self.instances[user_id].finalize_storages()
                    except Exception as e:
                        logger.error(f"Error finalizing instance for user {user_id}: {e}")
                    
                    del self.instances[user_id]
                    del self.last_accessed[user_id]
                    logger.info(f"Cleaned up RAG instance for user {user_id}")
    
    async def get_instance(self, user_id: str) -> LightRAG:
        """
        Get or create a LightRAG instance for a specific user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            A LightRAG instance with the appropriate user-specific namespace
        """
        # Start cleanup task if this is the first async call
        if self._cleanup_task is None:
            self._start_cleanup_task()
        
        async with self.lock:
            # Update last accessed time
            self.last_accessed[user_id] = time.time()
            
            # Return existing instance if available
            if user_id in self.instances:
                return self.instances[user_id]
            
            # Create new instance with user_id as prefix
            user_prefix = f"user_{user_id}_"
            
            # Get a base rag instance
            rag_instance = self.rag_factory_func()
            
            # Set the namespace prefix for this user
            rag_instance.namespace_prefix = user_prefix
            
            # Initialize storages
            await rag_instance.initialize_storages()
            
            # Store and return the instance
            self.instances[user_id] = rag_instance
            logger.info(f"Created new RAG instance for user {user_id}")
            
            return rag_instance
    
    async def close(self):
        """Close all RAG instances."""
        # Cancel the cleanup task if it exists
        if self._cleanup_task is not None:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            
        async with self.lock:
            for user_id, instance in self.instances.items():
                try:
                    await instance.finalize_storages()
                    logger.info(f"Finalized RAG instance for user {user_id}")
                except Exception as e:
                    logger.error(f"Error finalizing instance for user {user_id}: {e}")
            
            self.instances.clear()
            self.last_accessed.clear()
            
# Singleton instance
_manager: Optional[LightRAGManager] = None

def init_manager(rag_factory_func, max_instances: int = 100):
    """Initialize the global manager instance."""
    global _manager
    if _manager is None:
        _manager = LightRAGManager(rag_factory_func, max_instances)
    return _manager

def get_manager() -> LightRAGManager:
    """Get the global manager instance."""
    global _manager
    if _manager is None:
        raise RuntimeError("LightRAGManager not initialized. Call init_manager() first.")
    return _manager