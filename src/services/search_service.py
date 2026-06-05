"""
Search Service Module

Handles search and query operations including:
- Semantic search
- Keyword search
- AI-powered query with context
- Advanced filtering
"""

from typing import Dict, Any, Optional, List

from api_client import APIClient
from logger import get_logger
from error_handler import SearchError

logger = get_logger(__name__)


class SearchService:
    """Service for handling search and query operations"""

    def __init__(self, api_client: APIClient):
        """
        Initialize search service
        
        Args:
            api_client: API client instance
        """
        self.api_client = api_client
        logger.info("Search service initialized")

    def search(
        self,
        query: str,
        max_results: int = 10,
        similarity_threshold: float = 0.3,
        metadata_filters: Optional[Dict[str, Any]] = None,
        include_ai_response: bool = True
    ) -> Dict[str, Any]:
        """
        Perform semantic search
        
        Args:
            query: Search query text
            max_results: Maximum number of results to return
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            metadata_filters: Optional metadata filters
            include_ai_response: Whether to include AI summary
            
        Returns:
            Search response with results and optional AI summary
            
        Raises:
            SearchError: If search fails
        """
        try:
            logger.info(f"Performing search: '{query}' (max_results={max_results})")
            
            request_data = {
                'query': query,
                'max_results': max_results,
                'similarity_threshold': similarity_threshold,
                'include_ai_response': include_ai_response
            }
            
            if metadata_filters:
                request_data['metadata_filters'] = metadata_filters
            
            response = self.api_client.post('/search/', json=request_data)
            
            results_count = response.get('results_count', 0)
            logger.info(f"Search completed: {results_count} results found")
            
            return response
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise SearchError(f"Failed to perform search: {str(e)}")

    def query_with_ai(
        self,
        query: str,
        max_results: int = 5,
        similarity_threshold: float = 0.3,
        metadata_filters: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Query with AI-generated response
        
        Args:
            query: Question or query text
            max_results: Number of context chunks to use
            similarity_threshold: Minimum similarity score
            metadata_filters: Optional metadata filters
            model: Ollama model to use (default: llama3.2)
            temperature: Model temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Query response with AI-generated answer and sources
            
        Raises:
            SearchError: If query fails
        """
        try:
            logger.info(f"Querying with AI: '{query}'")
            
            request_data = {
                'query': query,
                'max_results': max_results,
                'similarity_threshold': similarity_threshold,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            if metadata_filters:
                request_data['metadata_filters'] = metadata_filters
            
            if model:
                request_data['model'] = model
            
            response = self.api_client.post('/search/query', json=request_data)
            
            logger.info(f"AI query completed: {len(response.get('sources', []))} sources used")
            
            return response
            
        except Exception as e:
            logger.error(f"AI query failed: {str(e)}")
            raise SearchError(f"Failed to query with AI: {str(e)}")

    def semantic_search(
        self,
        query: str,
        max_results: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search and return results list
        
        Args:
            query: Search query
            max_results: Maximum results
            filters: Optional filters
            
        Returns:
            List of search results
            
        Raises:
            SearchError: If search fails
        """
        try:
            response = self.search(
                query=query,
                max_results=max_results,
                metadata_filters=filters,
                include_ai_response=False
            )
            
            return response.get('results', [])
            
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            raise SearchError(f"Failed to perform semantic search: {str(e)}")

    def keyword_search(
        self,
        keywords: List[str],
        max_results: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform keyword-based search
        
        Args:
            keywords: List of keywords to search for
            max_results: Maximum results
            filters: Optional filters
            
        Returns:
            List of search results
            
        Raises:
            SearchError: If search fails
        """
        try:
            # Combine keywords into query
            query = " ".join(keywords)
            logger.info(f"Performing keyword search: {keywords}")
            
            return self.semantic_search(query, max_results, filters)
            
        except Exception as e:
            logger.error(f"Keyword search failed: {str(e)}")
            raise SearchError(f"Failed to perform keyword search: {str(e)}")

    def advanced_search(
        self,
        query: str,
        product_name: Optional[str] = None,
        product_version: Optional[str] = None,
        os_version: Optional[str] = None,
        backup_type: Optional[str] = None,
        backup_product: Optional[str] = None,
        tags: Optional[List[str]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        max_results: int = 10,
        similarity_threshold: float = 0.3
    ) -> Dict[str, Any]:
        """
        Perform advanced search with multiple filters
        
        Args:
            query: Search query
            product_name: Filter by product name
            product_version: Filter by product version
            os_version: Filter by OS version
            backup_type: Filter by backup type (full, differential, incremental)
            backup_product: Filter by backup product
            tags: Filter by tags
            date_from: Filter by date from (ISO format)
            date_to: Filter by date to (ISO format)
            max_results: Maximum results
            similarity_threshold: Minimum similarity score
            
        Returns:
            Search response with filtered results
            
        Raises:
            SearchError: If search fails
        """
        try:
            logger.info(f"Performing advanced search: '{query}'")
            
            # Build metadata filters
            metadata_filters = {}
            
            if product_name:
                metadata_filters['product_name'] = product_name
            if product_version:
                metadata_filters['product_version'] = product_version
            if os_version:
                metadata_filters['os_version'] = os_version
            if backup_type:
                metadata_filters['backup_type'] = backup_type
            if backup_product:
                metadata_filters['backup_product'] = backup_product
            if tags:
                metadata_filters['tags'] = tags
            if date_from:
                metadata_filters['date_from'] = date_from
            if date_to:
                metadata_filters['date_to'] = date_to
            
            response = self.search(
                query=query,
                max_results=max_results,
                similarity_threshold=similarity_threshold,
                metadata_filters=metadata_filters if metadata_filters else None
            )
            
            logger.info(f"Advanced search completed: {response.get('results_count', 0)} results")
            
            return response
            
        except Exception as e:
            logger.error(f"Advanced search failed: {str(e)}")
            raise SearchError(f"Failed to perform advanced search: {str(e)}")

    def search_by_file_type(
        self,
        query: str,
        file_type: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search within specific file type
        
        Args:
            query: Search query
            file_type: File type to filter by
            max_results: Maximum results
            
        Returns:
            List of search results
            
        Raises:
            SearchError: If search fails
        """
        try:
            logger.info(f"Searching in {file_type} files: '{query}'")
            
            # Note: file_type filtering would need to be added to metadata_filters
            # This is a placeholder implementation
            response = self.search(query=query, max_results=max_results)
            
            # Filter results by file type
            results = response.get('results', [])
            filtered_results = [
                r for r in results
                if r.get('file_name', '').endswith(f'.{file_type}')
            ]
            
            logger.info(f"Found {len(filtered_results)} results in {file_type} files")
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"File type search failed: {str(e)}")
            raise SearchError(f"Failed to search by file type: {str(e)}")

    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """
        Get search suggestions based on partial query
        
        Args:
            partial_query: Partial search query
            
        Returns:
            List of suggested queries
            
        Note:
            This is a placeholder. Actual implementation would require
            a suggestions endpoint in the backend.
        """
        try:
            logger.info(f"Getting search suggestions for: '{partial_query}'")
            
            # Placeholder implementation
            # In a real implementation, this would call a suggestions endpoint
            suggestions = []
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get search suggestions: {str(e)}")
            return []

# Made with Bob
