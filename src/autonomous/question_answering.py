"""
Autonomous Question Answering Engine

Automatically answers generated questions using discovered data,
relationships, metadata, and topology. Provides evidence-based answers
with confidence scores.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict, Counter

from logger import get_logger

logger = get_logger(__name__)


class Answer:
    """Represents an answer to a question"""
    
    def __init__(
        self,
        question_id: str,
        answer_text: str,
        confidence: float,
        evidence: List[Dict[str, Any]],
        reasoning: str
    ):
        self.question_id = question_id
        self.answer_text = answer_text
        self.confidence = confidence
        self.evidence = evidence
        self.reasoning = reasoning
        self.answered_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert answer to dictionary"""
        return {
            "question_id": self.question_id,
            "answer": self.answer_text,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "reasoning": self.reasoning,
            "answered_at": self.answered_at
        }


class AutonomousQuestionAnsweringEngine:
    """
    Automatically answers questions about the system
    
    Uses:
    - Entity data
    - Relationships
    - Metadata
    - Topology
    - Comparison data
    
    Provides:
    - Evidence-based answers
    - Confidence scores
    - Reasoning explanations
    """
    
    def __init__(self):
        """Initialize Question Answering Engine"""
        self.answers: List[Answer] = []
        
        logger.info("Autonomous Question Answering Engine initialized")
    
    def answer_questions(
        self,
        questions: List[Dict[str, Any]],
        entities: Dict[str, List[Any]],
        relationships: List[Dict[str, Any]],
        metadata: Dict[str, List[Dict[str, Any]]],
        topology: Dict[str, Any],
        comparison: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Answer all questions
        
        Args:
            questions: List of questions to answer
            entities: Discovered entities
            relationships: Discovered relationships
            metadata: Extracted metadata
            topology: Topology graph
            comparison: Optional comparison data
            
        Returns:
            List of answers with evidence and confidence
        """
        logger.info(f"Answering {len(questions)} questions...")
        start_time = datetime.now()
        
        self.answers.clear()
        
        # Store data for answering
        self.entities = entities
        self.relationships = relationships
        self.metadata = metadata
        self.topology = topology
        self.comparison = comparison
        
        # Answer each question
        for question in questions:
            answer = self._answer_question(question)
            if answer:
                self.answers.append(answer)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Answered {len(self.answers)} questions in {duration:.2f}s")
        
        return [a.to_dict() for a in self.answers]
    
    def _answer_question(self, question: Dict[str, Any]) -> Optional[Answer]:
        """Answer a single question"""
        category = question.get("category")
        answer_type = question.get("expected_answer_type", "")
        context = question.get("context", {})
        
        if not answer_type:
            return None
        
        # Route to appropriate answering method
        if category == "overview":
            return self._answer_overview_question(question, context, answer_type)
        elif category == "entities":
            return self._answer_entity_question(question, context, answer_type)
        elif category == "relationships":
            return self._answer_relationship_question(question, context, answer_type)
        elif category == "topology":
            return self._answer_topology_question(question, context, answer_type)
        elif category == "changes":
            return self._answer_change_question(question, context, answer_type)
        elif category == "anomalies":
            return self._answer_anomaly_question(question, context, answer_type)
        elif category == "recommendations":
            return self._answer_recommendation_question(question, context, answer_type)
        
        return None
    
    def _answer_overview_question(
        self,
        question: Dict[str, Any],
        context: Dict[str, Any],
        answer_type: str
    ) -> Answer:
        """Answer overview questions"""
        if answer_type == "summary":
            total_entities = context.get("total_entities", 0)
            total_relationships = context.get("total_relationships", 0)
            
            answer_text = (
                f"The system contains {total_entities} entities organized through "
                f"{total_relationships} relationships. "
            )
            
            # Add entity distribution
            entity_counts = {k: len(v) for k, v in self.entities.items()}
            top_types = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            if top_types:
                answer_text += f"The largest entity types are: "
                answer_text += ", ".join([f"{t[0]} ({t[1]})" for t in top_types])
                answer_text += ". "
            
            # Add topology info
            max_depth = self.topology.get("summary", {}).get("max_depth", 0)
            if max_depth > 0:
                answer_text += f"The topology has a hierarchical depth of {max_depth} levels."
            
            evidence = [
                {"type": "entity_count", "value": total_entities},
                {"type": "relationship_count", "value": total_relationships},
                {"type": "entity_distribution", "value": entity_counts}
            ]
            
            reasoning = "Analyzed total entity and relationship counts, identified dominant entity types, and examined topology structure."
            
            return Answer(
                question_id=question.get("id", ""),
                answer_text=answer_text,
                confidence=0.95,
                evidence=evidence,
                reasoning=reasoning
            )
        
        elif answer_type == "distribution":
            entity_counts = context.get("entity_counts", {})
            
            answer_text = "Entity distribution: "
            sorted_counts = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
            
            for entity_type, count in sorted_counts:
                percentage = (count / sum(entity_counts.values())) * 100
                answer_text += f"{entity_type}: {count} ({percentage:.1f}%), "
            
            answer_text = answer_text.rstrip(", ")
            
            evidence = [{"type": "distribution", "value": entity_counts}]
            reasoning = "Calculated distribution percentages for each entity type."
            
            return Answer(
                question_id=question.get("id", ""),
                answer_text=answer_text,
                confidence=1.0,
                evidence=evidence,
                reasoning=reasoning
            )
        
        return self._create_generic_answer(question, context)
    
    def _answer_entity_question(
        self,
        question: Dict[str, Any],
        context: Dict[str, Any],
        answer_type: str
    ) -> Answer:
        """Answer entity-specific questions"""
        entity_type = context.get("entity_type", "")
        
        if answer_type == "characteristics":
            entities = self.entities.get(entity_type, []) if entity_type else []
            
            if not entities:
                return Answer(
                    question_id=question.get("id", ""),
                    answer_text=f"No {entity_type} entities found in the system.",
                    confidence=1.0,
                    evidence=[],
                    reasoning="No entities of this type exist."
                )
            
            # Analyze characteristics
            characteristics = []
            
            # Sample first few entities
            sample_size = min(5, len(entities))
            sample = entities[:sample_size]
            
            answer_text = f"The {len(entities)} {entity_type} entities have the following characteristics: "
            
            # Extract common fields
            if sample:
                common_fields = set(sample[0].keys()) if isinstance(sample[0], dict) else set()
                answer_text += f"Common fields include {', '.join(list(common_fields)[:5])}. "
            
            evidence = [
                {"type": "entity_count", "value": len(entities)},
                {"type": "sample", "value": sample}
            ]
            
            reasoning = f"Analyzed {sample_size} sample entities to identify common characteristics."
            
            return Answer(
                question_id=question.get("id", ""),
                answer_text=answer_text,
                confidence=0.85,
                evidence=evidence,
                reasoning=reasoning
            )
        
        elif answer_type == "list":
            entities = self.entities.get(entity_type, []) if entity_type else []
            
            # For files, find largest
            if entity_type == "files":
                sorted_files = sorted(
                    entities,
                    key=lambda x: x.get("size", 0) if isinstance(x, dict) else 0,
                    reverse=True
                )[:5]
                
                answer_text = "Largest files: "
                for f in sorted_files:
                    if isinstance(f, dict):
                        name = f.get("name", "Unknown")
                        size = f.get("size", 0)
                        answer_text += f"{name} ({size} bytes), "
                
                answer_text = answer_text.rstrip(", ")
                
                evidence = [{"type": "largest_files", "value": sorted_files}]
                reasoning = "Sorted files by size and selected top 5."
                
                return Answer(
                    question_id=question.get("id", ""),
                    answer_text=answer_text,
                    confidence=0.9,
                    evidence=evidence,
                    reasoning=reasoning
                )
        
        return self._create_generic_answer(question, context)
    
    def _answer_relationship_question(
        self,
        question: Dict[str, Any],
        context: Dict[str, Any],
        answer_type: str
    ) -> Answer:
        """Answer relationship questions"""
        if answer_type == "analysis":
            rel_types = context.get("relationship_types", {})
            
            answer_text = f"The system has {len(self.relationships)} relationships of {len(rel_types)} types: "
            
            sorted_types = sorted(rel_types.items(), key=lambda x: x[1], reverse=True)
            for rel_type, count in sorted_types[:5]:
                answer_text += f"{rel_type} ({count}), "
            
            answer_text = answer_text.rstrip(", ")
            answer_text += ". These relationships define the connections and dependencies between entities."
            
            evidence = [{"type": "relationship_types", "value": rel_types}]
            reasoning = "Analyzed relationship types and their frequencies."
            
            return Answer(
                question_id=question.get("id", ""),
                answer_text=answer_text,
                confidence=0.9,
                evidence=evidence,
                reasoning=reasoning
            )
        
        elif answer_type == "list":
            # Find most connected entities
            connections = defaultdict(int)
            
            for rel in self.relationships:
                source_id = rel.get("source_id")
                target_id = rel.get("target_id")
                if source_id:
                    connections[source_id] += 1
                if target_id:
                    connections[target_id] += 1
            
            top_connected = sorted(connections.items(), key=lambda x: x[1], reverse=True)[:5]
            
            answer_text = "Most connected entities: "
            for entity_id, count in top_connected:
                answer_text += f"Entity {entity_id} ({count} connections), "
            
            answer_text = answer_text.rstrip(", ")
            answer_text += ". These entities are central to the system architecture."
            
            evidence = [{"type": "top_connected", "value": dict(top_connected)}]
            reasoning = "Counted connections for each entity and identified top 5."
            
            return Answer(
                question_id=question.get("id", ""),
                answer_text=answer_text,
                confidence=0.85,
                evidence=evidence,
                reasoning=reasoning
            )
        
        return self._create_generic_answer(question, context)
    
    def _answer_topology_question(
        self,
        question: Dict[str, Any],
        context: Dict[str, Any],
        answer_type: str
    ) -> Answer:
        """Answer topology questions"""
        summary = self.topology.get("summary", {})
        
        if answer_type == "list":
            root_count = context.get("root_count", 0)
            
            answer_text = f"The system has {root_count} root nodes representing top-level entities. "
            answer_text += "These serve as entry points into the topology hierarchy."
            
            evidence = [{"type": "root_count", "value": root_count}]
            reasoning = "Identified root nodes from topology structure."
            
            return Answer(
                question_id=question.get("id", ""),
                answer_text=answer_text,
                confidence=0.9,
                evidence=evidence,
                reasoning=reasoning
            )
        
        elif answer_type == "distribution":
            layers = context.get("layers", {})
            
            answer_text = "Topology layer distribution: "
            for layer_name, count in layers.items():
                answer_text += f"{layer_name} ({count}), "
            
            answer_text = answer_text.rstrip(", ")
            
            evidence = [{"type": "layers", "value": layers}]
            reasoning = "Analyzed entity distribution across topology layers."
            
            return Answer(
                question_id=question.get("id", ""),
                answer_text=answer_text,
                confidence=0.95,
                evidence=evidence,
                reasoning=reasoning
            )
        
        return self._create_generic_answer(question, context)
    
    def _answer_change_question(
        self,
        question: Dict[str, Any],
        context: Dict[str, Any],
        answer_type: str
    ) -> Answer:
        """Answer change-related questions"""
        if not self.comparison:
            return Answer(
                question_id=question.get("id", ""),
                answer_text="No comparison data available.",
                confidence=1.0,
                evidence=[],
                reasoning="This is the first run."
            )
        
        if answer_type == "list":
            added_count = context.get("added_count", 0)
            
            answer_text = f"{added_count} new entities were added. "
            
            # Get details from comparison
            entities_comp = self.comparison.get("entities", {})
            added_details = []
            
            for entity_type, changes in entities_comp.items():
                added = changes.get("added", [])
                if added:
                    added_details.append(f"{len(added)} {entity_type}")
            
            if added_details:
                answer_text += "Breakdown: " + ", ".join(added_details)
            
            evidence = [{"type": "added_entities", "value": entities_comp}]
            reasoning = "Extracted added entities from comparison data."
            
            return Answer(
                question_id=question.get("id", ""),
                answer_text=answer_text,
                confidence=0.95,
                evidence=evidence,
                reasoning=reasoning
            )
        
        return self._create_generic_answer(question, context)
    
    def _answer_anomaly_question(
        self,
        question: Dict[str, Any],
        context: Dict[str, Any],
        answer_type: str
    ) -> Answer:
        """Answer anomaly questions"""
        entity_type = context.get("entity_type")
        
        answer_text = f"The absence of {entity_type} entities could indicate: "
        answer_text += "1) They haven't been created yet, "
        answer_text += "2) They were filtered out during discovery, or "
        answer_text += "3) The system doesn't use this entity type."
        
        evidence = [{"type": "missing_entity_type", "value": entity_type}]
        reasoning = "Analyzed possible reasons for missing entity type."
        
        return Answer(
            question_id=question.get("id", ""),
            answer_text=answer_text,
            confidence=0.7,
            evidence=evidence,
            reasoning=reasoning
        )
    
    def _answer_recommendation_question(
        self,
        question: Dict[str, Any],
        context: Dict[str, Any],
        answer_type: str
    ) -> Answer:
        """Answer recommendation questions"""
        answer_text = "Recommendations: "
        
        total_entities = context.get("total_entities", 0)
        if total_entities > 1000:
            answer_text += "1) Consider implementing pagination for large datasets. "
            answer_text += "2) Add caching for frequently accessed entities. "
            answer_text += "3) Implement indexing for faster searches."
        
        max_depth = context.get("max_depth", 0)
        if max_depth > 5:
            answer_text += " 4) Consider flattening the topology hierarchy for better performance."
        
        evidence = [{"type": "system_metrics", "value": context}]
        reasoning = "Generated recommendations based on system scale and structure."
        
        return Answer(
            question_id=question.get("id", ""),
            answer_text=answer_text,
            confidence=0.8,
            evidence=evidence,
            reasoning=reasoning
        )
    
    def _create_generic_answer(
        self,
        question: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Answer:
        """Create a generic answer when specific logic isn't available"""
        return Answer(
            question_id=question.get("id", ""),
            answer_text="Analysis in progress. More data needed for detailed answer.",
            confidence=0.5,
            evidence=[{"type": "context", "value": context}],
            reasoning="Generic answer due to insufficient specific answering logic."
        )
    
    def get_high_confidence_answers(self, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Get answers with confidence above threshold"""
        return [
            a.to_dict() for a in self.answers
            if a.confidence >= threshold
        ]
    
    def get_answer_summary(self) -> Dict[str, Any]:
        """Get summary of answers"""
        if not self.answers:
            return {"total_answers": 0}
        
        avg_confidence = sum(a.confidence for a in self.answers) / len(self.answers)
        
        confidence_distribution = {
            "high": len([a for a in self.answers if a.confidence >= 0.8]),
            "medium": len([a for a in self.answers if 0.5 <= a.confidence < 0.8]),
            "low": len([a for a in self.answers if a.confidence < 0.5])
        }
        
        return {
            "total_answers": len(self.answers),
            "average_confidence": avg_confidence,
            "confidence_distribution": confidence_distribution
        }

# Made with Bob
