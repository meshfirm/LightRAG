from __future__ import annotations

import os
import asyncio
import time
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass

from lightrag import QueryParam
from lightrag.utils import logger

# Import our custom NamespacedLightRAG
from namespaced_lightrag import NamespacedLightRAG


@dataclass
class InstanceData:
    """Store instance data with metadata"""
    instance: NamespacedLightRAG
    last_access: float


class LightRAGManager:
    """
    Manager for LightRAG instances in a multi-tenant deployment.
    
    This class handles:
    - Creating and managing per-user LightRAG instances
    - Routing queries to the appropriate user's instance
    - Cleanup of inactive instances
    """
    
    def __init__(self, base_config: dict = None):
        self.instance_data: Dict[str, InstanceData] = {}
        self.base_config = base_config or {}
        self.lock = threading.Lock()
        
        # Schedule cleanup task for inactive instances if running in an event loop
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._cleanup_task())
        except RuntimeError:
            # Not running in an event loop, skip scheduling
            pass
        
    def get_instance(self, user_id: str) -> NamespacedLightRAG:
        """Get or create a LightRAG instance for a specific user"""
        with self.lock:
            if user_id in self.instance_data:
                # Update last access time
                self.instance_data[user_id].last_access = time.time()
                return self.instance_data[user_id].instance
            
            # Create a new instance for this user
            instance = self._create_instance(user_id)
            
            # Store instance with current timestamp
            self.instance_data[user_id] = InstanceData(
                instance=instance,
                last_access=time.time()
            )
            
            return instance
    
    def _create_instance(self, user_id: str) -> NamespacedLightRAG:
        """Create a new LightRAG instance with user-specific configuration"""
        # Create user-specific working directory
        working_dir = os.path.join(os.getcwd(), f"lightrag_cache_user_{user_id}")
        os.makedirs(working_dir, exist_ok=True)
        
        # Start with base configuration
        config = self.base_config.copy()
        
        # Initialize embedding function if specified in base config
        embedding_func = config.pop("embedding_func", None)
        
        # Initialize LLM model function if specified in base config
        llm_model_func = config.pop("llm_model_func", None)
        
        # Initialize NamespacedLightRAG with user-specific settings
        try:
            rag_instance = NamespacedLightRAG(
                user_id=user_id,
                working_dir=working_dir,
                embedding_func=embedding_func,
                llm_model_func=llm_model_func,
                **config
            )
            
            # Ensure storages are initialized if auto-manage is disabled
            if not rag_instance.auto_manage_storages_states:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(rag_instance.initialize_storages())
                
            logger.info(f"Created LightRAG instance for user {user_id}")
            return rag_instance
            
        except Exception as e:
            logger.error(f"Error creating LightRAG instance for user {user_id}: {str(e)}")
            raise
    
    async def aquery(self, user_id: str, query: str, param: QueryParam = None) -> str:
        """Execute an asynchronous query for a specific user"""
        instance = self.get_instance(user_id)
        return await instance.aquery(query, param)
    
    def query(self, user_id: str, query: str, param: QueryParam = None) -> str:
        """Execute a synchronous query for a specific user"""
        instance = self.get_instance(user_id)
        return instance.query(query, param)
    
    async def ainsert(
        self, 
        user_id: str, 
        document: str | list[str], 
        **kwargs
    ) -> None:
        """Insert a document asynchronously for a specific user"""
        instance = self.get_instance(user_id)
        await instance.ainsert(document, **kwargs)
    
    def insert(
        self, 
        user_id: str, 
        document: str | list[str], 
        **kwargs
    ) -> None:
        """Insert a document for a specific user"""
        instance = self.get_instance(user_id)
        instance.insert(document, **kwargs)
    
    def remove_instance(self, user_id: str) -> bool:
        """Remove a user's LightRAG instance"""
        with self.lock:
            if user_id in self.instance_data:
                # Attempt to finalize storages gracefully
                try:
                    instance = self.instance_data[user_id].instance
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(instance.finalize_storages())
                except Exception as e:
                    logger.warning(f"Error finalizing storages for user {user_id}: {str(e)}")
                
                # Remove instance from the manager
                del self.instance_data[user_id]
                logger.info(f"Removed LightRAG instance for user {user_id}")
                return True
            return False
    
    async def _cleanup_task(self, interval=3600, max_idle_time=3600):
        """Background task to clean up inactive instances"""
        while True:
            await asyncio.sleep(interval)
            await self.cleanup_inactive_instances(max_idle_time)
    
    async def cleanup_inactive_instances(self, max_idle_time=3600):
        """Remove instances that haven't been used for a while"""
        current_time = time.time()
        
        # Collect user_ids to remove
        to_remove = []
        with self.lock:
            for user_id, instance_data in self.instance_data.items():
                if current_time - instance_data.last_access > max_idle_time:
                    to_remove.append(user_id)
        
        # Remove instances outside the lock to avoid deadlock
        for user_id in to_remove:
            self.remove_instance(user_id)
            
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} inactive LightRAG instances")