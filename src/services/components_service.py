"""
Components Service Module

Handles component management operations including:
- Create, read, update, delete components
- List components with filtering
- Get component types
- Manage component relationships
- Get component files
"""

from typing import Dict, Any, Optional, List

from api_client import APIClient
from logger import get_logger
from error_handler import ComponentError

logger = get_logger(__name__)


class ComponentsService:
    """Service for handling component management operations"""

    def __init__(self, api_client: APIClient):
        """
        Initialize components service
        
        Args:
            api_client: API client instance
        """
        self.api_client = api_client
        logger.info("Components service initialized")

    def create_component(
        self,
        component_type: str,
        component_id: str,
        name: str,
        environment_id: str,
        parent_component_id: Optional[int] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new component
        
        Args:
            component_type: Type of component (server, storage_pool, storage_volume, workload)
            component_id: Unique component identifier
            name: Component name
            environment_id: Environment identifier
            parent_component_id: Optional parent component ID
            properties: Optional component properties
            
        Returns:
            Created component response
            
        Raises:
            ComponentError: If creation fails
        """
        try:
            logger.info(f"Creating component: {name} ({component_type})")
            
            request_data = {
                'component_type': component_type,
                'component_id': component_id,
                'name': name,
                'environment_id': environment_id
            }
            
            if parent_component_id is not None:
                request_data['parent_component_id'] = parent_component_id
            
            if properties:
                request_data['properties'] = properties
            else:
                request_data['properties'] = {}
            
            response = self.api_client.post('/components/', json=request_data)
            
            logger.info(f"Component created: id={response.get('id')}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to create component: {str(e)}")
            raise ComponentError(f"Failed to create component: {str(e)}")

    def list_components(
        self,
        skip: int = 0,
        limit: int = 100,
        component_type: Optional[str] = None,
        environment_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        List all components with optional filtering
        
        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            component_type: Optional component type filter
            environment_id: Optional environment ID filter
            
        Returns:
            Component list response with total count and components
            
        Raises:
            ComponentError: If listing fails
        """
        try:
            logger.info(f"Listing components (skip={skip}, limit={limit})")
            
            params = {
                'skip': skip,
                'limit': limit
            }
            
            if component_type:
                params['component_type'] = component_type
            
            if environment_id is not None:
                params['environment_id'] = environment_id
            
            response = self.api_client.get('/components/', params=params)
            
            total = response.get('total', 0)
            components_count = len(response.get('components', []))
            logger.info(f"Retrieved {components_count} components (total: {total})")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to list components: {str(e)}")
            raise ComponentError(f"Failed to list components: {str(e)}")

    def get_component(self, component_id: int) -> Dict[str, Any]:
        """
        Get component details by ID
        
        Args:
            component_id: Component ID
            
        Returns:
            Component details
            
        Raises:
            ComponentError: If retrieval fails
        """
        try:
            logger.info(f"Getting component: component_id={component_id}")
            
            response = self.api_client.get(f'/components/{component_id}')
            
            logger.info(f"Retrieved component: {response.get('name')}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get component {component_id}: {str(e)}")
            raise ComponentError(f"Failed to get component: {str(e)}")

    def update_component(
        self,
        component_id: int,
        name: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update a component
        
        Args:
            component_id: Component ID
            name: Optional new name
            properties: Optional new properties
            
        Returns:
            Updated component response
            
        Raises:
            ComponentError: If update fails
        """
        try:
            logger.info(f"Updating component: component_id={component_id}")
            
            request_data = {}
            
            if name is not None:
                request_data['name'] = name
            
            if properties is not None:
                request_data['properties'] = properties
            
            response = self.api_client.put(f'/components/{component_id}', json=request_data)
            
            logger.info(f"Component {component_id} updated successfully")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to update component {component_id}: {str(e)}")
            raise ComponentError(f"Failed to update component: {str(e)}")

    def delete_component(self, component_id: int) -> bool:
        """
        Delete a component
        
        Args:
            component_id: Component ID to delete
            
        Returns:
            True if deletion successful
            
        Raises:
            ComponentError: If deletion fails
        """
        try:
            logger.info(f"Deleting component: component_id={component_id}")
            
            self.api_client.delete(f'/components/{component_id}')
            
            logger.info(f"Component {component_id} deleted successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete component {component_id}: {str(e)}")
            raise ComponentError(f"Failed to delete component: {str(e)}")

    def get_component_types(self) -> List[Dict[str, Any]]:
        """
        Get all component types with statistics
        
        Returns:
            List of component types with counts
            
        Raises:
            ComponentError: If retrieval fails
        """
        try:
            logger.info("Getting component types")
            
            response = self.api_client.get('/components/types')
            
            types_count = len(response) if isinstance(response, list) else 0
            logger.info(f"Retrieved {types_count} component types")
            
            return response if isinstance(response, list) else []
            
        except Exception as e:
            logger.error(f"Failed to get component types: {str(e)}")
            raise ComponentError(f"Failed to get component types: {str(e)}")

    def get_component_children(self, component_id: int) -> Dict[str, Any]:
        """
        Get all child components
        
        Args:
            component_id: Parent component ID
            
        Returns:
            Component list response with children
            
        Raises:
            ComponentError: If retrieval fails
        """
        try:
            logger.info(f"Getting children for component: component_id={component_id}")
            
            response = self.api_client.get(f'/components/{component_id}/children')
            
            children_count = len(response.get('components', []))
            logger.info(f"Retrieved {children_count} child components")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get component children: {str(e)}")
            raise ComponentError(f"Failed to get component children: {str(e)}")

    def get_component_files(
        self,
        component_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get all files associated with a component
        
        Args:
            component_id: Component ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Files associated with the component
            
        Raises:
            ComponentError: If retrieval fails
        """
        try:
            logger.info(f"Getting files for component: component_id={component_id}")
            
            params = {
                'skip': skip,
                'limit': limit
            }
            
            response = self.api_client.get(f'/components/{component_id}/files', params=params)
            
            logger.info(f"Retrieved files for component {component_id}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get component files: {str(e)}")
            raise ComponentError(f"Failed to get component files: {str(e)}")

    def get_all_components(self) -> List[Dict[str, Any]]:
        """
        Get all components (handles pagination automatically)
        
        Returns:
            List of all components
            
        Raises:
            ComponentError: If retrieval fails
        """
        try:
            logger.info("Retrieving all components")
            
            all_components = []
            skip = 0
            limit = 100
            
            while True:
                response = self.list_components(skip=skip, limit=limit)
                components = response.get('components', [])
                
                if not components:
                    break
                
                all_components.extend(components)
                skip += limit
                
                # Check if we've retrieved all components
                if len(all_components) >= response.get('total', 0):
                    break
            
            logger.info(f"Retrieved all {len(all_components)} components")
            
            return all_components
            
        except Exception as e:
            logger.error(f"Failed to get all components: {str(e)}")
            raise ComponentError(f"Failed to get all components: {str(e)}")

    def get_components_by_type(self, component_type: str) -> List[Dict[str, Any]]:
        """
        Get all components of a specific type
        
        Args:
            component_type: Type of components to retrieve
            
        Returns:
            List of components matching the type
            
        Raises:
            ComponentError: If retrieval fails
        """
        try:
            logger.info(f"Getting components of type: {component_type}")
            
            response = self.list_components(component_type=component_type, limit=1000)
            components = response.get('components', [])
            
            logger.info(f"Found {len(components)} components of type {component_type}")
            
            return components
            
        except Exception as e:
            logger.error(f"Failed to get components by type: {str(e)}")
            raise ComponentError(f"Failed to get components by type: {str(e)}")

    def search_components_by_name(self, name_pattern: str) -> List[Dict[str, Any]]:
        """
        Search components by name pattern
        
        Args:
            name_pattern: Name pattern to search for
            
        Returns:
            List of matching components
            
        Raises:
            ComponentError: If search fails
        """
        try:
            logger.info(f"Searching components by name: '{name_pattern}'")
            
            all_components = self.get_all_components()
            
            # Filter components by name pattern
            matching_components = [
                c for c in all_components
                if name_pattern.lower() in c.get('name', '').lower()
            ]
            
            logger.info(f"Found {len(matching_components)} matching components")
            
            return matching_components
            
        except Exception as e:
            logger.error(f"Failed to search components by name: {str(e)}")
            raise ComponentError(f"Failed to search components by name: {str(e)}")

    def get_component_statistics(self) -> Dict[str, Any]:
        """
        Get component statistics
        
        Returns:
            Statistics about components in the system
            
        Raises:
            ComponentError: If retrieval fails
        """
        try:
            logger.info("Getting component statistics")
            
            # Get component types with counts
            types = self.get_component_types()
            
            total_components = sum(t.get('count', 0) for t in types)
            
            statistics = {
                'total_components': total_components,
                'types': {t.get('component_type'): t.get('count', 0) for t in types}
            }
            
            logger.info(f"Component statistics: {total_components} total components")
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get component statistics: {str(e)}")
            raise ComponentError(f"Failed to get component statistics: {str(e)}")

# Made with Bob
