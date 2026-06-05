"""
Error handling utilities for CABP Client Application.
Defines custom exceptions and error handling logic.
"""

from typing import Optional, Dict, Any
import requests
from logger import get_logger

logger = get_logger(__name__)


class CABPClientError(Exception):
    """
    Base exception for CABP Client errors.
    
    All custom exceptions in the application inherit from this class.
    """
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize CABP Client error.
        
        Args:
            message: Error message
            details: Optional dictionary with additional error details
            original_error: Optional original exception that caused this error
        """
        self.message = message
        self.details = details or {}
        self.original_error = original_error
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """String representation of the error."""
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary format.
        
        Returns:
            Dictionary representation of the error
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class AuthenticationError(CABPClientError):
    """
    Raised when authentication fails.
    
    This includes invalid API keys, expired tokens, or insufficient permissions.
    """
    pass


class APIError(CABPClientError):
    """
    Raised when API request fails.
    
    This includes network errors, server errors, and invalid responses.
    """
    pass


class ValidationError(CABPClientError):
    """
    Raised when data validation fails.
    
    This includes invalid input parameters, malformed data, or constraint violations.
    """
    pass


class ConfigurationError(CABPClientError):
    """
    Raised when configuration is invalid or missing.
    
    This includes missing required settings or invalid configuration values.
    """
    pass


class FileOperationError(CABPClientError):
    """
    Raised when file operations fail.
    
    This includes file not found, permission denied, or I/O errors.
    """
    pass


class NetworkError(CABPClientError):
    """
    Raised when network operations fail.
    
    This includes connection timeouts, DNS failures, or network unavailability.
    """
    pass


class IngestionError(CABPClientError):
    """
    Raised when file ingestion operations fail.
    
    This includes file upload errors, processing failures, or validation issues.
    """
    pass


class SearchError(CABPClientError):
    """
    Raised when search operations fail.
    
    This includes query errors, result processing failures, or search service issues.
    """
    pass


class ManagementError(CABPClientError):
    """
    Raised when management operations fail.
    
    This includes file/document management errors or status check failures.
    """
    pass


class TopologyError(CABPClientError):
    """
    Raised when topology operations fail.
    
    This includes topology fetch errors or visualization failures.
    """
    pass


class HealthError(CABPClientError):
    """
    Raised when health check operations fail.
    
    This includes health status fetch errors or monitoring failures.
    """
    pass


class ComponentError(CABPClientError):
    """
    Raised when component operations fail.
    
    This includes component CRUD errors or relationship failures.
    """
    pass


class MappingError(CABPClientError):
    """
    Raised when mapping operations fail.
    
    This includes mapping creation, deletion, or query failures.
    """
    pass


def handle_api_error(response: requests.Response) -> None:
    """
    Handle API error responses and raise appropriate exceptions.
    
    Args:
        response: HTTP response object
        
    Raises:
        AuthenticationError: For 401/403 status codes
        APIError: For other error status codes
        
    Example:
        >>> response = requests.get(url)
        >>> if not response.ok:
        >>>     handle_api_error(response)
    """
    status_code = response.status_code
    
    # Authentication errors
    if status_code == 401:
        logger.error("Authentication failed: Invalid or expired API key")
        raise AuthenticationError(
            "Authentication failed: Invalid or expired API key",
            {"status_code": status_code, "url": response.url}
        )
    
    if status_code == 403:
        logger.error("Access forbidden: Insufficient permissions")
        raise AuthenticationError(
            "Access forbidden: Insufficient permissions",
            {"status_code": status_code, "url": response.url}
        )
    
    # Try to extract error details from response
    try:
        error_data = response.json()
        error_message = error_data.get("message", "Unknown error")
        error_details = error_data.get("details", {})
    except (ValueError, KeyError):
        error_message = response.text or "Unknown error"
        error_details = {}
    
    # Client errors (4xx)
    if 400 <= status_code < 500:
        logger.error(f"Client error {status_code}: {error_message}")
        raise APIError(
            f"Client error: {error_message}",
            {
                "status_code": status_code,
                "url": response.url,
                "details": error_details
            }
        )
    
    # Server errors (5xx)
    if status_code >= 500:
        logger.error(f"Server error {status_code}: {error_message}")
        raise APIError(
            f"Server error: {error_message}",
            {
                "status_code": status_code,
                "url": response.url,
                "details": error_details
            }
        )
    
    # Other errors
    logger.error(f"API error {status_code}: {error_message}")
    raise APIError(
        f"API request failed: {error_message}",
        {
            "status_code": status_code,
            "url": response.url,
            "details": error_details
        }
    )


def handle_request_exception(error: Exception, url: str) -> None:
    """
    Handle request exceptions and raise appropriate custom exceptions.
    
    Args:
        error: Original exception
        url: URL that was being accessed
        
    Raises:
        NetworkError: For network-related errors
        APIError: For other request errors
    """
    if isinstance(error, requests.exceptions.Timeout):
        logger.error(f"Request timeout: {url}")
        raise NetworkError(
            "Request timeout",
            {"url": url, "timeout": True},
            original_error=error
        )
    
    if isinstance(error, requests.exceptions.ConnectionError):
        logger.error(f"Connection error: {url}")
        raise NetworkError(
            "Connection error: Unable to reach server",
            {"url": url, "connection_error": True},
            original_error=error
        )
    
    if isinstance(error, requests.exceptions.RequestException):
        logger.error(f"Request failed: {str(error)}")
        raise APIError(
            f"Request failed: {str(error)}",
            {"url": url},
            original_error=error
        )
    
    # Re-raise if it's already our custom exception
    if isinstance(error, CABPClientError):
        raise error
    
    # Wrap other exceptions
    logger.error(f"Unexpected error: {str(error)}")
    raise APIError(
        f"Unexpected error: {str(error)}",
        {"url": url},
        original_error=error
    )


def format_error_message(error: Exception) -> str:
    """
    Format error message for display to user.
    
    Args:
        error: Exception to format
        
    Returns:
        Formatted error message
        
    Example:
        >>> try:
        >>>     # some operation
        >>> except Exception as e:
        >>>     print(format_error_message(e))
    """
    if isinstance(error, CABPClientError):
        message = f"Error: {error.message}"
        if error.details:
            # Format details in a readable way
            details_str = ", ".join(
                f"{k}={v}" for k, v in error.details.items()
                if k not in ["url", "original_error"]
            )
            if details_str:
                message += f" ({details_str})"
        return message
    
    return f"Error: {str(error)}"


def log_error(error: Exception, context: Optional[str] = None) -> None:
    """
    Log error with appropriate level and context.
    
    Args:
        error: Exception to log
        context: Optional context string describing where error occurred
        
    Example:
        >>> try:
        >>>     # some operation
        >>> except Exception as e:
        >>>     log_error(e, "during file upload")
    """
    error_msg = format_error_message(error)
    
    if context:
        error_msg = f"{context}: {error_msg}"
    
    if isinstance(error, (AuthenticationError, ConfigurationError)):
        logger.error(error_msg)
    elif isinstance(error, ValidationError):
        logger.warning(error_msg)
    elif isinstance(error, CABPClientError):
        logger.error(error_msg, exc_info=True)
    else:
        logger.exception(error_msg)

# Made with Bob
