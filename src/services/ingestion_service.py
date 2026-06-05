"""
Ingestion Service Module

Handles file and document ingestion operations including:
- Single file upload
- Chunked file upload for large files
- Metadata ingestion
- Batch operations
"""

import os
import json
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path

from api_client import APIClient
from logger import get_logger
from error_handler import IngestionError

logger = get_logger(__name__)


class IngestionService:
    """Service for handling file and document ingestion"""

    def __init__(self, api_client: APIClient):
        """
        Initialize ingestion service
        
        Args:
            api_client: API client instance
        """
        self.api_client = api_client
        logger.info("Ingestion service initialized")

    def ingest_file(
        self,
        file_path: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ingest a single file
        
        Args:
            file_path: Path to file to ingest
            metadata: File metadata
            
        Returns:
            Ingestion response with file_id and statistics
            
        Raises:
            IngestionError: If ingestion fails
        """
        try:
            if not os.path.exists(file_path):
                raise IngestionError(f"File not found: {file_path}")
            
            file_size = os.path.getsize(file_path)
            logger.info(f"Ingesting file: {file_path} ({file_size} bytes)")
            
            # Prepare multipart form data
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                data = {'metadata': json.dumps(metadata)}
                
                response = self.api_client.post(
                    '/ingest/file',
                    files=files,
                    data=data
                )
            
            logger.info(f"File ingested successfully: file_id={response.get('file_id')}")
            return response
            
        except Exception as e:
            logger.error(f"File ingestion failed: {str(e)}")
            raise IngestionError(f"Failed to ingest file: {str(e)}")

    def init_chunked_upload(
        self,
        file_path: str,
        metadata: Dict[str, Any],
        chunk_size: int = 5 * 1024 * 1024  # 5MB default
    ) -> Dict[str, Any]:
        """
        Initialize chunked upload session for large files
        
        Args:
            file_path: Path to file
            metadata: File metadata
            chunk_size: Size of each chunk in bytes
            
        Returns:
            Upload session details with upload_id
            
        Raises:
            IngestionError: If initialization fails
        """
        try:
            if not os.path.exists(file_path):
                raise IngestionError(f"File not found: {file_path}")
            
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            file_type = Path(file_path).suffix.lstrip('.')
            
            logger.info(f"Initializing chunked upload: {file_name} ({file_size} bytes)")
            
            request_data = {
                'file_name': file_name,
                'file_size': file_size,
                'file_type': file_type,
                'chunk_size': chunk_size,
                'metadata': metadata
            }
            
            response = self.api_client.post('/ingest/chunked/init', json=request_data)
            
            logger.info(f"Chunked upload initialized: upload_id={response.get('upload_id')}")
            return response
            
        except Exception as e:
            logger.error(f"Chunked upload initialization failed: {str(e)}")
            raise IngestionError(f"Failed to initialize chunked upload: {str(e)}")

    def upload_chunk(
        self,
        upload_id: str,
        file_path: str,
        chunk_index: int,
        chunk_size: int = 5 * 1024 * 1024
    ) -> Dict[str, Any]:
        """
        Upload a single chunk
        
        Args:
            upload_id: Upload session ID
            file_path: Path to file
            chunk_index: Index of chunk to upload (0-based)
            chunk_size: Size of each chunk
            
        Returns:
            Chunk upload response
            
        Raises:
            IngestionError: If upload fails
        """
        try:
            offset = chunk_index * chunk_size
            
            with open(file_path, 'rb') as f:
                f.seek(offset)
                chunk_data = f.read(chunk_size)
            
            if not chunk_data:
                raise IngestionError(f"No data at chunk index {chunk_index}")
            
            logger.debug(f"Uploading chunk {chunk_index} ({len(chunk_data)} bytes)")
            
            files = {'chunk': ('chunk', chunk_data)}
            data = {
                'upload_id': upload_id,
                'chunk_index': chunk_index
            }
            
            response = self.api_client.post(
                '/ingest/chunked/upload',
                files=files,
                data=data
            )
            
            logger.debug(f"Chunk {chunk_index} uploaded successfully")
            return response
            
        except Exception as e:
            logger.error(f"Chunk upload failed: {str(e)}")
            raise IngestionError(f"Failed to upload chunk: {str(e)}")

    def finalize_chunked_upload(self, upload_id: str) -> Dict[str, Any]:
        """
        Finalize chunked upload and trigger processing
        
        Args:
            upload_id: Upload session ID
            
        Returns:
            Finalization response with file_id
            
        Raises:
            IngestionError: If finalization fails
        """
        try:
            logger.info(f"Finalizing chunked upload: {upload_id}")
            
            response = self.api_client.post(
                '/ingest/chunked/finalize',
                json={'upload_id': upload_id}
            )
            
            logger.info(f"Chunked upload finalized: file_id={response.get('file_id')}")
            return response
            
        except Exception as e:
            logger.error(f"Chunked upload finalization failed: {str(e)}")
            raise IngestionError(f"Failed to finalize upload: {str(e)}")

    def ingest_large_file(
        self,
        file_path: str,
        metadata: Dict[str, Any],
        chunk_size: int = 5 * 1024 * 1024,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Ingest a large file using chunked upload
        
        Args:
            file_path: Path to file
            metadata: File metadata
            chunk_size: Size of each chunk
            progress_callback: Optional callback for progress updates
            
        Returns:
            Final ingestion response
            
        Raises:
            IngestionError: If ingestion fails
        """
        try:
            # Initialize upload
            init_response = self.init_chunked_upload(file_path, metadata, chunk_size)
            upload_id = init_response['upload_id']
            total_chunks = init_response['total_chunks']
            
            logger.info(f"Uploading {total_chunks} chunks for {file_path}")
            
            # Upload chunks
            for chunk_index in range(total_chunks):
                chunk_response = self.upload_chunk(
                    upload_id,
                    file_path,
                    chunk_index,
                    chunk_size
                )
                
                if progress_callback:
                    progress = ((chunk_index + 1) / total_chunks) * 100
                    progress_callback(chunk_index + 1, total_chunks, progress)
            
            # Finalize upload
            final_response = self.finalize_chunked_upload(upload_id)
            
            logger.info(f"Large file ingestion completed: file_id={final_response.get('file_id')}")
            return final_response
            
        except Exception as e:
            logger.error(f"Large file ingestion failed: {str(e)}")
            raise IngestionError(f"Failed to ingest large file: {str(e)}")

    def batch_ingest(
        self,
        file_paths: List[str],
        metadata_list: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Batch ingest multiple files
        
        Args:
            file_paths: List of file paths
            metadata_list: List of metadata dicts (one per file)
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of ingestion responses
            
        Raises:
            IngestionError: If batch ingestion fails
        """
        try:
            if len(file_paths) != len(metadata_list):
                raise IngestionError("Number of files and metadata entries must match")
            
            logger.info(f"Starting batch ingestion of {len(file_paths)} files")
            
            results = []
            total_files = len(file_paths)
            
            for idx, (file_path, metadata) in enumerate(zip(file_paths, metadata_list)):
                try:
                    # Determine if file needs chunked upload (> 10MB)
                    file_size = os.path.getsize(file_path)
                    
                    if file_size > 10 * 1024 * 1024:  # 10MB threshold
                        result = self.ingest_large_file(file_path, metadata)
                    else:
                        result = self.ingest_file(file_path, metadata)
                    
                    results.append({
                        'success': True,
                        'file_path': file_path,
                        'result': result
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to ingest {file_path}: {str(e)}")
                    results.append({
                        'success': False,
                        'file_path': file_path,
                        'error': str(e)
                    })
                
                if progress_callback:
                    progress = ((idx + 1) / total_files) * 100
                    progress_callback(idx + 1, total_files, progress)
            
            successful = sum(1 for r in results if r['success'])
            logger.info(f"Batch ingestion completed: {successful}/{total_files} successful")
            
            return results
            
        except Exception as e:
            logger.error(f"Batch ingestion failed: {str(e)}")
            raise IngestionError(f"Failed to batch ingest files: {str(e)}")

    def ingest_metadata_only(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingest metadata without a file (for reference purposes)
        
        Args:
            metadata: Metadata to ingest
            
        Returns:
            Ingestion response
            
        Raises:
            IngestionError: If ingestion fails
        """
        try:
            logger.info("Ingesting metadata only")
            
            # Create a minimal file with metadata
            response = self.api_client.post(
                '/ingest/metadata',
                json=metadata
            )
            
            logger.info("Metadata ingested successfully")
            return response
            
        except Exception as e:
            logger.error(f"Metadata ingestion failed: {str(e)}")
            raise IngestionError(f"Failed to ingest metadata: {str(e)}")

# Made with Bob
