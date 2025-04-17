"""
Main entry point for LightRAG with simple multi-tenant support
"""

import os
from lightrag.api.lightrag_server import get_application
from lightrag_multitenant.simple_integration import integrate_with_server
from lightrag.utils import logger

# Get the base LightRAG application
app = get_application()

# Integrate simple multi-tenant functionality
app = integrate_with_server(app)

logger.info("LightRAG server with simple multi-tenant support initialized")

# This is important for Google Cloud Run to find the app
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable with fallback
    port = int(os.environ.get("PORT", 9621))
    
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)