from __future__ import annotations

import os
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

from lightrag import LightRAG, QueryParam
from lightrag.utils import logger


class NamespacedLightRAG(LightRAG):
    """
    Extension of LightRAG that enforces namespace isolation between users.
    This implementation creates user-specific namespaces within a single Neo4j database.
    """
    
    def __init__(
        self, 
        user_id: str,
        working_dir: Optional[str] = None,
        **kwargs
    ):
        # Generate user-specific working directory if not provided
        if working_dir is None:
            working_dir = os.path.join(os.getcwd(), f"lightrag_cache_user_{user_id}")
            os.makedirs(working_dir, exist_ok=True)
        
        # Create a namespace prefix for user isolation
        namespace_prefix = f"user_{user_id}_"
        
        # Prepare Neo4j configuration with namespace settings
        # These settings will be passed to NetworkXStorage or Neo4jGraphStorage
        graph_storage_config = kwargs.pop("vector_db_storage_cls_kwargs", {})
        graph_storage_config.update({
            "namespace_prefix": namespace_prefix,
            "user_id": user_id,
        })
        
        # Initialize the parent LightRAG class with user-specific settings
        super().__init__(
            working_dir=working_dir,
            namespace_prefix=namespace_prefix,
            vector_db_storage_cls_kwargs=graph_storage_config,
            **kwargs
        )
        
        # Store user_id for reference
        self.user_id = user_id
        logger.info(f"Initialized NamespacedLightRAG for user: {user_id}")
    
    async def aquery(
        self,
        query: str,
        param: QueryParam = None,
        system_prompt: str = None,
    ) -> str:
        """
        Override query method to add additional logging for user tracking
        """
        logger.info(f"User {self.user_id} executing query: {query[:50]}...")
        if param is None:
            param = QueryParam()
        
        # Execute the query using the parent implementation
        return await super().aquery(query, param, system_prompt)
    
    async def ainsert(
        self,
        input: str | list[str],
        split_by_character: str | None = None,
        split_by_character_only: bool = False,
        ids: str | list[str] | None = None,
        file_paths: str | list[str] | None = None,
    ) -> None:
        """
        Override insert method to add user context to file paths
        """
        # Add user context to file paths if not already present
        if file_paths is not None:
            if isinstance(file_paths, str):
                if not file_paths.startswith(f"user_{self.user_id}_"):
                    file_paths = f"user_{self.user_id}_{file_paths}"
            else:
                file_paths = [
                    f"user_{self.user_id}_{path}" if not path.startswith(f"user_{self.user_id}_") else path
                    for path in file_paths
                ]
        
        logger.info(f"User {self.user_id} inserting document(s)")
        await super().ainsert(
            input, split_by_character, split_by_character_only, ids, file_paths
        )