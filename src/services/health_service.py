"""
Health Service Module

Handles health check and monitoring operations including:
- System health checks
- Component health monitoring
- Service status checks
"""

from typing import Dict, Any, Optional

from api_client import APIClient
from logger import get_logger
from error_handler import HealthError

logger = get_logger(__name__)


class HealthService:
    """Service for handling health check and monitoring operations"""

    def __init__(self, api_client: APIClient):
        """
        Initialize health service
        
        Args:
            api_client: API client instance
        """
        self.api_client = api_client
        logger.info("Health service initialized")

    def check_system_health(self) -> Dict[str, Any]:
        """
        Perform system health check
        
        Returns:
            Health check response with system status
            
        Raises:
            HealthError: If health check fails
        """
        try:
            logger.info("Checking system health")
            
            response = self.api_client.get('/health/')
            
            status = response.get('status', 'unknown')
            logger.info(f"System health: {status}")
            
            return response
            
        except Exception as e:
            logger.error(f"System health check failed: {str(e)}")
            raise HealthError(f"Failed to check system health: {str(e)}")

    def get_component_health(self, component_id: int) -> Dict[str, Any]:
        """
        Get health status of a specific component
        
        Args:
            component_id: Component ID
            
        Returns:
            Component health response with status and metrics
            
        Raises:
            HealthError: If retrieval fails
        """
        try:
            logger.info(f"Getting health for component: {component_id}")
            
            response = self.api_client.get(f'/health/components/{component_id}')
            
            status = response.get('current_status', 'unknown')
            logger.info(f"Component {component_id} health: {status}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get component health: {str(e)}")
            raise HealthError(f"Failed to get component health: {str(e)}")

    def is_system_healthy(self) -> bool:
        """
        Check if system is healthy
        
        Returns:
            True if system is healthy, False otherwise
        """
        try:
            health = self.check_system_health()
            status = health.get('status', '').lower()
            return status == 'healthy'
        except Exception as e:
            logger.error(f"Failed to check if system is healthy: {str(e)}")
            return False

    def get_database_status(self) -> str:
        """
        Get database status
        
        Returns:
            Database status string
            
        Raises:
            HealthError: If retrieval fails
        """
        try:
            health = self.check_system_health()
            db_status = health.get('database', 'unknown')
            logger.info(f"Database status: {db_status}")
            return db_status
        except Exception as e:
            logger.error(f"Failed to get database status: {str(e)}")
            raise HealthError(f"Failed to get database status: {str(e)}")

    def get_embedding_service_status(self) -> str:
        """
        Get embedding service status
        
        Returns:
            Embedding service status string
            
        Raises:
            HealthError: If retrieval fails
        """
        try:
            health = self.check_system_health()
            embedding_status = health.get('embedding_service', 'unknown')
            logger.info(f"Embedding service status: {embedding_status}")
            return embedding_status
        except Exception as e:
            logger.error(f"Failed to get embedding service status: {str(e)}")
            raise HealthError(f"Failed to get embedding service status: {str(e)}")

    def get_ollama_service_status(self) -> str:
        """
        Get Ollama service status
        
        Returns:
            Ollama service status string
            
        Raises:
            HealthError: If retrieval fails
        """
        try:
            health = self.check_system_health()
            ollama_status = health.get('ollama_service', 'unknown')
            logger.info(f"Ollama service status: {ollama_status}")
            return ollama_status
        except Exception as e:
            logger.error(f"Failed to get Ollama service status: {str(e)}")
            raise HealthError(f"Failed to get Ollama service status: {str(e)}")

    def get_all_component_statuses(self) -> Dict[str, str]:
        """
        Get status of all components
        
        Returns:
            Dictionary mapping component names to statuses
            
        Raises:
            HealthError: If retrieval fails
        """
        try:
            health = self.check_system_health()
            components = health.get('components', {})
            logger.info(f"Retrieved status for {len(components)} components")
            return components
        except Exception as e:
            logger.error(f"Failed to get component statuses: {str(e)}")
            raise HealthError(f"Failed to get component statuses: {str(e)}")

    def get_system_version(self) -> str:
        """
        Get system version
        
        Returns:
            System version string
            
        Raises:
            HealthError: If retrieval fails
        """
        try:
            health = self.check_system_health()
            version = health.get('version', 'unknown')
            logger.info(f"System version: {version}")
            return version
        except Exception as e:
            logger.error(f"Failed to get system version: {str(e)}")
            raise HealthError(f"Failed to get system version: {str(e)}")

    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive health summary
        
        Returns:
            Health summary with all service statuses
            
        Raises:
            HealthError: If retrieval fails
        """
        try:
            logger.info("Getting health summary")
            
            health = self.check_system_health()
            
            summary = {
                'overall_status': health.get('status', 'unknown'),
                'database': health.get('database', 'unknown'),
                'embedding_service': health.get('embedding_service', 'unknown'),
                'ollama_service': health.get('ollama_service', 'unknown'),
                'components': health.get('components', {}),
                'version': health.get('version', 'unknown'),
                'timestamp': health.get('timestamp')
            }
            
            logger.info(f"Health summary: {summary['overall_status']}")
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get health summary: {str(e)}")
            raise HealthError(f"Failed to get health summary: {str(e)}")

    def get_component_metrics(self, component_id: int) -> Dict[str, Any]:
        """
        Get metrics for a specific component
        
        Args:
            component_id: Component ID
            
        Returns:
            Component metrics
            
        Raises:
            HealthError: If retrieval fails
        """
        try:
            logger.info(f"Getting metrics for component: {component_id}")
            
            health = self.get_component_health(component_id)
            metrics = health.get('latest_metrics', {})
            
            logger.info(f"Retrieved {len(metrics)} metrics for component {component_id}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get component metrics: {str(e)}")
            raise HealthError(f"Failed to get component metrics: {str(e)}")

    def get_component_history(self, component_id: int) -> list:
        """
        Get health history for a component
        
        Args:
            component_id: Component ID
            
        Returns:
            List of health history entries
            
        Raises:
            HealthError: If retrieval fails
        """
        try:
            logger.info(f"Getting health history for component: {component_id}")
            
            health = self.get_component_health(component_id)
            history = health.get('history', [])
            
            logger.info(f"Retrieved {len(history)} history entries for component {component_id}")
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get component history: {str(e)}")
            raise HealthError(f"Failed to get component history: {str(e)}")

    def check_all_services_healthy(self) -> bool:
        """
        Check if all services are healthy
        
        Returns:
            True if all services are healthy, False otherwise
        """
        try:
            health = self.check_system_health()
            
            # Check overall status
            if health.get('status', '').lower() != 'healthy':
                return False
            
            # Check individual services
            services = ['database', 'embedding_service', 'ollama_service']
            for service in services:
                status = health.get(service, '').lower()
                if status not in ['healthy', 'connected', 'available']:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check all services: {str(e)}")
            return False

    def get_unhealthy_components(self) -> list:
        """
        Get list of unhealthy components
        
        Returns:
            List of component names that are not healthy
        """
        try:
            components = self.get_all_component_statuses()
            
            unhealthy = [
                name for name, status in components.items()
                if status.lower() not in ['healthy', 'connected', 'available']
            ]
            
            logger.info(f"Found {len(unhealthy)} unhealthy components")
            
            return unhealthy
            
        except Exception as e:
            logger.error(f"Failed to get unhealthy components: {str(e)}")
            return []

    def wait_for_healthy_status(
        self,
        timeout_seconds: int = 30,
        check_interval: int = 5
    ) -> bool:
        """
        Wait for system to become healthy
        
        Args:
            timeout_seconds: Maximum time to wait
            check_interval: Seconds between checks
            
        Returns:
            True if system became healthy, False if timeout
        """
        import time
        
        logger.info(f"Waiting for healthy status (timeout: {timeout_seconds}s)")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            if self.is_system_healthy():
                logger.info("System is healthy")
                return True
            
            time.sleep(check_interval)
        
        logger.warning(f"System did not become healthy within {timeout_seconds}s")
        return False

# Made with Bob
