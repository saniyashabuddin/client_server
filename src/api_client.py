"""
HTTP client for CABP API communication.
Handles authentication, requests, response processing, and error handling.
"""

import time
from typing import Optional, Dict, Any, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import config
from logger import get_logger
from error_handler import (
    handle_api_error,
    handle_request_exception,
    APIError,
    NetworkError
)

logger = get_logger(__name__)


class APIClient:
    """
    HTTP client for CABP API interactions.
    
    Manages authentication, request handling, retry logic, and error processing.
    Provides a clean interface for making API calls with automatic error handling.
    
    Example:
        >>> client = APIClient()
        >>> response = client.get("/files")
        >>> files = response.get("files", [])
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ):
        """
        Initialize API client.
        
        Args:
            base_url: Optional API base URL (defaults to config.base_url)
            api_key: Optional API key (defaults to config.api_key)
            timeout: Optional request timeout (defaults to config.timeout)
            max_retries: Optional max retries (defaults to config.max_retries)
        """
        self.base_url = base_url if base_url else config.base_url
        self.base_url = self.base_url.rstrip('/')
        self.api_key = api_key if api_key else config.api_key
        self.timeout = timeout if timeout else config.timeout
        self.max_retries = max_retries if max_retries else config.max_retries
        self.session = self._create_session()
        
        logger.info(f"API Client initialized for {self.base_url}")
        logger.debug(f"Timeout: {self.timeout}s, Max retries: {self.max_retries}")
    
    def _create_session(self) -> requests.Session:
        """
        Create and configure requests session with retry logic.
        
        Returns:
            Configured session object with retry strategy
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
            raise_on_status=False
        )
        
        # Mount adapter with retry strategy
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "CABP-Client/1.0.0"
        })
        
        # Add authentication header if API key is available
        if self.api_key:
            session.headers.update({
                "Authorization": f"Bearer {self.api_key}"
            })
            logger.debug("Authentication header added to session")
        
        return session
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set or update API key for authentication.
        
        Args:
            api_key: API authentication key
        """
        self.api_key = api_key
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}"
        })
        logger.info("API key updated")
    
    def clear_api_key(self) -> None:
        """Clear API key from session."""
        self.api_key = None
        self.session.headers.pop("Authorization", None)
        logger.info("API key cleared")
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from endpoint.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Full URL
        """
        endpoint = endpoint.lstrip('/')
        return f"{self.base_url}/{endpoint}"
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with error handling and logging.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters (params, json, data, files, etc.)
            
        Returns:
            Response object
            
        Raises:
            NetworkError: If network/connection error occurs
            APIError: If API returns error response
        """
        url = self._build_url(endpoint)
        
        # Set timeout if not provided
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        logger.debug(f"{method} {url}")
        if 'params' in kwargs:
            logger.debug(f"Query params: {kwargs['params']}")
        if 'json' in kwargs:
            logger.debug(f"JSON payload: {kwargs['json']}")
        
        try:
            # Make the request
            response = self.session.request(
                method=method,
                url=url,
                **kwargs
            )
            
            logger.debug(f"Response: {response.status_code}")
            
            # Handle error responses
            if not response.ok:
                handle_api_error(response)
            
            return response
            
        except requests.exceptions.RequestException as e:
            handle_request_exception(e, url)
            raise  # This line won't be reached, but satisfies type checker
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform GET request.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            **kwargs: Additional request parameters
            
        Returns:
            Response data as dictionary
            
        Example:
            >>> client.get("/files", params={"limit": 10})
        """
        response = self._make_request("GET", endpoint, params=params, **kwargs)
        return self._parse_response(response)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform POST request.
        
        Args:
            endpoint: API endpoint path
            data: Optional form data
            json: Optional JSON data
            files: Optional files to upload
            **kwargs: Additional request parameters
            
        Returns:
            Response data as dictionary
            
        Example:
            >>> client.post("/ingest/metadata", json={"key": "value"})
        """
        # Remove Content-Type header for file uploads
        if files:
            headers = kwargs.get('headers', {})
            headers.pop('Content-Type', None)
            kwargs['headers'] = headers
        
        response = self._make_request(
            "POST",
            endpoint,
            data=data,
            json=json,
            files=files,
            **kwargs
        )
        return self._parse_response(response)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform PUT request.
        
        Args:
            endpoint: API endpoint path
            data: Optional form data
            json: Optional JSON data
            **kwargs: Additional request parameters
            
        Returns:
            Response data as dictionary
            
        Example:
            >>> client.put("/files/123", json={"name": "new_name"})
        """
        response = self._make_request(
            "PUT",
            endpoint,
            data=data,
            json=json,
            **kwargs
        )
        return self._parse_response(response)
    
    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform DELETE request.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            **kwargs: Additional request parameters
            
        Returns:
            Response data as dictionary (empty dict if no content)
            
        Example:
            >>> client.delete("/files/123")
        """
        response = self._make_request("DELETE", endpoint, params=params, **kwargs)
        return self._parse_response(response)
    
    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform PATCH request.
        
        Args:
            endpoint: API endpoint path
            data: Optional form data
            json: Optional JSON data
            **kwargs: Additional request parameters
            
        Returns:
            Response data as dictionary
            
        Example:
            >>> client.patch("/files/123", json={"status": "active"})
        """
        response = self._make_request(
            "PATCH",
            endpoint,
            data=data,
            json=json,
            **kwargs
        )
        return self._parse_response(response)
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Parse response and return data.
        
        Args:
            response: HTTP response object
            
        Returns:
            Parsed response data as dictionary
            
        Raises:
            APIError: If response cannot be parsed
        """
        # Handle empty responses
        if not response.content:
            logger.debug("Empty response received")
            return {}
        
        # Try to parse JSON
        try:
            data = response.json()
            logger.debug(f"Response data: {data}")
            return data
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise APIError(
                "Invalid JSON response from server",
                {"response_text": response.text[:200]},
                original_error=e
            )
    
    def health_check(self) -> bool:
        """
        Check if API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
            
        Example:
            >>> if client.health_check():
            >>>     print("API is accessible")
        """
        try:
            response = self.get("/health")
            return response.get("status") == "ok"
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False
    
    def close(self) -> None:
        """
        Close the session and cleanup resources.
        
        Should be called when done using the client.
        """
        if self.session:
            self.session.close()
            logger.info("API Client session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __repr__(self) -> str:
        """String representation of API client."""
        return f"APIClient(base_url='{self.base_url}')"

# Made with Bob
