from fastapi import Depends, HTTPException, status, Query
from typing import Annotated, Optional

from lightrag_manager import LightRAGManager
from namespaced_lightrag import NamespacedLightRAG

# Initialize the manager (should be done at application startup)
tenant_manager = LightRAGManager()

class TenantContext:
    """Context object containing user and tenant information"""
    def __init__(self, user_id: str, lightrag: NamespacedLightRAG):
        self.user_id = user_id
        self.lightrag = lightrag
        
    @property
    def namespace(self) -> str:
        """Get the namespace for this tenant"""
        return f"user_{self.user_id}_"

async def get_tenant_context(
    user_id: str = Query(..., description="User ID for tenant isolation")
) -> TenantContext:
    """
    Get tenant context from user_id parameter.
    This simplifies integration by not requiring authentication logic.
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id parameter is required"
        )
    
    # Simple validation to prevent dangerous user_ids
    if not user_id.isalnum() and not "_" in user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id format. Use only alphanumeric characters and underscores."
        )
    
    # Get the LightRAG instance for this user from tenant manager
    try:
        lightrag_instance = tenant_manager.get_instance(user_id)
        
        # Return tenant context with user info and LightRAG instance
        return TenantContext(user_id=user_id, lightrag=lightrag_instance)
    except Exception as e:
        # Handle errors when creating or retrieving tenant instance
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating tenant context: {str(e)}"
        )

# Type alias for dependency injection
TenantDepends = Annotated[TenantContext, Depends(get_tenant_context)]