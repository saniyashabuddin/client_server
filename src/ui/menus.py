"""
Menu Components Module

Provides interactive menu components for:
- Main menu
- Sub-menus
- Option selection
- User input
"""

from typing import List, Optional, Callable, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

console = Console()


def display_main_menu() -> None:
    """Display the main application menu"""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Content-Aware Backup Platform Client[/bold cyan]\n"
        "[dim]Interactive CLI for CABP Operations[/dim]",
        border_style="cyan"
    ))
    console.print()
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("Description", style="white")
    
    table.add_row("1", "Authentication & Ingestion")
    table.add_row("2", "Search Operations")
    table.add_row("3", "Management Operations")
    table.add_row("4", "Topology Explorer")
    table.add_row("5", "Health Dashboard")
    table.add_row("6", "Mapping Explorer")
    table.add_row("7", "System Information")
    table.add_row("8", "Exit")
    
    console.print(table)
    console.print()


def display_ingestion_menu() -> None:
    """Display the ingestion operations menu"""
    console.print()
    console.print("[bold cyan]Ingestion Operations[/bold cyan]")
    console.print()
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("Description", style="white")
    
    table.add_row("1", "Ingest Single File")
    table.add_row("2", "Ingest Large File (Chunked)")
    table.add_row("3", "Batch Ingest Files")
    table.add_row("4", "View Ingestion Status")
    table.add_row("5", "Back to Main Menu")
    
    console.print(table)
    console.print()


def display_search_menu() -> None:
    """Display the search operations menu"""
    console.print()
    console.print("[bold cyan]Search Operations[/bold cyan]")
    console.print()
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("Description", style="white")
    
    table.add_row("1", "Semantic Search")
    table.add_row("2", "AI-Powered Query")
    table.add_row("3", "Advanced Search with Filters")
    table.add_row("4", "Search by File Type")
    table.add_row("5", "Back to Main Menu")
    
    console.print(table)
    console.print()


def display_management_menu() -> None:
    """Display the management operations menu"""
    console.print()
    console.print("[bold cyan]Management Operations[/bold cyan]")
    console.print()
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("Description", style="white")
    
    table.add_row("1", "List All Files")
    table.add_row("2", "View File Details")
    table.add_row("3", "Delete File")
    table.add_row("4", "List All Documents")
    table.add_row("5", "View Document Details")
    table.add_row("6", "File Statistics")
    table.add_row("7", "Back to Main Menu")
    
    console.print(table)
    console.print()


def display_topology_menu() -> None:
    """Display the topology operations menu"""
    console.print()
    console.print("[bold cyan]Topology Explorer[/bold cyan]")
    console.print()
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("Description", style="white")
    
    table.add_row("1", "View Topology Tree")
    table.add_row("2", "View Topology Statistics")
    table.add_row("3", "Search Component")
    table.add_row("4", "View Components by Type")
    table.add_row("5", "Back to Main Menu")
    
    console.print(table)
    console.print()


def display_health_menu() -> None:
    """Display the health monitoring menu"""
    console.print()
    console.print("[bold cyan]Health Dashboard[/bold cyan]")
    console.print()
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("Description", style="white")
    
    table.add_row("1", "System Health Check")
    table.add_row("2", "Component Health Status")
    table.add_row("3", "Service Status")
    table.add_row("4", "Health Summary")
    table.add_row("5", "Back to Main Menu")
    
    console.print(table)
    console.print()


def display_mapping_menu() -> None:
    """Display the mapping operations menu"""
    console.print()
    console.print("[bold cyan]Mapping Explorer[/bold cyan]")
    console.print()
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Option", style="bold cyan", width=4)
    table.add_column("Description", style="white")
    
    table.add_row("1", "List All Mappings")
    table.add_row("2", "Create New Mapping")
    table.add_row("3", "View File Mappings")
    table.add_row("4", "View Component Mappings")
    table.add_row("5", "Delete Mapping")
    table.add_row("6", "Mapping Statistics")
    table.add_row("7", "Back to Main Menu")
    
    console.print(table)
    console.print()


def get_menu_choice(max_option: int, prompt_text: str = "Select an option") -> int:
    """
    Get user's menu choice
    
    Args:
        max_option: Maximum valid option number
        prompt_text: Prompt text to display
        
    Returns:
        Selected option number
    """
    while True:
        try:
            choice = Prompt.ask(
                f"[bold cyan]{prompt_text}[/bold cyan]",
                default="1"
            )
            
            choice_int = int(choice)
            
            if 1 <= choice_int <= max_option:
                return choice_int
            else:
                console.print(f"[bold red]Please enter a number between 1 and {max_option}[/bold red]")
        
        except ValueError:
            console.print("[bold red]Please enter a valid number[/bold red]")
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Operation cancelled[/bold yellow]")
            return max_option  # Return exit option


