from __future__ import annotations

import os
import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from neo4j import AsyncGraphDatabase, AsyncSession
from neo4j.exceptions import Neo4jError

from lightrag.base import BaseGraphStorage, StorageNameSpace
from lightrag.utils import EmbeddingFunc, logger
from lightrag.types import KnowledgeGraph, KnowledgeGraphNode, KnowledgeGraphEdge


@dataclass
class NamespacedNeo4jGraphStorage(BaseGraphStorage):
    """
    Neo4j graph storage adapter with built-in namespace isolation for multi-tenant deployment.
    
    This class extends BaseGraphStorage to enforce namespace isolation between users by:
    1. Prefixing all node labels with the user's namespace
    2. Prefixing all relationship types with the user's namespace
    3. Adding a namespace property to all nodes and relationships
    """
    
    # Neo4j connection parameters
    uri: str = field(default="bolt://localhost:7687")
    username: str = field(default="neo4j")
    password: str = field(default="password")
    database: str = field(default="neo4j")
    
    # Namespace for isolation (typically includes user_id)
    namespace_prefix: str = field(default="")
    
    # Connection pool settings
    max_connection_pool_size: int = field(default=50)
    
    # Default Neo4j labels and relationship types
    node_label: str = field(default="Entity")
    relationship_type: str = field(default="RELATED_TO")
    
    # Driver instance (initialized in initialize)
    _driver = None
    
    async def initialize(self):
        """Initialize the Neo4j connection"""
        await super().initialize()
        
        # Create Neo4j driver if not already initialized
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                max_connection_pool_size=self.max_connection_pool_size
            )
            
            # Ensure constraints and indexes exist
            await self._ensure_constraints()
            
            logger.info(f"Initialized Neo4j connection for namespace: {self.namespace}")
    
    async def _ensure_constraints(self):
        """Ensure necessary constraints and indexes exist in Neo4j"""
        # Create a prefixed label for namespace isolation
        ns_node_label = self._get_namespaced_label(self.node_label)
        
        async with self._driver.session(database=self.database) as session:
            # Create constraint for entity_id uniqueness within namespace
            try:
                query = f"""
                CREATE CONSTRAINT IF NOT EXISTS FOR (n:{ns_node_label})
                REQUIRE n.entity_id IS UNIQUE
                """
                await session.run(query)
                
                # Create index on namespace property
                query = f"""
                CREATE INDEX IF NOT EXISTS FOR (n:{ns_node_label})
                ON (n.namespace)
                """
                await session.run(query)
                
                logger.info(f"Created constraints and indexes for namespace: {self.namespace}")
            except Neo4jError as e:
                logger.warning(f"Error creating constraints: {str(e)}")
    
    async def finalize(self):
        """Close the Neo4j connection"""
        await super().finalize()
        if self._driver is not None:
            await self._driver.close()
            self._driver = None
            logger.info(f"Closed Neo4j connection for namespace: {self.namespace}")
    
    async def index_done_callback(self) -> None:
        """Commit the storage operations after indexing"""
        # Neo4j transactions are auto-committed, so nothing to do here
        pass
    
    async def drop(self) -> dict[str, str]:
        """Drop all data from this namespace's storage"""
        try:
            # Delete all nodes and relationships in this namespace
            async with self._driver.session(database=self.database) as session:
                # Get namespaced label
                ns_node_label = self._get_namespaced_label(self.node_label)
                
                # Delete all relationships first (to avoid constraint violations)
                query = f"""
                MATCH (n:{ns_node_label} {{namespace: $namespace}})-[r]-()
                DELETE r
                """
                await session.run(query, namespace=self.namespace)
                
                # Delete all nodes
                query = f"""
                MATCH (n:{ns_node_label} {{namespace: $namespace}})
                DELETE n
                """
                await session.run(query, namespace=self.namespace)
                
                logger.info(f"Dropped all data for namespace: {self.namespace}")
                return {"status": "success", "message": "data dropped"}
        except Exception as e:
            logger.error(f"Error dropping data: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _get_namespaced_label(self, label: str) -> str:
        """Get a label with the namespace prefix applied"""
        if not self.namespace_prefix:
            return label
        return f"{self.namespace_prefix}{label}"
    
    def _get_namespaced_relationship(self, rel_type: str) -> str:
        """Get a relationship type with the namespace prefix applied"""
        if not self.namespace_prefix:
            return rel_type
        return f"{self.namespace_prefix}{rel_type}"
    
    async def has_node(self, node_id: str) -> bool:
        """Check if a node exists in the graph with namespace isolation"""
        async with self._driver.session(database=self.database) as session:
            ns_node_label = self._get_namespaced_label(self.node_label)
            query = f"""
            MATCH (n:{ns_node_label} {{entity_id: $node_id, namespace: $namespace}})
            RETURN count(n) > 0 AS exists
            """
            result = await session.run(query, node_id=node_id, namespace=self.namespace)
            record = await result.single()
            return record and record["exists"]
    
    async def has_edge(self, source_node_id: str, target_node_id: str) -> bool:
        """Check if an edge exists between two nodes with namespace isolation"""
        async with self._driver.session(database=self.database) as session:
            ns_node_label = self._get_namespaced_label(self.node_label)
            ns_rel_type = self._get_namespaced_relationship(self.relationship_type)
            
            query = f"""
            MATCH (src:{ns_node_label} {{entity_id: $src_id, namespace: $namespace}})-[r:{ns_rel_type}]->(tgt:{ns_node_label} {{entity_id: $tgt_id, namespace: $namespace}})
            RETURN count(r) > 0 AS exists
            """
            result = await session.run(
                query, 
                src_id=source_node_id, 
                tgt_id=target_node_id, 
                namespace=self.namespace
            )
            record = await result.single()
            return record and record["exists"]
    
    async def node_degree(self, node_id: str) -> int:
        """Get the degree (number of connected edges) of a node"""
        async with self._driver.session(database=self.database) as session:
            ns_node_label = self._get_namespaced_label(self.node_label)
            
            query = f"""
            MATCH (n:{ns_node_label} {{entity_id: $node_id, namespace: $namespace}})-[r]-()
            RETURN count(r) AS degree
            """
            result = await session.run(query, node_id=node_id, namespace=self.namespace)
            record = await result.single()
            return record["degree"] if record else 0
    
    async def edge_degree(self, src_id: str, tgt_id: str) -> int:
        """Get the total degree of an edge (sum of degrees of its source and target nodes)"""
        src_degree, tgt_degree = await asyncio.gather(
            self.node_degree(src_id),
            self.node_degree(tgt_id)
        )
        return src_degree + tgt_degree
    
    async def get_node(self, node_id: str) -> dict[str, str] | None:
        """Get node by its ID, returning only node properties"""
        async with self._driver.session(database=self.database) as session:
            ns_node_label = self._get_namespaced_label(self.node_label)
            
            query = f"""
            MATCH (n:{ns_node_label} {{entity_id: $node_id, namespace: $namespace}})
            RETURN properties(n) AS props
            """
            result = await session.run(query, node_id=node_id, namespace=self.namespace)
            record = await result.single()
            
            if not record:
                return None
                
            # Remove internal namespace property
            props = record["props"]
            if "namespace" in props:
                del props["namespace"]
                
            return props
    
    async def get_edge(self, source_node_id: str, target_node_id: str) -> dict[str, str] | None:
        """Get edge properties between two nodes"""
        async with self._driver.session(database=self.database) as session:
            ns_node_label = self._get_namespaced_label(self.node_label)
            ns_rel_type = self._get_namespaced_relationship(self.relationship_type)
            
            query = f"""
            MATCH (src:{ns_node_label} {{entity_id: $src_id, namespace: $namespace}})-[r:{ns_rel_type}]->(tgt:{ns_node_label} {{entity_id: $tgt_id, namespace: $namespace}})
            RETURN properties(r) AS props
            """
            result = await session.run(
                query, 
                src_id=source_node_id, 
                tgt_id=target_node_id, 
                namespace=self.namespace
            )
            record = await result.single()
            
            if not record:
                return None
                
            # Remove internal namespace property
            props = record["props"]
            if "namespace" in props:
                del props["namespace"]
                
            return props
    
    async def get_node_edges(self, source_node_id: str) -> list[tuple[str, str]] | None:
        """Get all edges connected to a node"""
        # Check if node exists
        if not await self.has_node(source_node_id):
            return None
            
        async with self._driver.session(database=self.database) as session:
            ns_node_label = self._get_namespaced_label(self.node_label)
            
            # Get outgoing edges
            query = f"""
            MATCH (src:{ns_node_label} {{entity_id: $node_id, namespace: $namespace}})-[r]->(tgt:{ns_node_label} {{namespace: $namespace}})
            RETURN src.entity_id AS source, tgt.entity_id AS target
            """
            result = await session.run(query, node_id=source_node_id, namespace=self.namespace)
            outgoing = [(record["source"], record["target"]) async for record in result]
            
            # Get incoming edges
            query = f"""
            MATCH (src:{ns_node_label} {{namespace: $namespace}})-[r]->(tgt:{ns_node_label} {{entity_id: $node_id, namespace: $namespace}})
            RETURN src.entity_id AS source, tgt.entity_id AS target
            """
            result = await session.run(query, node_id=source_node_id, namespace=self.namespace)
            incoming = [(record["source"], record["target"]) async for record in result]
            
            return outgoing + incoming
    
    async def upsert_node(self, node_id: str, node_data: dict[str, str]) -> None:
        """Insert a new node or update an existing node in the graph with namespace isolation"""
        async with self._driver.session(database=self.database) as session:
            ns_node_label = self._get_namespaced_label(self.node_label)
            
            # Add namespace to properties
            properties = {**node_data, "namespace": self.namespace, "entity_id": node_id}
            
            # Create or update node
            query = f"""
            MERGE (n:{ns_node_label} {{entity_id: $entity_id, namespace: $namespace}})
            SET n = $properties
            """
            await session.run(query, entity_id=node_id, namespace=self.namespace, properties=properties)
    
    async def upsert_edge(self, source_node_id: str, target_node_id: str, edge_data: dict[str, str]) -> None:
        """Insert a new edge or update an existing edge in the graph with namespace isolation"""
        async with self._driver.session(database=self.database) as session:
            ns_node_label = self._get_namespaced_label(self.node_label)
            ns_rel_type = self._get_namespaced_relationship(self.relationship_type)
            
            # Add namespace to edge properties
            properties = {**edge_data, "namespace": self.namespace}
            
            # Create or update edge
            query = f"""
            MATCH (src:{ns_node_label} {{entity_id: $src_id, namespace: $namespace}})
            MATCH (tgt:{ns_node_label} {{entity_id: $tgt_id, namespace: $namespace}})
            MERGE (src)-[r:{ns_rel_type}]->(tgt)
            SET r = $properties
            """
            await session.run(
                query, 
                src_id=source_node_id, 
                tgt_id=target_node_id, 
                namespace=self.namespace,
                properties=properties
            )
    
    async def delete_node(self, node_id: str) -> None:
        """Delete a node from the graph with namespace isolation"""
        async with self._driver.session(database=self.database) as session:
            ns_node_label = self._get_namespaced_label(self.node_label)
            
            # First delete all relationships
            query = f"""
            MATCH (n:{ns_node_label} {{entity_id: $node_id, namespace: $namespace}})-[r]-()
            DELETE r
            """
            await session.run(query, node_id=node_id, namespace=self.namespace)
            
            # Then delete the node
            query = f"""
            MATCH (n:{ns_node_label} {{entity_id: $node_id, namespace: $namespace}})
            DELETE n
            """
            await session.run(query, node_id=node_id, namespace=self.namespace)
    
    async def remove_nodes(self, nodes: list[str]):
        """Delete multiple nodes with namespace isolation"""
        async with self._driver.session(database=self.database) as session:
            ns_node_label = self._get_namespaced_label(self.node_label)
            
            # First delete all relationships
            query = f"""
            MATCH (n:{ns_node_label} {{namespace: $namespace}})-[r]-()
            WHERE n.entity_id IN $node_ids
            DELETE r
            """
            await session.run(query, node_ids=nodes, namespace=self.namespace)
            
            # Then delete the nodes
            query = f"""
            MATCH (n:{ns_node_label} {{namespace: $namespace}})
            WHERE n.entity_id IN $node_ids
            DELETE n
            """
            await session.run(query, node_ids=nodes, namespace=self.namespace)
    
    async def remove_edges(self, edges: list[tuple[str, str]]):
        """Delete multiple edges with namespace isolation"""
        async with self._driver.session(database=self.database) as session:
            ns_node_label = self._get_namespaced_label(self.node_label)
            ns_rel_type = self._get_namespaced_relationship(self.relationship_type)
            
            # Build parameters for query
            params = {
                "edges": [{"src": src, "tgt": tgt} for src, tgt in edges],
                "namespace": self.namespace
            }
            
            # Delete relationships
            query = f"""
            UNWIND $edges AS edge
            MATCH (src:{ns_node_label} {{entity_id: edge.src, namespace: $namespace}})-[r:{ns_rel_type}]->(tgt:{ns_node_label} {{entity_id: edge.tgt, namespace: $namespace}})
            DELETE r
            """
            await session.run(query, **params)
    
    async def get_all_labels(self) -> list[str]:
        """Get all entity IDs in the graph for this namespace"""
        async with self._driver.session(database=self.database) as session:
            ns_node_label = self._get_namespaced_label(self.node_label)
            
            query = f"""
            MATCH (n:{ns_node_label} {{namespace: $namespace}})
            RETURN n.entity_id AS entity_id
            ORDER BY entity_id
            """
            result = await session.run(query, namespace=self.namespace)
            return [record["entity_id"] async for record in result]
    
    async def get_knowledge_graph(
        self, 
        node_label: str, 
        max_depth: int = 3, 
        max_nodes: int = 1000
    ) -> KnowledgeGraph:
        """Retrieve a connected subgraph with namespace isolation"""
        async with self._driver.session(database=self.database) as session:
            ns_node_label = self._get_namespaced_label(self.node_label)
            
            # Build query based on whether we want a specific label or all nodes
            if node_label == "*":
                # Get all nodes in namespace
                match_clause = f"MATCH (n:{ns_node_label} {{namespace: $namespace}})"
            else:
                # Get nodes that match the label (can be partial match)
                match_clause = f"MATCH (n:{ns_node_label} {{namespace: $namespace}}) WHERE n.entity_id CONTAINS $label"
            
            # Query for nodes and their relationships up to max_depth
            query = f"""
            {match_clause}
            CALL apoc.path.subgraphAll(n, {{maxLevel: $max_depth, limit: $max_nodes}})
            YIELD nodes, relationships
            RETURN 
                [node in nodes | {{
                    id: node.entity_id,
                    properties: apoc.map.removeKeys(node, ['namespace'])
                }}] AS graph_nodes,
                [rel in relationships | {{
                    source: startNode(rel).entity_id,
                    target: endNode(rel).entity_id,
                    properties: apoc.map.removeKeys(rel, ['namespace'])
                }}] AS graph_edges,
                size(nodes) > $max_nodes AS is_truncated
            """
            
            try:
                result = await session.run(
                    query, 
                    namespace=self.namespace,
                    label=node_label,
                    max_depth=max_depth,
                    max_nodes=max_nodes
                )
                record = await result.single()
                
                if not record:
                    # Return empty graph
                    return KnowledgeGraph(nodes=[], edges=[], is_truncated=False)
                
                # Convert to KnowledgeGraph format
                nodes = [
                    KnowledgeGraphNode(
                        id=node["id"],
                        labels=[self.node_label],
                        properties=node["properties"]
                    )
                    for node in record["graph_nodes"]
                ]
                
                edges = [
                    KnowledgeGraphEdge(
                        id=f"{edge['source']}_{edge['target']}",
                        type=self.relationship_type,
                        source=edge["source"],
                        target=edge["target"],
                        properties=edge["properties"]
                    )
                    for edge in record["graph_edges"]
                ]
                
                return KnowledgeGraph(
                    nodes=nodes,
                    edges=edges,
                    is_truncated=record["is_truncated"]
                )
                
            except Exception as e:
                logger.error(f"Error retrieving knowledge graph: {str(e)}")
                # Return empty graph in case of error
                return KnowledgeGraph(nodes=[], edges=[], is_truncated=False)