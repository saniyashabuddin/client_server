"""
Autonomous Question Generator

Automatically generates intelligent questions about the discovered system
based on entities, relationships, metadata, and topology.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

from logger import get_logger

logger = get_logger(__name__)


class Question:
    """Represents a generated question"""
    
    def __init__(
        self,
        question_id: str,
        question_text: str,
        category: str,
        priority: str,
        context: Dict[str, Any],
        expected_answer_type: str
    ):
        self.question_id = question_id
        self.question_text = question_text
        self.category = category
        self.priority = priority
        self.context = context
        self.expected_answer_type = expected_answer_type
        self.generated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert question to dictionary"""
        return {
            "id": self.question_id,
            "text": self.question_text,
            "category": self.category,
            "priority": self.priority,
            "context": self.context,
            "expected_answer_type": self.expected_answer_type,
            "generated_at": self.generated_at
        }


class AutonomousQuestionGenerator:
    """
    Automatically generates questions about the system
    
    Question categories:
    - Overview: High-level system questions
    - Entities: Questions about specific entities
    - Relationships: Questions about connections
    - Topology: Questions about structure
    - Changes: Questions about differences from previous runs
    - Anomalies: Questions about unusual patterns
    - Recommendations: Questions about improvements
    """
    
    def __init__(self):
        """Initialize Question Generator"""
        self.questions: List[Question] = []
        self.question_counter = 0
        
        logger.info("Autonomous Question Generator initialized")
    
    def generate_questions(
        self,
        entities: Dict[str, List[Any]],
        relationships: List[Dict[str, Any]],
        metadata: Dict[str, List[Dict[str, Any]]],
        topology: Dict[str, Any],
        comparison: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate all questions
        
        Args:
            entities: Discovered entities
            relationships: Discovered relationships
            metadata: Extracted metadata
            topology: Topology graph
            comparison: Optional comparison with previous run
            
        Returns:
            List of generated questions
        """
        logger.info("Generating autonomous questions...")
        start_time = datetime.now()
        
        self.questions.clear()
        self.question_counter = 0
        
        # Generate different types of questions
        self._generate_overview_questions(entities, relationships, topology)
        self._generate_entity_questions(entities, metadata)
        self._generate_relationship_questions(relationships)
        self._generate_topology_questions(topology)
        
        if comparison:
            self._generate_change_questions(comparison)
        
        self._generate_anomaly_questions(entities, relationships, metadata)
        self._generate_recommendation_questions(entities, topology)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Generated {len(self.questions)} questions in {duration:.2f}s")
        
        return [q.to_dict() for q in self.questions]
    
    def _generate_overview_questions(
        self,
        entities: Dict[str, List[Any]],
        relationships: List[Dict[str, Any]],
        topology: Dict[str, Any]
    ) -> None:
        """Generate high-level overview questions"""
        # Total counts
        total_entities = sum(len(v) for v in entities.values())
        total_relationships = len(relationships)
        
        self._add_question(
            f"What is the overall structure of the system with {total_entities} entities and {total_relationships} relationships?",
            "overview",
            "high",
            {"total_entities": total_entities, "total_relationships": total_relationships},
            "summary"
        )
        
        # Entity distribution
        self._add_question(
            f"How are the {total_entities} entities distributed across different types?",
            "overview",
            "high",
            {"entity_counts": {k: len(v) for k, v in entities.items()}},
            "distribution"
        )
        
        # Topology depth
        max_depth = topology.get("summary", {}).get("max_depth", 0)
        if max_depth > 0:
            self._add_question(
                f"What does the topology hierarchy with depth {max_depth} tell us about system organization?",
                "overview",
                "medium",
                {"max_depth": max_depth},
                "analysis"
            )
    
    def _generate_entity_questions(
        self,
        entities: Dict[str, List[Any]],
        metadata: Dict[str, List[Dict[str, Any]]]
    ) -> None:
        """Generate questions about specific entities"""
        for entity_type, entity_list in entities.items():
            if not entity_list:
                continue
            
            count = len(entity_list)
            
            # Count questions
            self._add_question(
                f"What are the characteristics of the {count} {entity_type} entities in the system?",
                "entities",
                "medium",
                {"entity_type": entity_type, "count": count},
                "characteristics"
            )
            
            # Metadata questions
            meta_list = metadata.get(entity_type, [])
            if meta_list:
                self._add_question(
                    f"What insights can we derive from the metadata of {entity_type} entities?",
                    "entities",
                    "medium",
                    {"entity_type": entity_type, "metadata_count": len(meta_list)},
                    "insights"
                )
            
            # Largest entities
            if entity_type == "files" and count > 0:
                self._add_question(
                    f"Which are the largest files and what do they contain?",
                    "entities",
                    "low",
                    {"entity_type": "files"},
                    "list"
                )
    
    def _generate_relationship_questions(
        self,
        relationships: List[Dict[str, Any]]
    ) -> None:
        """Generate questions about relationships"""
        if not relationships:
            return
        
        # Relationship types
        rel_types = defaultdict(int)
        for rel in relationships:
            rel_types[rel.get("relationship", "unknown")] += 1
        
        self._add_question(
            f"What types of relationships exist between entities and what do they signify?",
            "relationships",
            "high",
            {"relationship_types": dict(rel_types)},
            "analysis"
        )
        
        # Most connected entities
        self._add_question(
            "Which entities have the most connections and why are they central?",
            "relationships",
            "medium",
            {"total_relationships": len(relationships)},
            "list"
        )
        
        # Orphaned entities
        self._add_question(
            "Are there any isolated entities with no relationships?",
            "relationships",
            "medium",
            {},
            "list"
        )
    
    def _generate_topology_questions(
        self,
        topology: Dict[str, Any]
    ) -> None:
        """Generate questions about topology"""
        summary = topology.get("summary", {})
        
        if not summary:
            return
        
        # Root nodes
        root_count = summary.get("root_nodes", 0)
        if root_count > 0:
            self._add_question(
                f"What are the {root_count} root nodes and what do they represent?",
                "topology",
                "high",
                {"root_count": root_count},
                "list"
            )
        
        # Topology layers
        layers = summary.get("layers", {})
        if layers:
            self._add_question(
                f"How are entities organized across {len(layers)} topology layers?",
                "topology",
                "medium",
                {"layers": layers},
                "distribution"
            )
        
        # Depth analysis
        max_depth = summary.get("max_depth", 0)
        if max_depth > 3:
            self._add_question(
                f"Why is the topology depth {max_depth} levels deep and what does this indicate?",
                "topology",
                "medium",
                {"max_depth": max_depth},
                "analysis"
            )
    
    def _generate_change_questions(
        self,
        comparison: Dict[str, Any]
    ) -> None:
        """Generate questions about changes from previous run"""
        summary = comparison.get("summary", {})
        
        if not summary.get("has_significant_changes"):
            self._add_question(
                "Why are there no significant changes since the last run?",
                "changes",
                "low",
                {"comparison": summary},
                "analysis"
            )
            return
        
        # Entity changes
        entity_changes = summary.get("entities", {})
        added = entity_changes.get("added", 0)
        removed = entity_changes.get("removed", 0)
        modified = entity_changes.get("modified", 0)
        
        if added > 0:
            self._add_question(
                f"What are the {added} new entities that were added since the last run?",
                "changes",
                "high",
                {"added_count": added},
                "list"
            )
        
        if removed > 0:
            self._add_question(
                f"Why were {removed} entities removed since the last run?",
                "changes",
                "high",
                {"removed_count": removed},
                "analysis"
            )
        
        if modified > 0:
            self._add_question(
                f"What changed in the {modified} modified entities?",
                "changes",
                "medium",
                {"modified_count": modified},
                "details"
            )
        
        # Relationship changes
        rel_changes = summary.get("relationships", {})
        rel_added = rel_changes.get("added", 0)
        rel_removed = rel_changes.get("removed", 0)
        
        if rel_added > 0 or rel_removed > 0:
            self._add_question(
                f"How have relationships changed with {rel_added} added and {rel_removed} removed?",
                "changes",
                "medium",
                {"rel_added": rel_added, "rel_removed": rel_removed},
                "analysis"
            )
    
    def _generate_anomaly_questions(
        self,
        entities: Dict[str, List[Any]],
        relationships: List[Dict[str, Any]],
        metadata: Dict[str, List[Dict[str, Any]]]
    ) -> None:
        """Generate questions about anomalies"""
        # Check for empty entity types
        for entity_type, entity_list in entities.items():
            if len(entity_list) == 0:
                self._add_question(
                    f"Why are there no {entity_type} entities in the system?",
                    "anomalies",
                    "medium",
                    {"entity_type": entity_type},
                    "analysis"
                )
        
        # Check for entities without metadata
        for entity_type, entity_list in entities.items():
            if entity_list and not metadata.get(entity_type):
                self._add_question(
                    f"Why do {entity_type} entities have no metadata?",
                    "anomalies",
                    "low",
                    {"entity_type": entity_type},
                    "analysis"
                )
    
    def _generate_recommendation_questions(
        self,
        entities: Dict[str, List[Any]],
        topology: Dict[str, Any]
    ) -> None:
        """Generate questions about recommendations"""
        total_entities = sum(len(v) for v in entities.values())
        
        if total_entities > 1000:
            self._add_question(
                f"With {total_entities} entities, what optimizations should be considered?",
                "recommendations",
                "medium",
                {"total_entities": total_entities},
                "recommendations"
            )
        
        # Topology recommendations
        max_depth = topology.get("summary", {}).get("max_depth", 0)
        if max_depth > 5:
            self._add_question(
                f"Should the topology depth of {max_depth} be restructured for better organization?",
                "recommendations",
                "low",
                {"max_depth": max_depth},
                "recommendations"
            )
    
    def _add_question(
        self,
        text: str,
        category: str,
        priority: str,
        context: Dict[str, Any],
        answer_type: str
    ) -> None:
        """Add a question to the list"""
        self.question_counter += 1
        question = Question(
            question_id=f"Q{self.question_counter:03d}",
            question_text=text,
            category=category,
            priority=priority,
            context=context,
            expected_answer_type=answer_type
        )
        self.questions.append(question)
    
    def get_questions_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get questions by category"""
        return [
            q.to_dict() for q in self.questions
            if q.category == category
        ]
    
    def get_questions_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Get questions by priority"""
        return [
            q.to_dict() for q in self.questions
            if q.priority == priority
        ]
    
    def get_question_summary(self) -> Dict[str, Any]:
        """Get summary of generated questions"""
        by_category = defaultdict(int)
        by_priority = defaultdict(int)
        
        for q in self.questions:
            by_category[q.category] += 1
            by_priority[q.priority] += 1
        
        return {
            "total_questions": len(self.questions),
            "by_category": dict(by_category),
            "by_priority": dict(by_priority)
        }

# Made with Bob
