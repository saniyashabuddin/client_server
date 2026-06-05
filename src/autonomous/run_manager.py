"""
Run and Session Management for Autonomous CABP Platform

Manages unique run IDs, session IDs, and execution tracking.
Every execution creates a new run with complete isolation.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import uuid
from pathlib import Path
import json

from logger import get_logger

logger = get_logger(__name__)


class RunManager:
    """Manages run IDs, session IDs, and execution tracking"""
    
    def __init__(self, storage_path: str = "runs"):
        """
        Initialize Run Manager
        
        Args:
            storage_path: Directory to store run information
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.run_id: Optional[str] = None
        self.session_id: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.metadata: Dict[str, Any] = {}
        
        logger.info("Run Manager initialized")
    
    def create_run(self) -> str:
        """
        Create a new run ID
        
        Returns:
            Unique run ID in format RUN_YYYYMMDD_NNN
        """
        # Generate date-based run ID
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Find next available run number for today
        run_number = 1
        while True:
            run_id = f"RUN_{date_str}_{run_number:03d}"
            run_file = self.storage_path / f"{run_id}.json"
            if not run_file.exists():
                break
            run_number += 1
        
        self.run_id = run_id
        self.start_time = datetime.now()
        
        logger.info(f"Created new run: {run_id}")
        return run_id
    
    def create_session(self) -> str:
        """
        Create a new session ID
        
        Returns:
            Unique session ID (UUID)
        """
        self.session_id = str(uuid.uuid4())
        logger.info(f"Created new session: {self.session_id}")
        return self.session_id
    
    def update_metadata(self, key: str, value: Any) -> None:
        """
        Update run metadata
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        logger.debug(f"Updated metadata: {key} = {value}")
    
    def save_run_info(self) -> None:
        """Save run information to disk"""
        if not self.run_id:
            logger.warning("No run ID to save")
            return
        
        run_info = {
            "run_id": self.run_id,
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": datetime.now().isoformat(),
            "metadata": self.metadata
        }
        
        run_file = self.storage_path / f"{self.run_id}.json"
        with open(run_file, 'w') as f:
            json.dump(run_info, f, indent=2)
        
        logger.info(f"Saved run info to {run_file}")
    
    def get_previous_runs(self, limit: int = 10) -> list:
        """
        Get previous run IDs
        
        Args:
            limit: Maximum number of runs to return
            
        Returns:
            List of previous run IDs (most recent first)
        """
        run_files = sorted(
            self.storage_path.glob("RUN_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        runs = []
        for run_file in run_files[:limit]:
            try:
                with open(run_file, 'r') as f:
                    run_info = json.load(f)
                    runs.append(run_info)
            except Exception as e:
                logger.error(f"Error loading run file {run_file}: {e}")
        
        return runs
    
    def get_run_info(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific run
        
        Args:
            run_id: Run ID to retrieve
            
        Returns:
            Run information or None if not found
        """
        run_file = self.storage_path / f"{run_id}.json"
        if not run_file.exists():
            return None
        
        try:
            with open(run_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading run {run_id}: {e}")
            return None
    
    def get_current_run_summary(self) -> Dict[str, Any]:
        """
        Get summary of current run
        
        Returns:
            Dictionary with run summary
        """
        return {
            "run_id": self.run_id,
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "duration": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            "metadata": self.metadata
        }

# Made with Bob
