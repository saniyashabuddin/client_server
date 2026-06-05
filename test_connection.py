#!/usr/bin/env python3
"""
Simple test script to verify CABP Client connection to CABS backend.
Run this to test if everything is working correctly.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import config
from api_client import APIClient
from services.auth_service import AuthService
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def print_header(title):
    """Print a formatted header"""
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    console.print("=" * 60)


def test_backend_health():
    """Test if CABS backend is running"""
    print_header("1. Testing CABS Backend Health")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            console.print(f"[green]✓[/green] Backend is healthy")
            console.print(f"  Status: {data.get('status')}")
            console.print(f"  Version: {data.get('version')}")
            console.print(f"  Timestamp: {data.get('timestamp')}")
            return True
        else:
            console.print(f"[red]✗[/red] Backend returned status {response.status_code}")
            return False
    except Exception as e:
        console.print(f"[red]✗[/red] Cannot connect to backend: {e}")
        console.print("\n[yellow]Make sure CABS backend is running:[/yellow]")
        console.print("  cd /Users/saniya/Desktop/cabs")
        console.print("  python -m api.main")
        return False


def test_configuration():
    """Test client configuration"""
    print_header("2. Testing Client Configuration")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Base URL", config.base_url)
    table.add_row("API Key", f"{config.api_key[:20]}..." if config.api_key else "Not set")
    table.add_row("Timeout", f"{config.timeout}s")
    table.add_row("Max Retries", str(config.max_retries))
    table.add_row("Log Level", config.log_level)
    table.add_row("Environment", config.environment)
    
    console.print(table)
    
    if not config.api_key:
        console.print("\n[red]✗[/red] API key not configured!")
        return False
    
    console.print("\n[green]✓[/green] Configuration is valid")
    return True


def test_api_client():
    """Test API client initialization"""
    print_header("3. Testing API Client")
    
    try:
        client = APIClient()
        console.print(f"[green]✓[/green] API Client initialized")
        console.print(f"  Base URL: {client.base_url}")
        console.print(f"  Timeout: {client.timeout}s")
        console.print(f"  Max Retries: {client.max_retries}")
        return client
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to initialize API client: {e}")
        return None


def test_authentication(client):
    """Test authentication service"""
    print_header("4. Testing Authentication")
    
    try:
        auth_service = AuthService(client)
        console.print(f"[green]✓[/green] Authentication service initialized")
        
        # Check if already authenticated
        if auth_service.is_authenticated():
            console.print(f"[green]✓[/green] Already authenticated")
        else:
            console.print(f"[yellow]![/yellow] Not authenticated (API key will be used for requests)")
        
        return True
    except Exception as e:
        console.print(f"[red]✗[/red] Authentication test failed: {e}")
        return False


def test_api_endpoints(client):
    """Test various API endpoints"""
    print_header("5. Testing API Endpoints")
    
    endpoints = [
        ("Root", "/", "GET"),
        ("Health (root)", "http://localhost:8000/health", "GET"),
    ]
    
    results = []
    for name, endpoint, method in endpoints:
        try:
            if endpoint.startswith("http"):
                response = requests.get(endpoint, timeout=5)
                status = response.status_code
            else:
                if method == "GET":
                    response = client.get(endpoint)
                    status = 200
            
            results.append((name, endpoint, status, "✓"))
            console.print(f"[green]✓[/green] {name}: {status}")
        except Exception as e:
            results.append((name, endpoint, "Error", "✗"))
            console.print(f"[yellow]![/yellow] {name}: {str(e)[:50]}")
    
    return results


def print_summary(backend_ok, config_ok, client_ok, auth_ok):
    """Print test summary"""
    print_header("Test Summary")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="green")
    
    table.add_row("Backend Health", "✓ Pass" if backend_ok else "✗ Fail")
    table.add_row("Configuration", "✓ Pass" if config_ok else "✗ Fail")
    table.add_row("API Client", "✓ Pass" if client_ok else "✗ Fail")
    table.add_row("Authentication", "✓ Pass" if auth_ok else "✗ Fail")
    
    console.print(table)
    
    if all([backend_ok, config_ok, client_ok, auth_ok]):
        console.print(Panel(
            "[bold green]All tests passed! ✓[/bold green]\n\n"
            "The CABP Client is successfully connected to the CABS backend.\n"
            "You can now use the client to interact with the backend.",
            title="Success",
            border_style="green"
        ))
        return True
    else:
        console.print(Panel(
            "[bold red]Some tests failed! ✗[/bold red]\n\n"
            "Please check the errors above and fix the issues.",
            title="Failed",
            border_style="red"
        ))
        return False


def main():
    """Main test function"""
    console.print(Panel(
        "[bold]CABP Client - Connection Test[/bold]\n\n"
        "This script tests the connection between the CABP Client\n"
        "and the CABS backend.",
        title="Test Suite",
        border_style="blue"
    ))
    
    # Run tests
    backend_ok = test_backend_health()
    config_ok = test_configuration()
    client = test_api_client()
    client_ok = client is not None
    
    auth_ok = False
    if client_ok:
        auth_ok = test_authentication(client)
        test_api_endpoints(client)
    
    # Print summary
    success = print_summary(backend_ok, config_ok, client_ok, auth_ok)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

# Made with Bob
