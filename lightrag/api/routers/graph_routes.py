"""
This module contains all graph-related routes for the LightRAG API.
"""

from typing import Optional, Dict, Any
import traceback
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from pydantic import BaseModel

from lightrag.utils import logger
from ..utils_api import get_combined_auth_dependency, extract_user_id
from ..user_rag_manager import get_manager

router = APIRouter(tags=["graph"])


class EntityUpdateRequest(BaseModel):
    entity_name: str
    updated_data: Dict[str, Any]
    allow_rename: bool = False


class RelationUpdateRequest(BaseModel):
    source_id: str
    target_id: str
    updated_data: Dict[str, Any]


def create_graph_routes(rag, api_key: Optional[str] = None):
    combined_auth = get_combined_auth_dependency(api_key)
    
    # Import the RAG manager and user ID extractor
    from lightrag.api.user_rag_manager import get_manager
    from lightrag.api.utils_api import extract_user_id

    @router.get("/graph/label/list", dependencies=[Depends(combined_auth)])
    async def get_graph_labels(request: Request):
        """
        Get all graph labels

        Args:
            request: The FastAPI request object
            
        Returns:
            List[str]: List of graph labels
        """
        try:
            # Get user ID
            user_id = None
            try:
                user_id = extract_user_id(request)
            except HTTPException:
                logger.warning("No valid user ID provided, using system-wide storage")
            
            # Get user-specific RAG instance if user_id is available
            user_rag = rag
            if user_id:
                user_rag = await get_manager().get_instance(user_id)
                logger.info(f"Getting graph labels for user: {user_id}")
                
            return await user_rag.get_graph_labels()
        except Exception as e:
            logger.error(f"Error getting graph labels: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Error getting graph labels: {str(e)}"
            )

    @router.get("/graphs", dependencies=[Depends(combined_auth)])
    async def get_knowledge_graph(
        request: Request,
        label: str = Query(..., description="Label to get knowledge graph for"),
        max_depth: int = Query(3, description="Maximum depth of graph", ge=1),
        max_nodes: int = Query(1000, description="Maximum nodes to return", ge=1),
    ):
        """
        Retrieve a connected subgraph of nodes where the label includes the specified label.
        When reducing the number of nodes, the prioritization criteria are as follows:
            1. Hops(path) to the staring node take precedence
            2. Followed by the degree of the nodes

        Args:
            request: The FastAPI request object
            label (str): Label of the starting node
            max_depth (int, optional): Maximum depth of the subgraph,Defaults to 3
            max_nodes: Maxiumu nodes to return

        Returns:
            Dict[str, List[str]]: Knowledge graph for label
        """
        try:
            # Get user ID
            user_id = None
            try:
                user_id = extract_user_id(request)
            except HTTPException:
                logger.warning("No valid user ID provided, using system-wide storage")
            
            # Get user-specific RAG instance if user_id is available
            user_rag = rag
            if user_id:
                user_rag = await get_manager().get_instance(user_id)
                logger.info(f"Getting knowledge graph for user: {user_id}, label: {label}")
                
            return await user_rag.get_knowledge_graph(
                node_label=label,
                max_depth=max_depth,
                max_nodes=max_nodes,
            )
        except Exception as e:
            logger.error(f"Error getting knowledge graph for label '{label}': {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Error getting knowledge graph: {str(e)}"
            )

    @router.get("/graph/entity/exists", dependencies=[Depends(combined_auth)])
    async def check_entity_exists(
        request: Request,
        name: str = Query(..., description="Entity name to check"),
    ):
        """
        Check if an entity with the given name exists in the knowledge graph

        Args:
            request: The FastAPI request object
            name (str): Name of the entity to check

        Returns:
            Dict[str, bool]: Dictionary with 'exists' key indicating if entity exists
        """
        try:
            # Get user ID
            user_id = None
            try:
                user_id = extract_user_id(request)
            except HTTPException:
                logger.warning("No valid user ID provided, using system-wide storage")
            
            # Get user-specific RAG instance if user_id is available
            user_rag = rag
            if user_id:
                user_rag = await get_manager().get_instance(user_id)
                logger.info(f"Checking entity existence for user: {user_id}, entity: {name}")
                
            exists = await user_rag.chunk_entity_relation_graph.has_node(name)
            return {"exists": exists}
        except Exception as e:
            logger.error(f"Error checking entity existence for '{name}': {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Error checking entity existence: {str(e)}"
            )

    @router.post("/graph/entity/edit", dependencies=[Depends(combined_auth)])
    async def update_entity(request: Request, entity_request: EntityUpdateRequest):
        """
        Update an entity's properties in the knowledge graph

        Args:
            request: The FastAPI request object
            entity_request (EntityUpdateRequest): Request containing entity name, updated data, and rename flag

        Returns:
            Dict: Updated entity information
        """
        try:
            # Get user ID
            user_id = None
            try:
                user_id = extract_user_id(request)
            except HTTPException:
                logger.warning("No valid user ID provided")
                raise HTTPException(status_code=400, detail="No valid user ID provided")
            
            # Get user-specific RAG instance if user_id is available
            user_rag = rag
            if user_id:
                user_rag = await get_manager().get_instance(user_id)
                logger.info(f"Updating entity for user: {user_id}, entity: {entity_request.entity_name}")
                
            result = await user_rag.aedit_entity(
                entity_name=entity_request.entity_name,
                updated_data=entity_request.updated_data,
                allow_rename=entity_request.allow_rename,
            )
            return {
                "status": "success",
                "message": "Entity updated successfully",
                "data": result,
            }
        except ValueError as ve:
            logger.error(
                f"Validation error updating entity '{entity_request.entity_name}': {str(ve)}"
            )
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            logger.error(f"Error updating entity '{entity_request.entity_name}': {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Error updating entity: {str(e)}"
            )

    @router.post("/graph/relation/edit", dependencies=[Depends(combined_auth)])
    async def update_relation(request: Request, relation_request: RelationUpdateRequest):
        """Update a relation's properties in the knowledge graph

        Args:
            request: The FastAPI request object
            relation_request (RelationUpdateRequest): Request containing source ID, target ID and updated data

        Returns:
            Dict: Updated relation information
        """
        try:
            # Get user ID
            user_id = None
            try:
                user_id = extract_user_id(request)
            except HTTPException:
                logger.warning("No valid user ID provided")
                raise HTTPException(status_code=400, detail="No valid user ID provided")
            
            # Get user-specific RAG instance if user_id is available
            user_rag = rag
            if user_id:
                user_rag = await get_manager().get_instance(user_id)
                logger.info(f"Updating relation for user: {user_id}, relation: {relation_request.source_id} -> {relation_request.target_id}")
                
            result = await user_rag.aedit_relation(
                source_entity=relation_request.source_id,
                target_entity=relation_request.target_id,
                updated_data=relation_request.updated_data,
            )
            return {
                "status": "success",
                "message": "Relation updated successfully",
                "data": result,
            }
        except ValueError as ve:
            logger.error(
                f"Validation error updating relation between '{relation_request.source_id}' and '{relation_request.target_id}': {str(ve)}"
            )
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            logger.error(
                f"Error updating relation between '{relation_request.source_id}' and '{relation_request.target_id}': {str(e)}"
            )
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Error updating relation: {str(e)}"
            )

    @router.post("/graph/relation/edit", dependencies=[Depends(combined_auth)])
    async def update_relation(request: RelationUpdateRequest):
        """Update a relation's properties in the knowledge graph

        Args:
            request (RelationUpdateRequest): Request containing source ID, target ID and updated data

        Returns:
            Dict: Updated relation information
        """
        try:
            result = await rag.aedit_relation(
                source_entity=request.source_id,
                target_entity=request.target_id,
                updated_data=request.updated_data,
            )
            return {
                "status": "success",
                "message": "Relation updated successfully",
                "data": result,
            }
        except ValueError as ve:
            logger.error(
                f"Validation error updating relation between '{request.source_id}' and '{request.target_id}': {str(ve)}"
            )
            raise HTTPException(status_code=400, detail=str(ve))
        except Exception as e:
            logger.error(
                f"Error updating relation between '{request.source_id}' and '{request.target_id}': {str(e)}"
            )
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500, detail=f"Error updating relation: {str(e)}"
            )

    return router