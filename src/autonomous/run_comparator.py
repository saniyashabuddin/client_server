"""
Run Comparator

Compares current run with previous runs to detect changes, additions, deletions,
and modifications in the system state.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
import json
from pathlib import Path

from logger import get_logger

logger = get_logger(__name__)


class RunComparator:
    """
    Compares runs to detect changes
    
    Detects:
    - New entities added
    - Entities removed
    - Entities modified
    - Relationship changes
    - Metadata changes
    - Topology changes
    """
    
    def __init__(self, runs_dir: str = "runs"):
        """Initialize Run Comparator"""
        self.runs_dir = Path(runs_dir)
        logger.info("Run Comparator initialized")
    
    def compare_runs(
        self,
        current_run_id: str,
        previous_run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare current run with previous run
        
        Args:
            current_run_id: Current run ID
            previous_run_id: Previous run ID (if None, uses most recent)
            
        Returns:
            Dictionary with comparison results
        """
        logger.info(f"Comparing runs: {current_run_id} vs {previous_run_id or 'latest'}")
        
        # Load current run data
        current_data = self._load_run_data(current_run_id)
        if not current_data:
            logger.error(f"Could not load current run data: {current_run_id}")
            return {"error": "Current run data not found"}
        
        # Load previous run data
        if not previous_run_id:
            previous_run_id = self._get_previous_run_id(current_run_id)
        
        if not previous_run_id:
            logger.info("No previous run found for comparison")
            return {
                "comparison_type": "baseline",
                "message": "This is the first run, no comparison available"
            }
        
        previous_data = self._load_run_data(previous_run_id)
        if not previous_data:
            logger.error(f"Could not load previous run data: {previous_run_id}")
            return {"error": "Previous run data not found"}
        
        # Perform comparison
        comparison = {
            "current_run_id": current_run_id,
            "previous_run_id": previous_run_id,
            "compared_at": datetime.now().isoformat(),
            "entities": self._compare_entities(
                current_data.get("entities", {}),
                previous_data.get("entities", {})
            ),
            "relationships": self._compare_relationships(
                current_data.get("relationships", []),
                previous_data.get("relationships", [])
            ),
            "metadata": self._compare_metadata(
                current_data.get("metadata", {}),
                previous_data.get("metadata", {})
            ),
            "topology": self._compare_topology(
                current_data.get("topology", {}),
                previous_data.get("topology", {})
            ),
            "summary": {}
        }
        
        # Generate summary
        comparison["summary"] = self._generate_comparison_summary(comparison)
        
        logger.info(f"Comparison complete: {comparison['summary']['total_changes']} changes detected")
        
        return comparison
    
    def _load_run_data(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Load run data from file"""
        run_file = self.runs_dir / run_id / "run_data.json"
        
        if not run_file.exists():
            return None
        
        try:
            with open(run_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading run data: {e}")
            return None
    
    def _get_previous_run_id(self, current_run_id: str) -> Optional[str]:
        """Get the most recent run ID before current run"""
        if not self.runs_dir.exists():
            return None
        
        # Get all run directories
        run_dirs = [d for d in self.runs_dir.iterdir() if d.is_dir()]
        
        # Sort by name (which includes date)
        run_dirs.sort()
        
        # Find current run and return previous
        try:
            current_index = [d.name for d in run_dirs].index(current_run_id)
            if current_index > 0:
                return run_dirs[current_index - 1].name
        except ValueError:
            pass
        
        return None
    
    def _compare_entities(
        self,
        current: Dict[str, List[Any]],
        previous: Dict[str, List[Any]]
    ) -> Dict[str, Any]:
        """Compare entities between runs"""
        comparison = {}
        
        # Get all entity types
        all_types = set(current.keys()) | set(previous.keys())
        
        for entity_type in all_types:
            current_entities = current.get(entity_type, [])
            previous_entities = previous.get(entity_type, [])
            
            # Create ID sets
            current_ids = {self._get_entity_id(e) for e in current_entities}
            previous_ids = {self._get_entity_id(e) for e in previous_entities}
            
            # Find changes
            added = current_ids - previous_ids
            removed = previous_ids - current_ids
            common = current_ids & previous_ids
            
            # Check for modifications in common entities
            modified = []
            for entity_id in common:
                current_entity = next((e for e in current_entities if self._get_entity_id(e) == entity_id), None)
                previous_entity = next((e for e in previous_entities if self._get_entity_id(e) == entity_id), None)
                
                if current_entity and previous_entity:
                    if self._entities_differ(current_entity, previous_entity):
                        modified.append(entity_id)
            
            comparison[entity_type] = {
                "added": list(added),
                "removed": list(removed),
                "modified": modified,
                "unchanged": len(common) - len(modified),
                "total_current": len(current_entities),
                "total_previous": len(previous_entities)
            }
        
        return comparison
    
    def _compare_relationships(
        self,
        current: List[Dict[str, Any]],
        previous: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare relationships between runs"""
        # Create relationship signatures
        current_sigs = {self._relationship_signature(r) for r in current}
        previous_sigs = {self._relationship_signature(r) for r in previous}
        
        added = current_sigs - previous_sigs
        removed = previous_sigs - current_sigs
        
        return {
            "added": list(added),
            "removed": list(removed),
            "unchanged": len(current_sigs & previous_sigs),
            "total_current": len(current),
            "total_previous": len(previous)
        }
    
    def _compare_metadata(
        self,
        current: Dict[str, List[Dict[str, Any]]],
        previous: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Compare metadata between runs"""
        comparison = {}
        
        all_types = set(current.keys()) | set(previous.keys())
        
        for entity_type in all_types:
            current_meta = current.get(entity_type, [])
            previous_meta = previous.get(entity_type, [])
            
            # Count metadata entries
            current_count = len(current_meta)
            previous_count = len(previous_meta)
            
            comparison[entity_type] = {
                "current_count": current_count,
                "previous_count": previous_count,
                "change": current_count - previous_count
            }
        
        return comparison
    
    def _compare_topology(
        self,
        current: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare topology between runs"""
        current_summary = current.get("summary", {})
        previous_summary = previous.get("summary", {})
        
        return {
            "nodes": {
                "current": current_summary.get("total_nodes", 0),
                "previous": previous_summary.get("total_nodes", 0),
                "change": current_summary.get("total_nodes", 0) - previous_summary.get("total_nodes", 0)
            },
            "depth": {
                "current": current_summary.get("max_depth", 0),
                "previous": previous_summary.get("max_depth", 0),
                "change": current_summary.get("max_depth", 0) - previous_summary.get("max_depth", 0)
            },
            "by_type": self._compare_type_counts(
                current_summary.get("by_type", {}),
                previous_summary.get("by_type", {})
            )
        }
    
    def _compare_type_counts(
        self,
        current: Dict[str, int],
        previous: Dict[str, int]
    ) -> Dict[str, Dict[str, int]]:
        """Compare counts by type"""
        comparison = {}
        all_types = set(current.keys()) | set(previous.keys())
        
        for type_name in all_types:
            current_count = current.get(type_name, 0)
            previous_count = previous.get(type_name, 0)
            
            comparison[type_name] = {
                "current": current_count,
                "previous": previous_count,
                "change": current_count - previous_count
            }
        
        return comparison
    
    def _get_entity_id(self, entity: Any) -> str:
        """Get entity ID"""
        if isinstance(entity, dict):
            return str(entity.get("id", ""))
        return str(entity)
    
    def _entities_differ(self, entity1: Any, entity2: Any) -> bool:
        """Check if two entities differ"""
        if not isinstance(entity1, dict) or not isinstance(entity2, dict):
            return entity1 != entity2
        
        # Compare key fields (excluding timestamps)
        exclude_keys = {"created_at", "updated_at", "last_modified"}
        
        keys1 = set(entity1.keys()) - exclude_keys
        keys2 = set(entity2.keys()) - exclude_keys
        
        if keys1 != keys2:
            return True
        
        for key in keys1:
            if entity1[key] != entity2[key]:
                return True
        
        return False
    
    def _relationship_signature(self, rel: Dict[str, Any]) -> str:
        """Create unique signature for relationship"""
        return f"{rel.get('source_type')}:{rel.get('source_id')}-{rel.get('relationship')}-{rel.get('target_type')}:{rel.get('target_id')}"
    
    def _generate_comparison_summary(self, comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of comparison"""
        total_changes = 0
        
        # Count entity changes
        entities_added = 0
        entities_removed = 0
        entities_modified = 0
        
        for entity_type, changes in comparison.get("entities", {}).items():
            entities_added += len(changes.get("added", []))
            entities_removed += len(changes.get("removed", []))
            entities_modified += len(changes.get("modified", []))
        
        total_changes += entities_added + entities_removed + entities_modified
        
        # Count relationship changes
        rel_changes = comparison.get("relationships", {})
        relationships_added = len(rel_changes.get("added", []))
        relationships_removed = len(rel_changes.get("removed", []))
        
        total_changes += relationships_added + relationships_removed
        
        # Count topology changes
        topo_changes = comparison.get("topology", {})
        topology_node_change = abs(topo_changes.get("nodes", {}).get("change", 0))
        
        total_changes += topology_node_change
        
        return {
            "total_changes": total_changes,
            "entities": {
                "added": entities_added,
                "removed": entities_removed,
                "modified": entities_modified
            },
            "relationships": {
                "added": relationships_added,
                "removed": relationships_removed
            },
            "topology": {
                "node_change": topology_node_change
            },
            "has_significant_changes": total_changes > 0
        }
    
    def get_change_details(
        self,
        comparison: Dict[str, Any],
        entity_type: str,
        change_type: str
    ) -> List[str]:
        """
        Get detailed list of changes
        
        Args:
            comparison: Comparison result
            entity_type: Type of entity
            change_type: Type of change (added, removed, modified)
            
        Returns:
            List of entity IDs
        """
        entities = comparison.get("entities", {})
        entity_changes = entities.get(entity_type, {})
        return entity_changes.get(change_type, [])

# Made with Bob
