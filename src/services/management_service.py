"""
Management Service Module

Handles file and document management operations including:
- List files and documents
- View file/document details
- Delete files and documents
- Get document chunks
- Monitor ingestion status
"""

from typing import Dict, Any, Optional, List

from api_client import APIClient
from logger import get_logger
from error_handler import ManagementError

logger = get_logger(__name__)


class ManagementService:
    """Service for handling file and document management"""

    def __init__(self, api_client: APIClient):
        """
        Initialize management service
        
        Args:
            api_client: API client instance
        """
        self.api_client = api_client
        logger.info("Management service initialized")

    def list_files(
        self,
        skip: int = 0,
        limit: int = 100,
        component_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        List all files with optional filtering
        
        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            component_id: Optional component ID filter
            
        Returns:
            File list response with total count and files
            
        Raises:
            ManagementError: If listing fails
        """
        try:
            logger.info(f"Listing files (skip={skip}, limit={limit})")
            
            params = {
                'skip': skip,
                'limit': limit
            }
            
            if component_id is not None:
                params['component_id'] = component_id
            
            response = self.api_client.get('/management/files', params=params)
            
            total = response.get('total', 0)
            files_count = len(response.get('files', []))
            logger.info(f"Retrieved {files_count} files (total: {total})")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to list files: {str(e)}")
            raise ManagementError(f"Failed to list files: {str(e)}")

    def get_file(self, file_id: int) -> Dict[str, Any]:
        """
        Get file details by ID
        
        Args:
            file_id: File ID
            
        Returns:
            File details
            
        Raises:
            ManagementError: If retrieval fails
        """
        try:
            logger.info(f"Getting file details: file_id={file_id}")
            
            response = self.api_client.get(f'/management/files/{file_id}')
            
            logger.info(f"Retrieved file: {response.get('file_name')}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get file {file_id}: {str(e)}")
            raise ManagementError(f"Failed to get file: {str(e)}")

    def delete_file(self, file_id: int) -> bool:
        """
        Delete a file and all associated data
        
        Args:
            file_id: File ID to delete
            
        Returns:
            True if deletion successful
            
        Raises:
            ManagementError: If deletion fails
        """
        try:
            logger.info(f"Deleting file: file_id={file_id}")
            
            self.api_client.delete(f'/management/files/{file_id}')
            
            logger.info(f"File {file_id} deleted successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file {file_id}: {str(e)}")
            raise ManagementError(f"Failed to delete file: {str(e)}")

    def list_documents(
        self,
        skip: int = 0,
        limit: int = 100,
        file_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        List all documents with optional filtering
        
        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            file_id: Optional file ID filter
            
        Returns:
            Document list response with total count and documents
            
        Raises:
            ManagementError: If listing fails
        """
        try:
            logger.info(f"Listing documents (skip={skip}, limit={limit})")
            
            params = {
                'skip': skip,
                'limit': limit
            }
            
            if file_id is not None:
                params['file_id'] = file_id
            
            response = self.api_client.get('/management/documents', params=params)
            
            total = response.get('total', 0)
            docs_count = len(response.get('documents', []))
            logger.info(f"Retrieved {docs_count} documents (total: {total})")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to list documents: {str(e)}")
            raise ManagementError(f"Failed to list documents: {str(e)}")

    def get_document(self, document_id: int) -> Dict[str, Any]:
        """
        Get document details by ID
        
        Args:
            document_id: Document ID
            
        Returns:
            Document details with content
            
        Raises:
            ManagementError: If retrieval fails
        """
        try:
            logger.info(f"Getting document details: document_id={document_id}")
            
            response = self.api_client.get(f'/management/documents/{document_id}')
            
            logger.info(f"Retrieved document: {response.get('file_name')}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get document {document_id}: {str(e)}")
            raise ManagementError(f"Failed to get document: {str(e)}")

    def get_document_chunks(self, document_id: int) -> List[Dict[str, Any]]:
        """
        Get all chunks for a document
        
        Args:
            document_id: Document ID
            
        Returns:
            List of document chunks
            
        Raises:
            ManagementError: If retrieval fails
        """
        try:
            logger.info(f"Getting chunks for document: document_id={document_id}")
            
            response = self.api_client.get(f'/management/documents/{document_id}/chunks')
            
            # Ensure response is a list
            if not isinstance(response, list):
                response = []
            
            chunks_count = len(response)
            logger.info(f"Retrieved {chunks_count} chunks")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get chunks for document {document_id}: {str(e)}")
            raise ManagementError(f"Failed to get document chunks: {str(e)}")

    def get_all_files(self) -> List[Dict[str, Any]]:
        """
        Get all files (handles pagination automatically)
        
        Returns:
            List of all files
            
        Raises:
            ManagementError: If retrieval fails
        """
        try:
            logger.info("Retrieving all files")
            
            all_files = []
            skip = 0
            limit = 100
            
            while True:
                response = self.list_files(skip=skip, limit=limit)
                files = response.get('files', [])
                
                if not files:
                    break
                
                all_files.extend(files)
                skip += limit
                
                # Check if we've retrieved all files
                if len(all_files) >= response.get('total', 0):
                    break
            
            logger.info(f"Retrieved all {len(all_files)} files")
            
            return all_files
            
        except Exception as e:
            logger.error(f"Failed to get all files: {str(e)}")
            raise ManagementError(f"Failed to get all files: {str(e)}")

    def get_all_documents(self, file_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all documents (handles pagination automatically)
        
        Args:
            file_id: Optional file ID filter
            
        Returns:
            List of all documents
            
        Raises:
            ManagementError: If retrieval fails
        """
        try:
            logger.info(f"Retrieving all documents{f' for file {file_id}' if file_id else ''}")
            
            all_documents = []
            skip = 0
            limit = 100
            
            while True:
                response = self.list_documents(skip=skip, limit=limit, file_id=file_id)
                documents = response.get('documents', [])
                
                if not documents:
                    break
                
                all_documents.extend(documents)
                skip += limit
                
                # Check if we've retrieved all documents
                if len(all_documents) >= response.get('total', 0):
                    break
            
            logger.info(f"Retrieved all {len(all_documents)} documents")
            
            return all_documents
            
        except Exception as e:
            logger.error(f"Failed to get all documents: {str(e)}")
            raise ManagementError(f"Failed to get all documents: {str(e)}")

    def get_file_statistics(self) -> Dict[str, Any]:
        """
        Get file statistics
        
        Returns:
            Statistics about files in the system
            
        Raises:
            ManagementError: If retrieval fails
        """
        try:
            logger.info("Getting file statistics")
            
            response = self.list_files(skip=0, limit=1)
            total_files = response.get('total', 0)
            
            # Get all files to calculate statistics
            all_files = self.get_all_files()
            
            # Calculate statistics
            total_size = sum(f.get('file_size', 0) for f in all_files)
            file_types = {}
            
            for file in all_files:
                file_type = file.get('file_type', 'unknown')
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            statistics = {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'file_types': file_types
            }
            
            logger.info(f"File statistics: {total_files} files, {statistics['total_size_mb']} MB")
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get file statistics: {str(e)}")
            raise ManagementError(f"Failed to get file statistics: {str(e)}")

    def search_files_by_name(self, name_pattern: str) -> List[Dict[str, Any]]:
        """
        Search files by name pattern
        
        Args:
            name_pattern: Name pattern to search for
            
        Returns:
            List of matching files
            
        Raises:
            ManagementError: If search fails
        """
        try:
            logger.info(f"Searching files by name: '{name_pattern}'")
            
            all_files = self.get_all_files()
            
            # Filter files by name pattern
            matching_files = [
                f for f in all_files
                if name_pattern.lower() in f.get('file_name', '').lower()
            ]
            
            logger.info(f"Found {len(matching_files)} matching files")
            
            return matching_files
            
        except Exception as e:
            logger.error(f"Failed to search files by name: {str(e)}")
            raise ManagementError(f"Failed to search files by name: {str(e)}")

    def get_recent_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most recently created files
        
        Args:
            limit: Number of files to return
            
        Returns:
            List of recent files
            
        Raises:
            ManagementError: If retrieval fails
        """
        try:
            logger.info(f"Getting {limit} most recent files")
            
            response = self.list_files(skip=0, limit=limit)
            files = response.get('files', [])
            
            # Sort by created_at (assuming files are already sorted by backend)
            logger.info(f"Retrieved {len(files)} recent files")
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to get recent files: {str(e)}")
            raise ManagementError(f"Failed to get recent files: {str(e)}")

# Made with Bob
