"""
Autonomous Relationship Engine

Automatically discovers and creates relationships between all entities.
Builds a comprehensive relationship graph for the entire system.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict

from logger import get_logger

logger = get_logger(__name__)


class RelationshipEngine:
    """
    Automatically discovers and manages relationships between entities
    
    Creates relationships based on:
    - Direct references (file_id, component_id, etc.)
    - Metadata patterns
    - Naming conventions
    - Temporal patterns
    - Structural hierarchies
    """
    
    def __init__(self):
        """Initialize Relationship Engine"""
        self.relationships: List[Dict[str, Any]] = []
        self.relationship_graph: Dict[str, List[str]] = defaultdict(list)
        self.entity_connections: Dict[str, Set[str]] = defaultdict(set)
        
        self.relationship_types = {
            "file_to_document": "generates",
            "document_to_chunk": "contains",
            "chunk_to_embedding": "has_embedding",
            "component_hierarchy": "contains",
            "file_to_component": "belongs_to",
            "server_to_storage_pool": "manages",
            "storage_pool_to_volume": "contains",
            "volume_to_backup": "stores",
            "backup_to_file": "includes",
            "metadata_reference": "references"
        }
        
        logger.info("Relationship Engine initialized")
    
    def build_relationships(
        self,
        entities: Dict[str, List[Any]],
        metadata: Dict[str, List[Dict[str, Any]]],
        mappings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build comprehensive relationship graph
        
        Args:
            entities: Discovered entities
            metadata: Extracted metadata
            mappings: Existing mappings
            
        Returns:
            Dictionary with relationship statistics
        """
        logger.info("Building relationship graph...")
        start_time = datetime.now()
        
        # Clear existing relationships
        self.relationships.clear()
        self.relationship_graph.clear()
        self.entity_connections.clear()
        
        # Build relationships from different sources
        self._build_from_mappings(mappings)
        self._build_from_metadata(metadata)
        self._build_from_entities(entities)
        self._build_hierarchical_relationships(entities)
        self._build_temporal_relationships(metadata)
        
        # Build graph structure
        self._build_graph()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        stats = {
            "total_relationships": len(self.relationships),
            "by_type": self._count_by_type(),
            "graph_nodes": len(self.relationship_graph),
            "highly_connected": self._find_highly_connected(top_n=10),
            "orphaned_entities": self._find_orphaned_entities(entities),
            "duration": duration
        }
        
        logger.info(f"Built {len(self.relationships)} relationships in {duration:.2f}s")
        
        return stats
    
    def _build_from_mappings(self, mappings: List[Dict[str, Any]]) -> None:
        """Build relationships from existing mappings"""
        for mapping in mappings:
            relationship = {
                "type": "file_to_component",
                "source_type": "file",
                "source_id": mapping.get("file_id"),
                "target_type": "component",
                "target_id": mapping.get("component_id"),
                "relationship": "mapped_to",
                "confidence": 1.0,
                "source": "mapping",
                "metadata": {
                    "mapping_id": mapping.get("id"),
                    "relationship_type": mapping.get("relationship_type"),
                    "created_at": mapping.get("created_at")
                }
            }
            self.relationships.append(relationship)
    
    def _build_from_metadata(self, metadata: Dict[str, List[Dict[str, Any]]]) -> None:
        """Build relationships from metadata"""
        # File to Document relationships
        for doc_meta in metadata.get("documents", []):
            source_file_id = doc_meta.get("source_file_id")
            if source_file_id:
                relationship = {
                    "type": "file_to_document",
                    "source_type": "file",
                    "source_id": source_file_id,
                    "target_type": "document",
                    "target_id": doc_meta.get("entity_id"),
                    "relationship": "generates",
                    "confidence": 1.0,
                    "source": "metadata",
                    "metadata": {
                        "chunk_count": doc_meta.get("chunk_count"),
                        "indexed_at": doc_meta.get("indexed_at")
                    }
                }
                self.relationships.append(relationship)
        
        # Component hierarchy relationships
        for comp_meta in metadata.get("components", []):
            parent_id = comp_meta.get("parent_id")
            if parent_id:
                relationship = {
                    "type": "component_hierarchy",
                    "source_type": "component",
                    "source_id": parent_id,
                    "target_type": "component",
                    "target_id": comp_meta.get("entity_id"),
                    "relationship": "contains",
                    "confidence": 1.0,
                    "source": "metadata",
                    "metadata": {
                        "component_type": comp_meta.get("component_type")
                    }
                }
                self.relationships.append(relationship)
    
    def _build_from_entities(self, entities: Dict[str, List[Any]]) -> None:
        """Build relationships from entity data"""
        # This would analyze entity properties to discover implicit relationships
        # For now, we'll use explicit references
        pass
    
    def _build_hierarchical_relationships(self, entities: Dict[str, List[Any]]) -> None:
        """Build hierarchical relationships (server -> pool -> volume -> backup)"""
        # This would build infrastructure hierarchy
        # Placeholder for future implementation
        pass
    
    def _build_temporal_relationships(self, metadata: Dict[str, List[Dict[str, Any]]]) -> None:
        """Build relationships based on temporal patterns"""
        # Group entities by creation time to find related entities
        # Placeholder for future implementation
        pass
    
    def _build_graph(self) -> None:
        """Build graph structure from relationships"""
        for rel in self.relationships:
            source_id = rel.get("source_id")
            target_id = rel.get("target_id")
            
            if source_id and target_id:
                # Add to graph
                self.relationship_graph[source_id].append(target_id)
                
                # Track connections
                self.entity_connections[source_id].add(target_id)
                self.entity_connections[target_id].add(source_id)
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count relationships by type"""
        counts = defaultdict(int)
        for rel in self.relationships:
            counts[rel.get("type", "unknown")] += 1
        return dict(counts)
    
    def _find_highly_connected(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Find most highly connected entities"""
        connections = [
            {"entity_id": entity_id, "connection_count": len(connections)}
            for entity_id, connections in self.entity_connections.items()
        ]
        connections.sort(key=lambda x: x["connection_count"], reverse=True)
        return connections[:top_n]
    
    def _find_orphaned_entities(self, entities: Dict[str, List[Any]]) -> List[str]:
        """Find entities with no relationships"""
        all_entity_ids = set()
        
        for entity_list in entities.values():
            for entity in entity_list:
                entity_id = entity.get("id")
                if entity_id:
                    all_entity_ids.add(entity_id)
        
        connected_ids = set(self.entity_connections.keys())
        orphaned = all_entity_ids - connected_ids
        
        return list(orphaned)
    
    def get_relationship_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5
    ) -> Optional[List[str]]:
        """
        Find shortest path between two entities
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            max_depth: Maximum search depth
            
        Returns:
            List of entity IDs forming the path, or None if no path found
        """
        if source_id == target_id:
            return [source_id]
        
        visited = set()
        queue = [(source_id, [source_id])]
        
        while queue:
            current_id, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            for neighbor_id in self.relationship_graph.get(current_id, []):
                if neighbor_id == target_id:
                    return path + [neighbor_id]
                
                if neighbor_id not in visited:
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return None
    
    def get_related_entities(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all entities related to a given entity
        
        Args:
            entity_id: Entity ID to find relationships for
            relationship_type: Optional filter by relationship type
            
        Returns:
            List of related entities with relationship details
        """
        related = []
        
        for rel in self.relationships:
            if rel.get("source_id") == entity_id:
                if relationship_type is None or rel.get("type") == relationship_type:
                    related.append({
                        "entity_id": rel.get("target_id"),
                        "entity_type": rel.get("target_type"),
                        "relationship": rel.get("relationship"),
                        "confidence": rel.get("confidence"),
                        "metadata": rel.get("metadata")
                    })
            elif rel.get("target_id") == entity_id:
                if relationship_type is None or rel.get("type") == relationship_type:
                    related.append({
                        "entity_id": rel.get("source_id"),
                        "entity_type": rel.get("source_type"),
                        "relationship": f"inverse_{rel.get('relationship')}",
                        "confidence": rel.get("confidence"),
                        "metadata": rel.get("metadata")
                    })
        
        return related
    
    def get_relationship_summary(self) -> Dict[str, Any]:
        """Get summary of relationship analysis"""
        return {
            "total_relationships": len(self.relationships),
            "relationship_types": list(self._count_by_type().keys()),
            "by_type": self._count_by_type(),
            "graph_nodes": len(self.relationship_graph),
            "total_connections": sum(len(v) for v in self.entity_connections.values()) // 2
        }

# Made with Bob
