"""
Display Components Module

Provides rich terminal display components for:
- Formatted output
- Tables
- Panels
- Trees
- Progress indicators
"""

from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.syntax import Syntax
from rich.markdown import Markdown
from datetime import datetime

console = Console()


def print_header(title: str, subtitle: Optional[str] = None) -> None:
    """
    Print a formatted header
    
    Args:
        title: Main title
        subtitle: Optional subtitle
    """
    console.print()
    if subtitle:
        console.print(Panel(f"[bold cyan]{title}[/bold cyan]\n{subtitle}", 
                          border_style="cyan"))
    else:
        console.print(Panel(f"[bold cyan]{title}[/bold cyan]", 
                          border_style="cyan"))
    console.print()


def print_success(message: str) -> None:
    """Print a success message"""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    """Print an error message"""
    console.print(f"[bold red]✗[/bold red] {message}")


def print_warning(message: str) -> None:
    """Print a warning message"""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def print_info(message: str) -> None:
    """Print an info message"""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def print_section(title: str) -> None:
    """Print a section divider"""
    console.print()
    console.print(f"[bold underline]{title}[/bold underline]")
    console.print()


def display_file_list(files: List[Dict[str, Any]]) -> None:
    """
    Display a list of files in a table
    
    Args:
        files: List of file dictionaries
    """
    if not files:
        print_info("No files found")
        return
    
    table = Table(title="Files", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=8)
    table.add_column("File Name", style="green")
    table.add_column("Type", style="yellow", width=10)
    table.add_column("Size", style="blue", width=12)
    table.add_column("Created", style="magenta", width=20)
    
    for file in files:
        file_id = str(file.get('id', 'N/A'))
        file_name = file.get('file_name', 'Unknown')
        file_type = file.get('file_type', 'N/A')
        file_size = format_file_size(file.get('file_size', 0))
        created_at = format_datetime(file.get('created_at'))
        
        table.add_row(file_id, file_name, file_type, file_size, created_at)
    
    console.print(table)


def display_file_details(file: Dict[str, Any]) -> None:
    """
    Display detailed file information
    
    Args:
        file: File dictionary
    """
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Property", style="bold cyan")
    table.add_column("Value", style="white")
    
    table.add_row("ID", str(file.get('id', 'N/A')))
    table.add_row("File Name", file.get('file_name', 'Unknown'))
    table.add_row("File Type", file.get('file_type', 'N/A'))
    table.add_row("File Size", format_file_size(file.get('file_size', 0)))
    table.add_row("File Hash", file.get('file_hash', 'N/A'))
    table.add_row("Version", file.get('version', 'N/A'))
    table.add_row("Chunk Count", str(file.get('chunk_count', 0)))
    table.add_row("Created At", format_datetime(file.get('created_at')))
    table.add_row("Updated At", format_datetime(file.get('updated_at')))
    
    console.print(Panel(table, title="[bold]File Details[/bold]", border_style="green"))


def display_search_results(results: List[Dict[str, Any]], query: str) -> None:
    """
    Display search results
    
    Args:
        results: List of search result dictionaries
        query: Original search query
    """
    if not results:
        print_info(f"No results found for: '{query}'")
        return
    
    print_header(f"Search Results for: '{query}'", f"Found {len(results)} results")
    
    for idx, result in enumerate(results, 1):
        similarity = result.get('similarity_score', 0)
        file_name = result.get('file_name', 'Unknown')
        content = result.get('content', '')[:200] + "..." if len(result.get('content', '')) > 200 else result.get('content', '')
        
        # Color code by similarity
        if similarity >= 0.8:
            color = "green"
        elif similarity >= 0.5:
            color = "yellow"
        else:
            color = "red"
        
        console.print(f"\n[bold]{idx}. {file_name}[/bold] [dim](Similarity: [{color}]{similarity:.2%}[/{color}])[/dim]")
        console.print(f"[dim]{content}[/dim]")


def display_topology_tree(components: List[Dict[str, Any]]) -> None:
    """
    Display topology as a tree structure
    
    Args:
        components: List of component dictionaries with nested children
    """
    if not components:
        print_info("No topology data available")
        return
    
    tree = Tree("[bold cyan]IBM Storage Protect Topology[/bold cyan]")
    
    def add_component_to_tree(parent_tree: Tree, component: Dict[str, Any]) -> None:
        """Recursively add components to tree"""
        name = component.get('name', 'Unknown')
        comp_type = component.get('component_type', 'unknown')
        health = component.get('health_status', 'unknown')
        
        # Color code by health status
        if health == 'healthy':
            health_color = "green"
        elif health == 'degraded':
            health_color = "yellow"
        elif health == 'unhealthy':
            health_color = "red"
        else:
            health_color = "white"
        
        label = f"[bold]{name}[/bold] [dim]({comp_type})[/dim] [{health_color}]{health}[/{health_color}]"
        branch = parent_tree.add(label)
        
        # Add children recursively
        children = component.get('children', [])
        for child in children:
            add_component_to_tree(branch, child)
    
    for component in components:
        add_component_to_tree(tree, component)
    
    console.print(tree)


