"""
Audit Store

Maintains comprehensive audit trail of all autonomous operations,
decisions, and data transformations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json

from logger import get_logger

logger = get_logger(__name__)


class AuditEntry:
    """Represents a single audit entry"""
    
    def __init__(
        self,
        entry_id: str,
        run_id: str,
        session_id: str,
        timestamp: str,
        operation: str,
        component: str,
        status: str,
        details: Dict[str, Any],
        duration: Optional[float] = None,
        error: Optional[str] = None
    ):
        self.entry_id = entry_id
        self.run_id = run_id
        self.session_id = session_id
        self.timestamp = timestamp
        self.operation = operation
        self.component = component
        self.status = status
        self.details = details
        self.duration = duration
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit entry to dictionary"""
        return {
            "entry_id": self.entry_id,
            "run_id": self.run_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "operation": self.operation,
            "component": self.component,
            "status": self.status,
            "details": self.details,
            "duration": self.duration,
            "error": self.error
        }


class AuditStore:
    """
    Maintains comprehensive audit trail
    
    Tracks:
    - All operations performed
    - Decisions made by autonomous system
    - Data transformations
    - Errors and exceptions
    - Performance metrics
    - User interactions
    """
    
    def __init__(self, audit_dir: str = "audit"):
        """Initialize Audit Store"""
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(exist_ok=True)
        
        self.entries: List[AuditEntry] = []
        self.entry_counter = 0
        
        self.current_run_id: Optional[str] = None
        self.current_session_id: Optional[str] = None
        
        logger.info("Audit Store initialized")
    
    def set_run_context(self, run_id: str, session_id: str) -> None:
        """
        Set current run context
        
        Args:
            run_id: Current run ID
            session_id: Current session ID
        """
        self.current_run_id = run_id
        self.current_session_id = session_id
        logger.info(f"Audit context set: {run_id} / {session_id}")
    
    def log_operation(
        self,
        operation: str,
        component: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        duration: Optional[float] = None,
        error: Optional[str] = None
    ) -> str:
        """
        Log an operation
        
        Args:
            operation: Operation name
            component: Component performing operation
            status: Operation status (success, failure, in_progress)
            details: Additional details
            duration: Operation duration in seconds
            error: Error message if failed
            
        Returns:
            Entry ID
        """
        self.entry_counter += 1
        entry_id = f"AUD{self.entry_counter:06d}"
        
        entry = AuditEntry(
            entry_id=entry_id,
            run_id=self.current_run_id or "unknown",
            session_id=self.current_session_id or "unknown",
            timestamp=datetime.now().isoformat(),
            operation=operation,
            component=component,
            status=status,
            details=details or {},
            duration=duration,
            error=error
        )
        
        self.entries.append(entry)
        
        return entry_id
    
    def log_discovery(
        self,
        entity_type: str,
        count: int,
        duration: float,
        errors: int = 0
    ) -> str:
        """Log discovery operation"""
        return self.log_operation(
            operation="discovery",
            component="DiscoveryEngine",
            status="success" if errors == 0 else "partial_success",
            details={
                "entity_type": entity_type,
                "count": count,
                "errors": errors
            },
            duration=duration
        )
    
    def log_metadata_extraction(
        self,
        entity_type: str,
        count: int,
        duration: float
    ) -> str:
        """Log metadata extraction"""
        return self.log_operation(
            operation="metadata_extraction",
            component="MetadataEngine",
            status="success",
            details={
                "entity_type": entity_type,
                "count": count
            },
            duration=duration
        )
    
    def log_relationship_building(
        self,
        relationship_count: int,
        duration: float
    ) -> str:
        """Log relationship building"""
        return self.log_operation(
            operation="relationship_building",
            component="RelationshipEngine",
            status="success",
            details={
                "relationship_count": relationship_count
            },
            duration=duration
        )
    
    def log_topology_building(
        self,
        node_count: int,
        duration: float
    ) -> str:
        """Log topology building"""
        return self.log_operation(
            operation="topology_building",
            component="TopologyGraphBuilder",
            status="success",
            details={
                "node_count": node_count
            },
            duration=duration
        )
    
    def log_question_generation(
        self,
        question_count: int,
        duration: float
    ) -> str:
        """Log question generation"""
        return self.log_operation(
            operation="question_generation",
            component="QuestionGenerator",
            status="success",
            details={
                "question_count": question_count
            },
            duration=duration
        )
    
    def log_question_answering(
        self,
        answer_count: int,
        avg_confidence: float,
        duration: float
    ) -> str:
        """Log question answering"""
        return self.log_operation(
            operation="question_answering",
            component="QuestionAnsweringEngine",
            status="success",
            details={
                "answer_count": answer_count,
                "avg_confidence": avg_confidence
            },
            duration=duration
        )
    
    def log_insight_generation(
        self,
        insight_count: int,
        duration: float
    ) -> str:
        """Log insight generation"""
        return self.log_operation(
            operation="insight_generation",
            component="InsightEngine",
            status="success",
            details={
                "insight_count": insight_count
            },
            duration=duration
        )
    
    def log_comparison(
        self,
        current_run: str,
        previous_run: str,
        change_count: int,
        duration: float
    ) -> str:
        """Log run comparison"""
        return self.log_operation(
            operation="run_comparison",
            component="RunComparator",
            status="success",
            details={
                "current_run": current_run,
                "previous_run": previous_run,
                "change_count": change_count
            },
            duration=duration
        )
    
    def log_error(
        self,
        component: str,
        operation: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log an error"""
        return self.log_operation(
            operation=operation,
            component=component,
            status="failure",
            details=details or {},
            error=error_message
        )
    
    def log_user_interaction(
        self,
        interaction_type: str,
        details: Dict[str, Any]
    ) -> str:
        """Log user interaction"""
        return self.log_operation(
            operation="user_interaction",
            component="UserInterface",
            status="success",
            details={
                "interaction_type": interaction_type,
                **details
            }
        )
    
    def get_entries_by_component(self, component: str) -> List[Dict[str, Any]]:
        """Get audit entries for a specific component"""
        return [
            e.to_dict() for e in self.entries
            if e.component == component
        ]
    
    def get_entries_by_operation(self, operation: str) -> List[Dict[str, Any]]:
        """Get audit entries for a specific operation"""
        return [
            e.to_dict() for e in self.entries
            if e.operation == operation
        ]
    
    def get_entries_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get audit entries by status"""
        return [
            e.to_dict() for e in self.entries
            if e.status == status
        ]
    
    def get_failed_operations(self) -> List[Dict[str, Any]]:
        """Get all failed operations"""
        return self.get_entries_by_status("failure")
    
    def get_audit_summary(self) -> Dict[str, Any]:
        """Get summary of audit trail"""
        if not self.entries:
            return {"total_entries": 0}
        
        by_component = {}
        by_operation = {}
        by_status = {}
        
        total_duration = 0.0
        duration_count = 0
        
        for entry in self.entries:
            # Count by component
            by_component[entry.component] = by_component.get(entry.component, 0) + 1
            
            # Count by operation
            by_operation[entry.operation] = by_operation.get(entry.operation, 0) + 1
            
            # Count by status
            by_status[entry.status] = by_status.get(entry.status, 0) + 1
            
            # Calculate average duration
            if entry.duration is not None:
                total_duration += entry.duration
                duration_count += 1
        
        avg_duration = total_duration / duration_count if duration_count > 0 else 0
        
        return {
            "total_entries": len(self.entries),
            "by_component": by_component,
            "by_operation": by_operation,
            "by_status": by_status,
            "average_duration": avg_duration,
            "failed_operations": len(self.get_failed_operations())
        }
    
    def export_audit_trail(self, run_id: Optional[str] = None) -> None:
        """
        Export audit trail to file
        
        Args:
            run_id: Optional run ID to filter entries
        """
        if run_id:
            entries_to_export = [e for e in self.entries if e.run_id == run_id]
            filename = f"audit_{run_id}.json"
        else:
            entries_to_export = self.entries
            filename = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.audit_dir / filename
        
        audit_data = {
            "exported_at": datetime.now().isoformat(),
            "run_id": run_id,
            "entry_count": len(entries_to_export),
            "entries": [e.to_dict() for e in entries_to_export],
            "summary": self.get_audit_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(audit_data, f, indent=2)
        
        logger.info(f"Exported {len(entries_to_export)} audit entries to {filepath}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from audit trail"""
        metrics = {}
        
        for entry in self.entries:
            if entry.duration is not None:
                operation = entry.operation
                if operation not in metrics:
                    metrics[operation] = {
                        "count": 0,
                        "total_duration": 0.0,
                        "min_duration": float('inf'),
                        "max_duration": 0.0
                    }
                
                metrics[operation]["count"] += 1
                metrics[operation]["total_duration"] += entry.duration
                metrics[operation]["min_duration"] = min(
                    metrics[operation]["min_duration"],
                    entry.duration
                )
                metrics[operation]["max_duration"] = max(
                    metrics[operation]["max_duration"],
                    entry.duration
                )
        
        # Calculate averages
        for operation, data in metrics.items():
            data["avg_duration"] = data["total_duration"] / data["count"]
        
        return metrics
    
    def clear_entries(self) -> None:
        """Clear all audit entries (use with caution)"""
        self.entries.clear()
        self.entry_counter = 0
        logger.warning("Audit entries cleared")

# Made with Bob
