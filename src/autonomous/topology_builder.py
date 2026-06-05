"""
Autonomous Topology Graph Builder

Automatically builds and maintains a live topology graph of the entire system.
Creates hierarchical representations and tracks topology changes over time.
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from collections import defaultdict
import json

from logger import get_logger

logger = get_logger(__name__)


class TopologyNode:
    """Represents a node in the topology graph"""
    
    def __init__(
        self,
        node_id: str,
        node_type: str,
        name: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.name = name
        self.properties = properties or {}
        self.children: List[str] = []
        self.parent: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary"""
        return {
            "id": self.node_id,
            "type": self.node_type,
            "name": self.name,
            "properties": self.properties,
            "children": self.children,
            "parent": self.parent,
            "metadata": self.metadata
        }


class TopologyGraphBuilder:
    """
    Automatically builds and maintains topology graphs
    
    Creates hierarchical topology representations from:
    - Discovered entities
    - Relationships
    - Metadata
    - Component hierarchies
    """
    
    def __init__(self):
        """Initialize Topology Graph Builder"""
        self.nodes: Dict[str, TopologyNode] = {}
        self.root_nodes: List[str] = []
        self.topology_layers: Dict[str, List[str]] = defaultdict(list)
        
        self.node_type_hierarchy = [
            "server",
            "storage_pool",
            "volume",
            "backup_object",
            "file",
            "document",
            "chunk",
            "embedding"
        ]
        
        logger.info("Topology Graph Builder initialized")
    
    def build_topology(
        self,
        entities: Dict[str, List[Any]],
        relationships: List[Dict[str, Any]],
        metadata: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Build complete topology graph
        
        Args:
            entities: Discovered entities
            relationships: Discovered relationships
            metadata: Extracted metadata
            
        Returns:
            Dictionary with topology statistics
        """
        logger.info("Building topology graph...")
        start_time = datetime.now()
        
        # Clear existing topology
        self.nodes.clear()
        self.root_nodes.clear()
        self.topology_layers.clear()
        
        # Create nodes from entities
        self._create_nodes_from_entities(entities, metadata)
        
        # Build hierarchy from relationships
        self._build_hierarchy_from_relationships(relationships)
        
        # Identify root nodes
        self._identify_root_nodes()
        
        # Organize into layers
        self._organize_layers()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        stats = {
            "total_nodes": len(self.nodes),
            "root_nodes": len(self.root_nodes),
            "layers": len(self.topology_layers),
            "by_type": self._count_by_type(),
            "max_depth": self._calculate_max_depth(),
            "duration": duration
        }
        
        logger.info(f"Built topology with {len(self.nodes)} nodes in {duration:.2f}s")
        
        return stats
    
    def _create_nodes_from_entities(
        self,
        entities: Dict[str, List[Any]],
        metadata: Dict[str, List[Dict[str, Any]]]
    ) -> None:
        """Create topology nodes from entities"""
        # Create nodes from files
        for file_entity in entities.get("files", []):
            node = TopologyNode(
                node_id=f"file_{file_entity.get('id')}",
                node_type="file",
                name=file_entity.get("name", "Unknown"),
                properties={
                    "size": file_entity.get("size"),
                    "file_type": file_entity.get("file_type"),
                    "path": file_entity.get("path")
                }
            )
            self.nodes[node.node_id] = node
            self.topology_layers["file"].append(node.node_id)
        
        # Create nodes from documents
        for doc_entity in entities.get("documents", []):
            node = TopologyNode(
                node_id=f"document_{doc_entity.get('id')}",
                node_type="document",
                name=doc_entity.get("title", "Unknown"),
                properties={
                    "content_type": doc_entity.get("content_type"),
                    "chunk_count": doc_entity.get("chunk_count")
                }
            )
            self.nodes[node.node_id] = node
            self.topology_layers["document"].append(node.node_id)
        
        # Create nodes from components
        for comp_entity in entities.get("components", []):
            node = TopologyNode(
                node_id=f"component_{comp_entity.get('id')}",
                node_type="component",
                name=comp_entity.get("name", "Unknown"),
                properties={
                    "component_type": comp_entity.get("type"),
                    "properties": comp_entity.get("properties", {})
                }
            )
            self.nodes[node.node_id] = node
            self.topology_layers["component"].append(node.node_id)
        
        # Create nodes from topology nodes
        for topo_node in entities.get("topology_nodes", []):
            node = TopologyNode(
                node_id=f"topology_{topo_node.get('id')}",
                node_type=topo_node.get("type", "unknown"),
                name=topo_node.get("name", "Unknown"),
                properties=topo_node.get("properties", {})
            )
            self.nodes[node.node_id] = node
            node_type = topo_node.get("type", "unknown")
            self.topology_layers[node_type].append(node.node_id)
    
    def _build_hierarchy_from_relationships(
        self,
        relationships: List[Dict[str, Any]]
    ) -> None:
        """Build parent-child hierarchy from relationships"""
        for rel in relationships:
            if rel.get("relationship") in ["contains", "has", "includes"]:
                source_type = rel.get("source_type")
                target_type = rel.get("target_type")
                
                if source_type and target_type:
                    source_id = self._normalize_id(rel.get("source_id"), source_type)
                    target_id = self._normalize_id(rel.get("target_id"), target_type)
                    
                    if source_id in self.nodes and target_id in self.nodes:
                        # Set parent-child relationship
                        self.nodes[source_id].children.append(target_id)
                        self.nodes[target_id].parent = source_id
    
    def _normalize_id(self, entity_id: Any, entity_type: str) -> str:
        """Normalize entity ID to topology node ID"""
        if not entity_id:
            return ""
        return f"{entity_type}_{entity_id}"
    
    def _identify_root_nodes(self) -> None:
        """Identify root nodes (nodes with no parent)"""
        self.root_nodes = [
            node_id for node_id, node in self.nodes.items()
            if node.parent is None
        ]
        logger.info(f"Identified {len(self.root_nodes)} root nodes")
    
    def _organize_layers(self) -> None:
        """Organize nodes into hierarchical layers"""
        # Already organized by type during node creation
        pass
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count nodes by type"""
        counts = defaultdict(int)
        for node in self.nodes.values():
            counts[node.node_type] += 1
        return dict(counts)
    
    def _calculate_max_depth(self) -> int:
        """Calculate maximum depth of topology tree"""
        max_depth = 0
        
        for root_id in self.root_nodes:
            depth = self._calculate_node_depth(root_id)
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _calculate_node_depth(self, node_id: str, current_depth: int = 0) -> int:
        """Calculate depth of a node's subtree"""
        node = self.nodes.get(node_id)
        if not node or not node.children:
            return current_depth
        
        max_child_depth = current_depth
        for child_id in node.children:
            child_depth = self._calculate_node_depth(child_id, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    def get_topology_tree(self, root_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get topology as a tree structure
        
        Args:
            root_id: Optional root node ID. If None, returns all root nodes
            
        Returns:
            Dictionary representing the topology tree
        """
        if root_id:
            return self._build_tree(root_id)
        else:
            return {
                "roots": [self._build_tree(rid) for rid in self.root_nodes]
            }
    
    def _build_tree(self, node_id: str) -> Dict[str, Any]:
        """Recursively build tree structure"""
        node = self.nodes.get(node_id)
        if not node:
            return {}
        
        tree = node.to_dict()
        tree["children"] = [
            self._build_tree(child_id) for child_id in node.children
        ]
        
        return tree
    
    def get_node_path(self, node_id: str) -> List[str]:
        """
        Get path from root to node
        
        Args:
            node_id: Node ID
            
        Returns:
            List of node IDs from root to target node
        """
        path = []
        current_id = node_id
        
        while current_id:
            path.insert(0, current_id)
            node = self.nodes.get(current_id)
            if not node:
                break
            current_id = node.parent
        
        return path
    
    def find_nodes_by_type(self, node_type: str) -> List[Dict[str, Any]]:
        """
        Find all nodes of a specific type
        
        Args:
            node_type: Type of nodes to find
            
        Returns:
            List of nodes matching the type
        """
        return [
            node.to_dict() for node in self.nodes.values()
            if node.node_type == node_type
        ]
    
    def get_topology_summary(self) -> Dict[str, Any]:
        """Get summary of topology"""
        return {
            "total_nodes": len(self.nodes),
            "root_nodes": len(self.root_nodes),
            "by_type": self._count_by_type(),
            "layers": {k: len(v) for k, v in self.topology_layers.items()},
            "max_depth": self._calculate_max_depth()
        }
    
    def export_topology(self, filepath: str) -> None:
        """
        Export topology to JSON file
        
        Args:
            filepath: Path to save topology
        """
        topology_data = {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "root_nodes": self.root_nodes,
            "layers": {k: list(v) for k, v in self.topology_layers.items()},
            "summary": self.get_topology_summary(),
            "exported_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(topology_data, f, indent=2)
        
        logger.info(f"Exported topology to {filepath}")

# Made with Bob
