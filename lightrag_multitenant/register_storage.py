from lightrag.kg import STORAGES

def register_storages():
    """
    Register custom storage implementations with LightRAG.
    This needs to be called before initializing LightRAG instances.
    """
    # Register NamespacedNeo4jGraphStorage
    STORAGES["NamespacedNeo4jGraphStorage"] = "namespaced_neo4j_storage.NamespacedNeo4jGraphStorage"
    
    # Log registration
    from lightrag.utils import logger
    logger.info("Registered custom NamespacedNeo4jGraphStorage for multi-tenant isolation")