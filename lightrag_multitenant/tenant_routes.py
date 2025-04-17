from fastapi import APIRouter, HTTPException, status, Depends, Body
from typing import Dict, Any, List, Optional

from lightrag import QueryParam
from tenant_auth_middleware import TenantDepends

# Create tenant-specific router
router = APIRouter(prefix="/tenant", tags=["Multi-Tenant Operations"])

@router.post("/documents/insert")
async def tenant_insert_document(
    tenant: TenantDepends,
    document: str = Body(..., description="Document content to insert"),
    split_by_character: Optional[str] = Body(None, description="Character to split document by"),
    split_by_character_only: bool = Body(False, description="Split only by character"),
    doc_id: Optional[str] = Body(None, description="Optional document ID"),
    file_path: Optional[str] = Body(None, description="Optional file path")
):
    """Insert a document for the current tenant"""
    try:
        # Use the tenant's LightRAG instance to perform the operation
        await tenant.lightrag.ainsert(
            document,
            split_by_character=split_by_character,
            split_by_character_only=split_by_character_only,
            ids=doc_id,
            file_paths=file_path
        )
        
        return {
            "status": "success",
            "message": "Document inserted successfully",
            "tenant_id": tenant.user_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to insert document: {str(e)}"
        )

@router.post("/documents/query")
async def tenant_query_documents(
    tenant: TenantDepends,
    query: str = Body(..., description="Query to execute"),
    params: Dict[str, Any] = Body({}, description="Query parameters"),
    system_prompt: Optional[str] = Body(None, description="Optional system prompt")
):
    """Query documents for the current tenant"""
    try:
        # Convert params dict to QueryParam
        query_param = QueryParam(**params)
        
        # Use the tenant's LightRAG instance to perform the operation
        result = await tenant.lightrag.aquery(
            query, 
            param=query_param,
            system_prompt=system_prompt
        )
        
        return {
            "status": "success",
            "result": result,
            "tenant_id": tenant.user_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute query: {str(e)}"
        )

@router.get("/status")
async def tenant_status(tenant: TenantDepends):
    """Get status information for the current tenant"""
    try:
        # Get document processing status
        processing_status = await tenant.lightrag.get_processing_status()
        
        # Get knowledge graph labels
        graph_labels = await tenant.lightrag.get_graph_labels()
        
        return {
            "status": "success",
            "tenant_id": tenant.user_id,
            "namespace": tenant.namespace,
            "processing_status": processing_status,
            "graph_labels": graph_labels,
            "working_dir": tenant.lightrag.working_dir
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tenant status: {str(e)}"
        )

@router.delete("/data")
async def tenant_delete_data(tenant: TenantDepends):
    """Delete all data for the current tenant"""
    try:
        # Drop all data for this tenant (implementation-specific)
        drop_result = await tenant.lightrag.chunk_entity_relation_graph.drop()
        
        # Reinitialize storages
        await tenant.lightrag.initialize_storages()
        
        return {
            "status": "success",
            "message": "All tenant data deleted successfully",
            "tenant_id": tenant.user_id,
            "drop_result": drop_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tenant data: {str(e)}"
        )