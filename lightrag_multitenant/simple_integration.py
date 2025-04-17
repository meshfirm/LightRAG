"""
Simple multi-tenant integration for LightRAG server
"""

import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Import our custom modules
from register_storage import register_storages
from simple_tenant_middleware import tenant_manager
from simple_tenant_routes import router as tenant_router

# Set up Neo4j configuration from environment
def configure_neo4j():
    """Configure Neo4j connection details from environment variables"""
    neo4j_config = {
        "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        "username": os.getenv("NEO4J_USERNAME", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD", "password"),
        "database": os.getenv("NEO4J_DATABASE", "neo4j"),
    }
    return neo4j_config

# Application startup and shutdown handler
@asynccontextmanager
async def tenant_lifespan(app: FastAPI):
    """Set up and tear down multi-tenant resources"""
    # Register custom storage implementations
    register_storages()
    
    # Configure backend storage details
    neo4j_config = configure_neo4j()
    
    # Set base configuration for tenant manager
    tenant_manager.base_config.update({
        # Neo4j configuration
        "uri": neo4j_config["uri"],
        "username": neo4j_config["username"],
        "password": neo4j_config["password"],
        "database": neo4j_config["database"],
        
        # Storage configuration
        "graph_storage": "NamespacedNeo4jGraphStorage",
        
        # Add other global configurations as needed
        # These will be passed to each tenant's LightRAG instance
    })
    
    # Start background cleanup task for inactive instances
    cleanup_task = asyncio.create_task(
        tenant_manager.cleanup_inactive_instances(max_idle_time=3600)
    )
    
    # Yield control back to FastAPI
    try:
        yield
    finally:
        # Clean up resources when shutting down
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
        
        # Clean up all tenant instances
        for user_id in list(tenant_manager.instance_data.keys()):
            tenant_manager.remove_instance(user_id)

def integrate_with_server(app: FastAPI):
    """
    Integrate multi-tenant functionality with an existing FastAPI server
    
    Args:
        app: The existing FastAPI application instance
    """
    # Add tenant lifespan manager if not already defined
    if not hasattr(app, "router"):
        # No existing lifespan handler, create new one
        app.router.lifespan_context = tenant_lifespan
    
    # Include the tenant-specific routes
    app.include_router(tenant_router)
    
    # Log integration
    from lightrag.utils import logger
    logger.info("Simple multi-tenant functionality integrated with LightRAG server")
    
    return app