def display_health_dashboard(health: Dict[str, Any]) -> None:
    """
    Display system health dashboard
    
    Args:
        health: Health check response dictionary
    """
    status = health.get('status', 'unknown')
    
    # Color code overall status
    if status == 'healthy':
        status_color = "green"
        status_icon = "✓"
    elif status == 'degraded':
        status_color = "yellow"
        status_icon = "⚠"
    else:
        status_color = "red"
        status_icon = "✗"
    
    # Create main status panel
    console.print(Panel(
        f"[bold {status_color}]{status_icon} System Status: {status.upper()}[/bold {status_color}]",
        border_style=status_color
    ))
    
    # Create services table
    table = Table(title="Service Status", show_header=True, header_style="bold magenta")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="white")
    
    services = {
        'Database': health.get('database', 'unknown'),
        'Embedding Service': health.get('embedding_service', 'unknown'),
        'Ollama Service': health.get('ollama_service', 'unknown')
    }
    
    for service_name, service_status in services.items():
        # Color code service status
        if service_status.lower() in ['healthy', 'connected', 'available']:
            status_display = f"[green]✓ {service_status}[/green]"
        else:
            status_display = f"[red]✗ {service_status}[/red]"
        
        table.add_row(service_name, status_display)
    
    console.print(table)
    
    # Display components if available
    components = health.get('components', {})
    if components:
        console.print("\n[bold]Component Status:[/bold]")
        for comp_name, comp_status in components.items():
            if comp_status.lower() in ['healthy', 'connected', 'available']:
                console.print(f"  [green]✓[/green] {comp_name}: {comp_status}")
            else:
                console.print(f"  [red]✗[/red] {comp_name}: {comp_status}")
    
    # Display version and timestamp
    console.print(f"\n[dim]Version: {health.get('version', 'unknown')}[/dim]")
    console.print(f"[dim]Timestamp: {format_datetime(health.get('timestamp'))}[/dim]")


def display_mappings_table(mappings: List[Dict[str, Any]]) -> None:
    """
    Display mappings in a table
    
    Args:
        mappings: List of mapping dictionaries
    """
    if not mappings:
        print_info("No mappings found")
        return
    
    table = Table(title="File-Component Mappings", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=8)
    table.add_column("File", style="green")
    table.add_column("Component", style="yellow")
    table.add_column("Relationship", style="blue")
    table.add_column("Created", style="magenta", width=20)
    
    for mapping in mappings:
        mapping_id = str(mapping.get('id', 'N/A'))
        file_name = mapping.get('file_name', 'Unknown')
        component_name = mapping.get('component_name', 'Unknown')
        relationship = mapping.get('relationship_type', 'N/A')
        created_at = format_datetime(mapping.get('created_at'))
        
        table.add_row(mapping_id, file_name, component_name, relationship, created_at)
    
    console.print(table)


def display_statistics(stats: Dict[str, Any], title: str = "Statistics") -> None:
    """
    Display statistics in a formatted panel
    
    Args:
        stats: Statistics dictionary
        title: Panel title
    """
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Metric", style="bold cyan")
    table.add_column("Value", style="white")
    
    for key, value in stats.items():
        # Format key (convert snake_case to Title Case)
        formatted_key = key.replace('_', ' ').title()
        
        # Format value
        if isinstance(value, dict):
            formatted_value = "\n".join(f"  {k}: {v}" for k, v in value.items())
        elif isinstance(value, (int, float)):
            formatted_value = f"{value:,}"
        else:
            formatted_value = str(value)
        
        table.add_row(formatted_key, formatted_value)
    
    console.print(Panel(table, title=f"[bold]{title}[/bold]", border_style="cyan"))


def display_progress_bar(total: int, description: str = "Processing") -> Progress:
    """
    Create and return a progress bar
    
    Args:
        total: Total number of items
        description: Progress description
        
    Returns:
        Progress object
    """
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    )
    
    return progress


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def format_datetime(dt_string: Optional[str]) -> str:
    """
    Format datetime string for display
    
    Args:
        dt_string: ISO format datetime string
        
    Returns:
        Formatted datetime string
    """
    if not dt_string:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return dt_string


def clear_screen() -> None:
    """Clear the terminal screen"""
    console.clear()


def print_json(data: Dict[str, Any], title: Optional[str] = None) -> None:
    """
    Print JSON data with syntax highlighting
    
    Args:
        data: Dictionary to display as JSON
        title: Optional title
    """
    import json
    
    json_str = json.dumps(data, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    
    if title:
        console.print(Panel(syntax, title=f"[bold]{title}[/bold]", border_style="cyan"))
    else:
        console.print(syntax)


def print_markdown(text: str) -> None:
    """
    Print markdown formatted text
    
    Args:
        text: Markdown text
    """
    md = Markdown(text)
    console.print(md)


def pause(message: str = "Press Enter to continue...") -> None:
    """
    Pause and wait for user input
    
    Args:
        message: Message to display
    """
    console.print(f"\n[dim]{message}[/dim]")
    input()

# Made with Bob
