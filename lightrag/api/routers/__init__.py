"""
This module contains all the routers for the LightRAG API.
"""

from .document_routes import router as document_router
from .query_routes import router as query_router
from .graph_routes import router as graph_router
from .ollama_api import OllamaAPI
from ..user_rag_manager import LightRAGManager, init_manager, get_manager

__all__ = ["document_router", "query_router", "graph_router", "OllamaAPI", "LightRAGManager", "init_manager", "get_manager"]