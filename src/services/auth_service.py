"""
Authentication service for CABP Client Application.
Handles user authentication and token management.
"""

from typing import Dict, Any, Optional
from api_client import APIClient
from logger import get_logger
from error_handler import AuthenticationError

logger = get_logger(__name__)


class AuthService:
    """
    Service for handling authentication operations.
    
    Manages API key authentication, token validation, and session management.
    
    Example:
        >>> auth_service = AuthService(api_client)
        >>> result = auth_service.authenticate("my_api_key")
        >>> if result["success"]:
        >>>     print("Authenticated successfully")
    """
    
    def __init__(self, api_client: APIClient):
        """
        Initialize authentication service.
        
        Args:
            api_client: API client instance for making requests
        """
        self.api_client = api_client
        self.token: Optional[str] = None
        self.authenticated = False
        logger.info("Authentication service initialized")
    
    def authenticate(self, api_key: str) -> Dict[str, Any]:
        """
        Authenticate user with API key.
        
        Args:
            api_key: User API key for authentication
            
        Returns:
            Authentication response containing token and expiry
            
        Raises:
            AuthenticationError: If authentication fails
            
        Example:
            >>> result = auth_service.authenticate("my_api_key")
            >>> token = result["token"]
        """
        logger.info("Attempting authentication")
        
        try:
            # Set API key in client
            self.api_client.set_api_key(api_key)
            
            # Make authentication request
            response = self.api_client.post(
                "/auth/login",
                json={"api_key": api_key}
            )
            
            # Store token
            self.token = response.get("token")
            self.authenticated = True
            
            logger.info("Authentication successful")
            return {
                "success": True,
                "token": self.token,
                "expires_at": response.get("expires_at"),
                "message": "Authentication successful"
            }
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            self.authenticated = False
            self.token = None
            raise AuthenticationError(
                f"Authentication failed: {str(e)}",
                original_error=e
            )
    
    def validate_token(self) -> bool:
        """
        Validate current authentication token.
        
        Returns:
            True if token is valid, False otherwise
            
        Example:
            >>> if auth_service.validate_token():
            >>>     print("Token is valid")
        """
        if not self.token:
            logger.warning("No token to validate")
            return False
        
        try:
            logger.debug("Validating authentication token")
            response = self.api_client.get("/auth/validate")
            
            is_valid = response.get("valid", False)
            
            if is_valid:
                logger.debug("Token is valid")
            else:
                logger.warning("Token is invalid or expired")
                self.authenticated = False
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            self.authenticated = False
            return False
    
    def refresh_token(self) -> str:
        """
        Refresh authentication token.
        
        Returns:
            New authentication token
            
        Raises:
            AuthenticationError: If refresh fails
            
        Example:
            >>> new_token = auth_service.refresh_token()
        """
        logger.info("Refreshing authentication token")
        
        if not self.authenticated:
            raise AuthenticationError("Not authenticated. Please login first.")
        
        try:
            response = self.api_client.post("/auth/refresh")
            
            self.token = response.get("token")
            logger.info("Token refreshed successfully")
            
            return self.token
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            self.authenticated = False
            raise AuthenticationError(
                f"Token refresh failed: {str(e)}",
                original_error=e
            )
    
    def logout(self) -> None:
        """
        Logout and clear authentication token.
        
        Example:
            >>> auth_service.logout()
        """
        logger.info("Logging out")
        
        try:
            # Attempt to notify backend of logout
            if self.authenticated:
                self.api_client.post("/auth/logout")
        except Exception as e:
            logger.warning(f"Logout request failed: {str(e)}")
        finally:
            # Clear local state regardless of backend response
            self.token = None
            self.authenticated = False
            self.api_client.clear_api_key()
            logger.info("Logged out successfully")
    
    def is_authenticated(self) -> bool:
        """
        Check if user is currently authenticated.
        
        Returns:
            True if authenticated, False otherwise
            
        Example:
            >>> if auth_service.is_authenticated():
            >>>     print("User is authenticated")
        """
        return self.authenticated and self.token is not None
    
    def get_token(self) -> Optional[str]:
        """
        Get current authentication token.
        
        Returns:
            Current token or None if not authenticated
            
        Example:
            >>> token = auth_service.get_token()
        """
        return self.token

# Made with Bob
