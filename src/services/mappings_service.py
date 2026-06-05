"""
Mappings Service Module

Handles mapping operations between files and components including:
- Create mappings
- List mappings with filtering
- Delete mappings
- Query relationships
"""

from typing import Dict, Any, Optional, List

from api_client import APIClient
from logger import get_logger
from error_handler import MappingError

logger = get_logger(__name__)


class MappingsService:
    """Service for handling file-component mapping operations"""

    def __init__(self, api_client: APIClient):
        """
        Initialize mappings service
        
        Args:
            api_client: API client instance
        """
        self.api_client = api_client
        logger.info("Mappings service initialized")

    def create_mapping(
        self,
        file_id: int,
        component_id: int,
        relationship_type: str
    ) -> Dict[str, Any]:
        """
        Create a new mapping between file and component
        
        Args:
            file_id: File ID
            component_id: Component ID
            relationship_type: Type of relationship (backed_up_by, stored_in_pool, etc.)
            
        Returns:
            Created mapping response
            
        Raises:
            MappingError: If creation fails
        """
        try:
            logger.info(f"Creating mapping: file={file_id}, component={component_id}, type={relationship_type}")
            
            request_data = {
                'file_id': file_id,
                'component_id': component_id,
                'relationship_type': relationship_type
            }
            
            response = self.api_client.post('/mappings/', json=request_data)
            
            logger.info(f"Mapping created: id={response.get('id')}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to create mapping: {str(e)}")
            raise MappingError(f"Failed to create mapping: {str(e)}")

    def list_mappings(
        self,
        skip: int = 0,
        limit: int = 100,
        component_id: Optional[int] = None,
        file_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        List all mappings with optional filtering
        
        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            component_id: Optional component ID filter
            file_id: Optional file ID filter
            
        Returns:
            Mapping list response with total count and mappings
            
        Raises:
            MappingError: If listing fails
        """
        try:
            logger.info(f"Listing mappings (skip={skip}, limit={limit})")
            
            params = {
                'skip': skip,
                'limit': limit
            }
            
            if component_id is not None:
                params['component_id'] = component_id
            
            if file_id is not None:
                params['file_id'] = file_id
            
            response = self.api_client.get('/mappings/', params=params)
            
            total = response.get('total', 0)
            mappings_count = len(response.get('mappings', []))
            logger.info(f"Retrieved {mappings_count} mappings (total: {total})")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to list mappings: {str(e)}")
            raise MappingError(f"Failed to list mappings: {str(e)}")

    def delete_mapping(self, mapping_id: int) -> bool:
        """
        Delete a mapping
        
        Args:
            mapping_id: Mapping ID to delete
            
        Returns:
            True if deletion successful
            
        Raises:
            MappingError: If deletion fails
        """
        try:
            logger.info(f"Deleting mapping: mapping_id={mapping_id}")
            
            self.api_client.delete(f'/mappings/{mapping_id}')
            
            logger.info(f"Mapping {mapping_id} deleted successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete mapping {mapping_id}: {str(e)}")
            raise MappingError(f"Failed to delete mapping: {str(e)}")

    def get_file_mappings(self, file_id: int) -> List[Dict[str, Any]]:
        """
        Get all mappings for a specific file
        
        Args:
            file_id: File ID
            
        Returns:
            List of mappings for the file
            
        Raises:
            MappingError: If retrieval fails
        """
        try:
            logger.info(f"Getting mappings for file: file_id={file_id}")
            
            response = self.list_mappings(file_id=file_id, limit=1000)
            mappings = response.get('mappings', [])
            
            logger.info(f"Found {len(mappings)} mappings for file {file_id}")
            
            return mappings
            
        except Exception as e:
            logger.error(f"Failed to get file mappings: {str(e)}")
            raise MappingError(f"Failed to get file mappings: {str(e)}")

    def get_component_mappings(self, component_id: int) -> List[Dict[str, Any]]:
        """
        Get all mappings for a specific component
        
        Args:
            component_id: Component ID
            
        Returns:
            List of mappings for the component
            
        Raises:
            MappingError: If retrieval fails
        """
        try:
            logger.info(f"Getting mappings for component: component_id={component_id}")
            
            response = self.list_mappings(component_id=component_id, limit=1000)
            mappings = response.get('mappings', [])
            
            logger.info(f"Found {len(mappings)} mappings for component {component_id}")
            
            return mappings
            
        except Exception as e:
            logger.error(f"Failed to get component mappings: {str(e)}")
            raise MappingError(f"Failed to get component mappings: {str(e)}")

    def get_all_mappings(self) -> List[Dict[str, Any]]:
        """
        Get all mappings (handles pagination automatically)
        
        Returns:
            List of all mappings
            
        Raises:
            MappingError: If retrieval fails
        """
        try:
            logger.info("Retrieving all mappings")
            
            all_mappings = []
            skip = 0
            limit = 100
            
            while True:
                response = self.list_mappings(skip=skip, limit=limit)
                mappings = response.get('mappings', [])
                
                if not mappings:
                    break
                
                all_mappings.extend(mappings)
                skip += limit
                
                # Check if we've retrieved all mappings
                if len(all_mappings) >= response.get('total', 0):
                    break
            
            logger.info(f"Retrieved all {len(all_mappings)} mappings")
            
            return all_mappings
            
        except Exception as e:
            logger.error(f"Failed to get all mappings: {str(e)}")
            raise MappingError(f"Failed to get all mappings: {str(e)}")

    def get_mappings_by_relationship_type(
        self,
        relationship_type: str
    ) -> List[Dict[str, Any]]:
        """
        Get all mappings of a specific relationship type
        
        Args:
            relationship_type: Type of relationship to filter by
            
        Returns:
            List of mappings matching the relationship type
            
        Raises:
            MappingError: If retrieval fails
        """
        try:
            logger.info(f"Getting mappings by relationship type: {relationship_type}")
            
            all_mappings = self.get_all_mappings()
            
            # Filter by relationship type
            filtered_mappings = [
                m for m in all_mappings
                if m.get('relationship_type') == relationship_type
            ]
            
            logger.info(f"Found {len(filtered_mappings)} mappings of type {relationship_type}")
            
            return filtered_mappings
            
        except Exception as e:
            logger.error(f"Failed to get mappings by relationship type: {str(e)}")
            raise MappingError(f"Failed to get mappings by relationship type: {str(e)}")

    def get_file_components(self, file_id: int) -> List[Dict[str, Any]]:
        """
        Get all components associated with a file
        
        Args:
            file_id: File ID
            
        Returns:
            List of components associated with the file
            
        Raises:
            MappingError: If retrieval fails
        """
        try:
            logger.info(f"Getting components for file: file_id={file_id}")
            
            mappings = self.get_file_mappings(file_id)
            
            # Extract unique components
            components = []
            seen_ids = set()
            
            for mapping in mappings:
                comp_id = mapping.get('component_id')
                if comp_id and comp_id not in seen_ids:
                    components.append({
                        'component_id': comp_id,
                        'component_name': mapping.get('component_name'),
                        'relationship_type': mapping.get('relationship_type')
                    })
                    seen_ids.add(comp_id)
            
            logger.info(f"Found {len(components)} components for file {file_id}")
            
            return components
            
        except Exception as e:
            logger.error(f"Failed to get file components: {str(e)}")
            raise MappingError(f"Failed to get file components: {str(e)}")

    def get_component_files(self, component_id: int) -> List[Dict[str, Any]]:
        """
        Get all files associated with a component
        
        Args:
            component_id: Component ID
            
        Returns:
            List of files associated with the component
            
        Raises:
            MappingError: If retrieval fails
        """
        try:
            logger.info(f"Getting files for component: component_id={component_id}")
            
            mappings = self.get_component_mappings(component_id)
            
            # Extract unique files
            files = []
            seen_ids = set()
            
            for mapping in mappings:
                file_id = mapping.get('file_id')
                if file_id and file_id not in seen_ids:
                    files.append({
                        'file_id': file_id,
                        'file_name': mapping.get('file_name'),
                        'relationship_type': mapping.get('relationship_type')
                    })
                    seen_ids.add(file_id)
            
            logger.info(f"Found {len(files)} files for component {component_id}")
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to get component files: {str(e)}")
            raise MappingError(f"Failed to get component files: {str(e)}")

    def get_mapping_statistics(self) -> Dict[str, Any]:
        """
        Get mapping statistics
        
        Returns:
            Statistics about mappings in the system
            
        Raises:
            MappingError: If retrieval fails
        """
        try:
            logger.info("Getting mapping statistics")
            
            all_mappings = self.get_all_mappings()
            
            # Count by relationship type
            relationship_counts = {}
            for mapping in all_mappings:
                rel_type = mapping.get('relationship_type', 'unknown')
                relationship_counts[rel_type] = relationship_counts.get(rel_type, 0) + 1
            
            statistics = {
                'total_mappings': len(all_mappings),
                'by_relationship_type': relationship_counts
            }
            
            logger.info(f"Mapping statistics: {len(all_mappings)} total mappings")
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get mapping statistics: {str(e)}")
            raise MappingError(f"Failed to get mapping statistics: {str(e)}")

    def delete_file_mappings(self, file_id: int) -> int:
        """
        Delete all mappings for a file
        
        Args:
            file_id: File ID
            
        Returns:
            Number of mappings deleted
            
        Raises:
            MappingError: If deletion fails
        """
        try:
            logger.info(f"Deleting all mappings for file: file_id={file_id}")
            
            mappings = self.get_file_mappings(file_id)
            deleted_count = 0
            
            for mapping in mappings:
                mapping_id = mapping.get('id')
                if mapping_id:
                    self.delete_mapping(mapping_id)
                    deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} mappings for file {file_id}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete file mappings: {str(e)}")
            raise MappingError(f"Failed to delete file mappings: {str(e)}")

    def delete_component_mappings(self, component_id: int) -> int:
        """
        Delete all mappings for a component
        
        Args:
            component_id: Component ID
            
        Returns:
            Number of mappings deleted
            
        Raises:
            MappingError: If deletion fails
        """
        try:
            logger.info(f"Deleting all mappings for component: component_id={component_id}")
            
            mappings = self.get_component_mappings(component_id)
            deleted_count = 0
            
            for mapping in mappings:
                mapping_id = mapping.get('id')
                if mapping_id:
                    self.delete_mapping(mapping_id)
                    deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} mappings for component {component_id}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete component mappings: {str(e)}")
            raise MappingError(f"Failed to delete component mappings: {str(e)}")

# Made with Bob