def get_text_input(
    prompt_text: str,
    default: Optional[str] = None,
    password: bool = False
) -> str:
    """
    Get text input from user
    
    Args:
        prompt_text: Prompt text to display
        default: Default value
        password: Whether to hide input
        
    Returns:
        User input string
    """
    try:
        return Prompt.ask(
            f"[bold cyan]{prompt_text}[/bold cyan]",
            default=default,
            password=password
        )
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Input cancelled[/bold yellow]")
        return default or ""


def get_integer_input(
    prompt_text: str,
    default: Optional[int] = None,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None
) -> Optional[int]:
    """
    Get integer input from user
    
    Args:
        prompt_text: Prompt text to display
        default: Default value
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        User input integer or None if cancelled
    """
    while True:
        try:
            value_str = Prompt.ask(
                f"[bold cyan]{prompt_text}[/bold cyan]",
                default=str(default) if default is not None else None
            )
            
            if not value_str and default is not None:
                return default
            
            value = int(value_str)
            
            if min_value is not None and value < min_value:
                console.print(f"[bold red]Value must be at least {min_value}[/bold red]")
                continue
            
            if max_value is not None and value > max_value:
                console.print(f"[bold red]Value must be at most {max_value}[/bold red]")
                continue
            
            return value
        
        except ValueError:
            console.print("[bold red]Please enter a valid integer[/bold red]")
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Input cancelled[/bold yellow]")
            return None


def get_float_input(
    prompt_text: str,
    default: Optional[float] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> Optional[float]:
    """
    Get float input from user
    
    Args:
        prompt_text: Prompt text to display
        default: Default value
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        User input float or None if cancelled
    """
    while True:
        try:
            value_str = Prompt.ask(
                f"[bold cyan]{prompt_text}[/bold cyan]",
                default=str(default) if default is not None else None
            )
            
            if not value_str and default is not None:
                return default
            
            value = float(value_str)
            
            if min_value is not None and value < min_value:
                console.print(f"[bold red]Value must be at least {min_value}[/bold red]")
                continue
            
            if max_value is not None and value > max_value:
                console.print(f"[bold red]Value must be at most {max_value}[/bold red]")
                continue
            
            return value
        
        except ValueError:
            console.print("[bold red]Please enter a valid number[/bold red]")
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Input cancelled[/bold yellow]")
            return None


def get_confirmation(prompt_text: str, default: bool = False) -> bool:
    """
    Get yes/no confirmation from user
    
    Args:
        prompt_text: Prompt text to display
        default: Default value
        
    Returns:
        True if confirmed, False otherwise
    """
    try:
        return Confirm.ask(
            f"[bold cyan]{prompt_text}[/bold cyan]",
            default=default
        )
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Cancelled[/bold yellow]")
        return False


def get_file_path(prompt_text: str = "Enter file path") -> Optional[str]:
    """
    Get file path from user with validation
    
    Args:
        prompt_text: Prompt text to display
        
    Returns:
        File path or None if cancelled
    """
    import os
    
    while True:
        try:
            path = Prompt.ask(f"[bold cyan]{prompt_text}[/bold cyan]")
            
            if not path:
                console.print("[bold red]File path cannot be empty[/bold red]")
                continue
            
            # Expand user home directory
            path = os.path.expanduser(path)
            
            if not os.path.exists(path):
                console.print(f"[bold red]File not found: {path}[/bold red]")
                retry = get_confirmation("Try again?", default=True)
                if not retry:
                    return None
                continue
            
            if not os.path.isfile(path):
                console.print(f"[bold red]Not a file: {path}[/bold red]")
                continue
            
            return path
        
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Cancelled[/bold yellow]")
            return None


def select_from_list(
    items: List[Any],
    prompt_text: str = "Select an item",
    display_func: Optional[Callable[[Any], str]] = None
) -> Optional[Any]:
    """
    Let user select an item from a list
    
    Args:
        items: List of items to choose from
        prompt_text: Prompt text to display
        display_func: Optional function to format item display
        
    Returns:
        Selected item or None if cancelled
    """
    if not items:
        console.print("[bold yellow]No items available[/bold yellow]")
        return None
    
    console.print(f"\n[bold]{prompt_text}:[/bold]")
    
    for idx, item in enumerate(items, 1):
        if display_func:
            display = display_func(item)
        else:
            display = str(item)
        
        console.print(f"  {idx}. {display}")
    
    console.print(f"  0. Cancel")
    console.print()
    
    choice = get_integer_input(
        "Enter selection",
        min_value=0,
        max_value=len(items)
    )
    
    if choice is None or choice == 0:
        return None
    
    return items[choice - 1]


def display_loading(message: str = "Loading...") -> None:
    """
    Display a loading message
    
    Args:
        message: Loading message to display
    """
    console.print(f"[bold cyan]⏳ {message}[/bold cyan]")


def display_separator() -> None:
    """Display a visual separator"""
    console.print("\n" + "─" * console.width + "\n")

# Made with Bob
