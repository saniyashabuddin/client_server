"""
Topology Service Module

Handles topology operations including:
- Get current topology
- Refresh topology from IBM Storage Protect
- Visualize topology structure
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from api_client import APIClient
from logger import get_logger
from error_handler import TopologyError

logger = get_logger(__name__)


class TopologyService:
    """Service for handling topology operations"""

    def __init__(self, api_client: APIClient):
        """
        Initialize topology service
        
        Args:
            api_client: API client instance
        """
        self.api_client = api_client
        logger.info("Topology service initialized")

    def get_topology(self) -> Dict[str, Any]:
        """
        Get current IBM Storage Protect topology
        
        Returns:
            Topology response with components and statistics
            
        Raises:
            TopologyError: If retrieval fails
        """
        try:
            logger.info("Getting current topology")
            
            response = self.api_client.get('/topology/')
            
            components_count = len(response.get('components', []))
            logger.info(f"Retrieved topology with {components_count} components")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get topology: {str(e)}")
            raise TopologyError(f"Failed to get topology: {str(e)}")

    def refresh_topology(
        self,
        environment_id: str,
        components: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Refresh topology from IBM Storage Protect
        
        Args:
            environment_id: Environment identifier
            components: List of component data
            
        Returns:
            Updated topology response
            
        Raises:
            TopologyError: If refresh fails
        """
        try:
            logger.info(f"Refreshing topology for environment: {environment_id}")
            
            request_data = {
                'environment_id': environment_id,
                'components': components
            }
            
            response = self.api_client.post('/topology/refresh', json=request_data)
            
            logger.info("Topology refreshed successfully")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to refresh topology: {str(e)}")
            raise TopologyError(f"Failed to refresh topology: {str(e)}")

    def get_topology_statistics(self) -> Dict[str, Any]:
        """
        Get topology statistics
        
        Returns:
            Statistics about topology components
            
        Raises:
            TopologyError: If retrieval fails
        """
        try:
            logger.info("Getting topology statistics")
            
            topology = self.get_topology()
            statistics = topology.get('statistics', {})
            
            logger.info(f"Retrieved statistics: {statistics.get('total_components', 0)} total components")
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get topology statistics: {str(e)}")
            raise TopologyError(f"Failed to get topology statistics: {str(e)}")

    def get_component_tree(self) -> List[Dict[str, Any]]:
        """
        Get topology as a tree structure
        
        Returns:
            List of root components with nested children
            
        Raises:
            TopologyError: If retrieval fails
        """
        try:
            logger.info("Getting component tree")
            
            topology = self.get_topology()
            components = topology.get('components', [])
            
            logger.info(f"Retrieved component tree with {len(components)} root components")
            
            return components
            
        except Exception as e:
            logger.error(f"Failed to get component tree: {str(e)}")
            raise TopologyError(f"Failed to get component tree: {str(e)}")

    def find_component_by_id(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a component by its ID in the topology
        
        Args:
            component_id: Component ID to search for
            
        Returns:
            Component data if found, None otherwise
            
        Raises:
            TopologyError: If search fails
        """
        try:
            logger.info(f"Searching for component: {component_id}")
            
            topology = self.get_topology()
            components = topology.get('components', [])
            
            # Recursive search function
            def search_component(comp_list: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
                for comp in comp_list:
                    if comp.get('component_id') == component_id:
                        return comp
                    
                    # Search in children
                    children = comp.get('children', [])
                    if children:
                        result = search_component(children)
                        if result:
                            return result
                
                return None
            
            result = search_component(components)
            
            if result:
                logger.info(f"Found component: {result.get('name')}")
            else:
                logger.info(f"Component not found: {component_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to find component: {str(e)}")
            raise TopologyError(f"Failed to find component: {str(e)}")

    def get_components_by_type(self, component_type: str) -> List[Dict[str, Any]]:
        """
        Get all components of a specific type
        
        Args:
            component_type: Type of components to retrieve
            
        Returns:
            List of components matching the type
            
        Raises:
            TopologyError: If retrieval fails
        """
        try:
            logger.info(f"Getting components of type: {component_type}")
            
            topology = self.get_topology()
            components = topology.get('components', [])
            
            # Recursive collection function
            def collect_by_type(comp_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                result = []
                for comp in comp_list:
                    if comp.get('component_type') == component_type:
                        result.append(comp)
                    
                    # Search in children
                    children = comp.get('children', [])
                    if children:
                        result.extend(collect_by_type(children))
                
                return result
            
            matching_components = collect_by_type(components)
            
            logger.info(f"Found {len(matching_components)} components of type {component_type}")
            
            return matching_components
            
        except Exception as e:
            logger.error(f"Failed to get components by type: {str(e)}")
            raise TopologyError(f"Failed to get components by type: {str(e)}")

    def get_component_path(self, component_id: str) -> List[str]:
        """
        Get the path from root to a specific component
        
        Args:
            component_id: Component ID
            
        Returns:
            List of component names from root to target
            
        Raises:
            TopologyError: If retrieval fails
        """
        try:
            logger.info(f"Getting path to component: {component_id}")
            
            topology = self.get_topology()
            components = topology.get('components', [])
            
            # Recursive path finding function
            def find_path(comp_list: List[Dict[str, Any]], path: List[str]) -> Optional[List[str]]:
                for comp in comp_list:
                    current_path = path + [comp.get('name', 'Unknown')]
                    
                    if comp.get('component_id') == component_id:
                        return current_path
                    
                    # Search in children
                    children = comp.get('children', [])
                    if children:
                        result = find_path(children, current_path)
                        if result:
                            return result
                
                return None
            
            path = find_path(components, [])
            
            if path:
                logger.info(f"Found path: {' > '.join(path)}")
            else:
                logger.info(f"No path found to component: {component_id}")
                path = []
            
            return path
            
        except Exception as e:
            logger.error(f"Failed to get component path: {str(e)}")
            raise TopologyError(f"Failed to get component path: {str(e)}")

    def get_topology_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the topology
        
        Returns:
            Summary with counts and health status
            
        Raises:
            TopologyError: If retrieval fails
        """
        try:
            logger.info("Getting topology summary")
            
            topology = self.get_topology()
            statistics = topology.get('statistics', {})
            
            summary = {
                'environment_id': topology.get('environment_id'),
                'total_components': statistics.get('total_components', 0),
                'components_by_type': statistics.get('components_by_type', {}),
                'healthy_components': statistics.get('healthy_components', 0),
                'degraded_components': statistics.get('degraded_components', 0),
                'unhealthy_components': statistics.get('unhealthy_components', 0),
                'generated_at': topology.get('generated_at')
            }
            
            logger.info(f"Topology summary: {summary['total_components']} components")
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get topology summary: {str(e)}")
            raise TopologyError(f"Failed to get topology summary: {str(e)}")

    def flatten_topology(self) -> List[Dict[str, Any]]:
        """
        Get a flattened list of all components in the topology
        
        Returns:
            Flat list of all components
            
        Raises:
            TopologyError: If retrieval fails
        """
        try:
            logger.info("Flattening topology")
            
            topology = self.get_topology()
            components = topology.get('components', [])
            
            # Recursive flattening function
            def flatten(comp_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                result = []
                for comp in comp_list:
                    # Add component without children
                    comp_copy = comp.copy()
                    children = comp_copy.pop('children', [])
                    result.append(comp_copy)
                    
                    # Flatten children
                    if children:
                        result.extend(flatten(children))
                
                return result
            
            flat_components = flatten(components)
            
            logger.info(f"Flattened topology: {len(flat_components)} components")
            
            return flat_components
            
        except Exception as e:
            logger.error(f"Failed to flatten topology: {str(e)}")
            raise TopologyError(f"Failed to flatten topology: {str(e)}")

# Made with Bob
