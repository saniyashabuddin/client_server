"""
Insight Engine

Generates AI analyst insights from discovered data, relationships,
and answered questions. Provides high-level analysis and recommendations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

from logger import get_logger

logger = get_logger(__name__)


class Insight:
    """Represents an AI-generated insight"""
    
    def __init__(
        self,
        insight_id: str,
        category: str,
        title: str,
        description: str,
        severity: str,
        evidence: List[Dict[str, Any]],
        recommendations: List[str]
    ):
        self.insight_id = insight_id
        self.category = category
        self.title = title
        self.description = description
        self.severity = severity
        self.evidence = evidence
        self.recommendations = recommendations
        self.generated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert insight to dictionary"""
        return {
            "id": self.insight_id,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "evidence": self.evidence,
            "recommendations": self.recommendations,
            "generated_at": self.generated_at
        }


class InsightEngine:
    """
    Generates AI analyst insights
    
    Insight categories:
    - Architecture: System architecture insights
    - Performance: Performance-related insights
    - Security: Security considerations
    - Data Quality: Data quality issues
    - Optimization: Optimization opportunities
    - Anomalies: Unusual patterns
    - Trends: Trend analysis
    """
    
    def __init__(self):
        """Initialize Insight Engine"""
        self.insights: List[Insight] = []
        self.insight_counter = 0
        
        logger.info("Insight Engine initialized")
    
    def generate_insights(
        self,
        entities: Dict[str, List[Any]],
        relationships: List[Dict[str, Any]],
        metadata: Dict[str, List[Dict[str, Any]]],
        topology: Dict[str, Any],
        questions: List[Dict[str, Any]],
        answers: List[Dict[str, Any]],
        comparison: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate all insights
        
        Args:
            entities: Discovered entities
            relationships: Discovered relationships
            metadata: Extracted metadata
            topology: Topology graph
            questions: Generated questions
            answers: Question answers
            comparison: Optional comparison data
            
        Returns:
            List of generated insights
        """
        logger.info("Generating AI analyst insights...")
        start_time = datetime.now()
        
        self.insights.clear()
        self.insight_counter = 0
        
        # Generate different types of insights
        self._generate_architecture_insights(entities, relationships, topology)
        self._generate_performance_insights(entities, topology)
        self._generate_data_quality_insights(entities, metadata)
        self._generate_optimization_insights(entities, relationships, topology)
        
        if comparison:
            self._generate_trend_insights(comparison)
        
        self._generate_anomaly_insights(entities, relationships, metadata)
        self._generate_answer_based_insights(answers)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Generated {len(self.insights)} insights in {duration:.2f}s")
        
        return [i.to_dict() for i in self.insights]
    
    def _generate_architecture_insights(
        self,
        entities: Dict[str, List[Any]],
        relationships: List[Dict[str, Any]],
        topology: Dict[str, Any]
    ) -> None:
        """Generate architecture insights"""
        total_entities = sum(len(v) for v in entities.values())
        total_relationships = len(relationships)
        max_depth = topology.get("summary", {}).get("max_depth", 0)
        
        # Complexity insight
        if total_entities > 500 or total_relationships > 1000:
            self._add_insight(
                category="architecture",
                title="High System Complexity Detected",
                description=f"The system has {total_entities} entities and {total_relationships} relationships, indicating high complexity. This may impact maintainability and performance.",
                severity="medium",
                evidence=[
                    {"type": "entity_count", "value": total_entities},
                    {"type": "relationship_count", "value": total_relationships}
                ],
                recommendations=[
                    "Consider modularizing the system into smaller components",
                    "Implement clear boundaries between subsystems",
                    "Document architectural decisions and patterns"
                ]
            )
        
        # Hierarchy depth insight
        if max_depth > 5:
            self._add_insight(
                category="architecture",
                title="Deep Hierarchy Structure",
                description=f"The topology has a depth of {max_depth} levels, which may indicate over-nesting or complex dependencies.",
                severity="low",
                evidence=[{"type": "max_depth", "value": max_depth}],
                recommendations=[
                    "Review hierarchy structure for simplification opportunities",
                    "Consider flattening some levels if appropriate",
                    "Ensure deep nesting is intentional and documented"
                ]
            )
        
        # Relationship density
        if total_entities > 0:
            density = total_relationships / total_entities
            if density > 5:
                self._add_insight(
                    category="architecture",
                    title="High Relationship Density",
                    description=f"Average of {density:.1f} relationships per entity suggests tight coupling.",
                    severity="medium",
                    evidence=[{"type": "relationship_density", "value": density}],
                    recommendations=[
                        "Review coupling between components",
                        "Consider introducing abstraction layers",
                        "Evaluate if all relationships are necessary"
                    ]
                )
    
    def _generate_performance_insights(
        self,
        entities: Dict[str, List[Any]],
        topology: Dict[str, Any]
    ) -> None:
        """Generate performance insights"""
        total_entities = sum(len(v) for v in entities.values())
        
        # Large dataset insight
        if total_entities > 1000:
            self._add_insight(
                category="performance",
                title="Large Dataset Detected",
                description=f"System contains {total_entities} entities. Consider implementing performance optimizations.",
                severity="medium",
                evidence=[{"type": "total_entities", "value": total_entities}],
                recommendations=[
                    "Implement pagination for large result sets",
                    "Add caching for frequently accessed data",
                    "Consider database indexing strategies",
                    "Implement lazy loading where appropriate"
                ]
            )
        
        # File size analysis
        files = entities.get("files", [])
        if files:
            large_files = [f for f in files if isinstance(f, dict) and f.get("size", 0) > 10_000_000]
            if large_files:
                self._add_insight(
                    category="performance",
                    title="Large Files Detected",
                    description=f"Found {len(large_files)} files larger than 10MB. These may impact performance.",
                    severity="low",
                    evidence=[{"type": "large_files", "count": len(large_files)}],
                    recommendations=[
                        "Consider chunking large files for processing",
                        "Implement streaming for large file operations",
                        "Review if all large files are necessary"
                    ]
                )
    
    def _generate_data_quality_insights(
        self,
        entities: Dict[str, List[Any]],
        metadata: Dict[str, List[Dict[str, Any]]]
    ) -> None:
        """Generate data quality insights"""
        # Missing metadata
        for entity_type, entity_list in entities.items():
            if entity_list and not metadata.get(entity_type):
                self._add_insight(
                    category="data_quality",
                    title=f"Missing Metadata for {entity_type}",
                    description=f"{len(entity_list)} {entity_type} entities lack metadata, reducing discoverability.",
                    severity="low",
                    evidence=[{"type": "missing_metadata", "entity_type": entity_type}],
                    recommendations=[
                        f"Add metadata extraction for {entity_type}",
                        "Implement metadata validation",
                        "Ensure consistent metadata across all entity types"
                    ]
                )
        
        # Empty entity types
        empty_types = [k for k, v in entities.items() if len(v) == 0]
        if empty_types:
            self._add_insight(
                category="data_quality",
                title="Empty Entity Types Detected",
                description=f"Entity types {', '.join(empty_types)} have no data. This may indicate incomplete system setup.",
                severity="low",
                evidence=[{"type": "empty_types", "value": empty_types}],
                recommendations=[
                    "Verify if these entity types should have data",
                    "Check data ingestion processes",
                    "Review system configuration"
                ]
            )
    
    def _generate_optimization_insights(
        self,
        entities: Dict[str, List[Any]],
        relationships: List[Dict[str, Any]],
        topology: Dict[str, Any]
    ) -> None:
        """Generate optimization insights"""
        # Orphaned entities
        connected_entities = set()
        for rel in relationships:
            connected_entities.add(rel.get("source_id"))
            connected_entities.add(rel.get("target_id"))
        
        total_entities = sum(len(v) for v in entities.values())
        orphaned_count = total_entities - len(connected_entities)
        
        if orphaned_count > 0:
            orphan_percentage = (orphaned_count / total_entities) * 100
            if orphan_percentage > 10:
                self._add_insight(
                    category="optimization",
                    title="High Number of Orphaned Entities",
                    description=f"{orphaned_count} entities ({orphan_percentage:.1f}%) have no relationships.",
                    severity="medium",
                    evidence=[{"type": "orphaned_entities", "count": orphaned_count}],
                    recommendations=[
                        "Review orphaned entities for relevance",
                        "Consider establishing relationships",
                        "Clean up unused entities if appropriate"
                    ]
                )
        
        # Duplicate detection opportunity
        if total_entities > 100:
            self._add_insight(
                category="optimization",
                title="Consider Duplicate Detection",
                description=f"With {total_entities} entities, implementing duplicate detection could improve data quality.",
                severity="low",
                evidence=[{"type": "entity_count", "value": total_entities}],
                recommendations=[
                    "Implement duplicate detection algorithms",
                    "Add entity deduplication process",
                    "Create merge strategies for duplicates"
                ]
            )
    
    def _generate_trend_insights(
        self,
        comparison: Dict[str, Any]
    ) -> None:
        """Generate trend insights from comparison"""
        summary = comparison.get("summary", {})
        
        if not summary.get("has_significant_changes"):
            self._add_insight(
                category="trends",
                title="System Stability",
                description="No significant changes detected since last run, indicating system stability.",
                severity="info",
                evidence=[{"type": "comparison", "value": summary}],
                recommendations=[
                    "Continue monitoring for changes",
                    "Maintain current processes"
                ]
            )
            return
        
        # Growth trend
        entity_changes = summary.get("entities", {})
        added = entity_changes.get("added", 0)
        removed = entity_changes.get("removed", 0)
        
        if added > removed * 2:
            self._add_insight(
                category="trends",
                title="Rapid Growth Detected",
                description=f"System growing rapidly with {added} new entities vs {removed} removed.",
                severity="medium",
                evidence=[{"type": "growth", "added": added, "removed": removed}],
                recommendations=[
                    "Monitor resource utilization",
                    "Plan for scaling if growth continues",
                    "Review data retention policies"
                ]
            )
        elif removed > added * 2:
            self._add_insight(
                category="trends",
                title="Significant Data Reduction",
                description=f"Large number of entities removed ({removed}) vs added ({added}).",
                severity="medium",
                evidence=[{"type": "reduction", "added": added, "removed": removed}],
                recommendations=[
                    "Verify deletions are intentional",
                    "Review data retention policies",
                    "Ensure no data loss occurred"
                ]
            )
    
    def _generate_anomaly_insights(
        self,
        entities: Dict[str, List[Any]],
        relationships: List[Dict[str, Any]],
        metadata: Dict[str, List[Dict[str, Any]]]
    ) -> None:
        """Generate anomaly insights"""
        # Imbalanced entity distribution
        entity_counts = {k: len(v) for k, v in entities.items()}
        if entity_counts:
            max_count = max(entity_counts.values())
            min_count = min(entity_counts.values())
            
            if max_count > min_count * 10:
                self._add_insight(
                    category="anomalies",
                    title="Imbalanced Entity Distribution",
                    description="Significant imbalance in entity type distribution detected.",
                    severity="low",
                    evidence=[{"type": "distribution", "value": entity_counts}],
                    recommendations=[
                        "Review if imbalance is expected",
                        "Consider if underrepresented types need attention",
                        "Verify data collection is complete"
                    ]
                )
    
    def _generate_answer_based_insights(
        self,
        answers: List[Dict[str, Any]]
    ) -> None:
        """Generate insights based on question answers"""
        # Low confidence answers
        low_confidence = [a for a in answers if a.get("confidence", 1.0) < 0.6]
        
        if len(low_confidence) > len(answers) * 0.3:
            self._add_insight(
                category="data_quality",
                title="High Uncertainty in Analysis",
                description=f"{len(low_confidence)} of {len(answers)} answers have low confidence.",
                severity="medium",
                evidence=[{"type": "low_confidence_count", "value": len(low_confidence)}],
                recommendations=[
                    "Improve data collection processes",
                    "Add more metadata for better analysis",
                    "Review data completeness"
                ]
            )
    
    def _add_insight(
        self,
        category: str,
        title: str,
        description: str,
        severity: str,
        evidence: List[Dict[str, Any]],
        recommendations: List[str]
    ) -> None:
        """Add an insight to the list"""
        self.insight_counter += 1
        insight = Insight(
            insight_id=f"I{self.insight_counter:03d}",
            category=category,
            title=title,
            description=description,
            severity=severity,
            evidence=evidence,
            recommendations=recommendations
        )
        self.insights.append(insight)
    
    def get_insights_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get insights by category"""
        return [
            i.to_dict() for i in self.insights
            if i.category == category
        ]
    
    def get_insights_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Get insights by severity"""
        return [
            i.to_dict() for i in self.insights
            if i.severity == severity
        ]
    
    def get_insight_summary(self) -> Dict[str, Any]:
        """Get summary of insights"""
        by_category = defaultdict(int)
        by_severity = defaultdict(int)
        
        for insight in self.insights:
            by_category[insight.category] += 1
            by_severity[insight.severity] += 1
        
        return {
            "total_insights": len(self.insights),
            "by_category": dict(by_category),
            "by_severity": dict(by_severity)
        }

# Made with Bob
