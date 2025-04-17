from fastapi import Depends, HTTPException, status, Request
from typing import Annotated, Optional

from lightrag.api.auth import auth_handler
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
    request: Request, 
    authorization: Optional[str] = None,
) -> TenantContext:
    """
    Extract token from request and get tenant context.
    This works with the existing auth system to provide multi-tenancy.
    """
    # Get token from Authorization header
    if not authorization:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        # Format: "Bearer {token}"
        authorization = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    try:
        # Validate token with existing auth handler
        user_info = auth_handler.validate_token(authorization)
        
        # Extract user_id (username) from validated token
        user_id = user_info.get("username")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user identification in token"
            )
        
        # Handle guest user specially if needed
        if user_info.get("role") == "guest":
            # Option 1: Use a shared guest space
            user_id = "guest"
            # Option 2: Reject guest users if you want to enforce authentication
            # raise HTTPException(
            #     status_code=status.HTTP_403_FORBIDDEN,
            #     detail="Guest users cannot access tenant-specific operations"
            # )
        
        # Get the LightRAG instance for this user from tenant manager
        lightrag_instance = tenant_manager.get_instance(user_id)
        
        # Return tenant context with user info and LightRAG instance
        return TenantContext(user_id=user_id, lightrag=lightrag_instance)
        
    except HTTPException:
        # Re-raise HTTP exceptions from auth_handler
        raise
    except Exception as e:
        # Handle other exceptions
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}"
        )

# Type alias for dependency injection
TenantDepends = Annotated[TenantContext, Depends(get_tenant_context)]