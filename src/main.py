"""
CABP Client Application - Main Entry Point

This is the main entry point for the Content-Aware Backup Platform Client Application.
It provides an interactive CLI interface for all CABP operations.
"""

import sys
import os
from typing import Optional

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CABPConfig
from api_client import APIClient
from logger import get_logger
from error_handler import CABPClientError, AuthenticationError

# Services
from services.auth_service import AuthService
from services.ingestion_service import IngestionService
from services.search_service import SearchService
from services.management_service import ManagementService
from services.topology_service import TopologyService
from services.health_service import HealthService
from services.components_service import ComponentsService
from services.mappings_service import MappingsService

# UI Components
from ui.menus import (
    display_main_menu, display_ingestion_menu, display_search_menu,
    display_management_menu, display_topology_menu, display_health_menu,
    display_mapping_menu, get_menu_choice, get_text_input, get_integer_input,
    get_confirmation, get_file_path, display_loading, display_separator
)
from ui.displays import (
    print_header, print_success, print_error, print_warning, print_info,
    display_file_list, display_file_details, display_search_results,
    display_topology_tree, display_health_dashboard, display_mappings_table,
    display_statistics, clear_screen, pause
)

logger = get_logger(__name__)


class CABPClientApp:
    """Main CABP Client Application"""
    
    def __init__(self):
        """Initialize the application"""
        self.config: Optional[CABPConfig] = None
        self.api_client: Optional[APIClient] = None
        self.auth_service: Optional[AuthService] = None
        self.ingestion_service: Optional[IngestionService] = None
        self.search_service: Optional[SearchService] = None
        self.management_service: Optional[ManagementService] = None
        self.topology_service: Optional[TopologyService] = None
        self.health_service: Optional[HealthService] = None
        self.components_service: Optional[ComponentsService] = None
        self.mappings_service: Optional[MappingsService] = None
        self.running = True
    
    def initialize(self) -> bool:
        """
        Initialize application components
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            print_header("CABP Client Initialization", "Initializing application components...")
            
            # Load configuration
            display_loading("Loading configuration...")
            self.config = CABPConfig()
            print_success("Configuration loaded")
            
            # Initialize API client
            display_loading("Initializing API client...")
            self.api_client = APIClient(
                base_url=self.config.base_url,
                api_key=self.config.api_key,
                timeout=self.config.timeout,
                max_retries=self.config.max_retries
            )
            print_success("API client initialized")
            
            # Initialize services
            display_loading("Initializing services...")
            self.auth_service = AuthService(self.api_client)
            self.ingestion_service = IngestionService(self.api_client)
            self.search_service = SearchService(self.api_client)
            self.management_service = ManagementService(self.api_client)
            self.topology_service = TopologyService(self.api_client)
            self.health_service = HealthService(self.api_client)
            self.components_service = ComponentsService(self.api_client)
            self.mappings_service = MappingsService(self.api_client)
            print_success("All services initialized")
            
            # Check backend health (optional - skip if endpoint has issues)
            display_loading("Checking backend health...")
            try:
                health = self.health_service.check_system_health()
                if health.get('status') == 'healthy':
                    print_success(f"Backend is healthy (v{health.get('version', 'unknown')})")
                else:
                    print_warning(f"Backend status: {health.get('status', 'unknown')}")
            except Exception as e:
                print_warning(f"Health check skipped (backend endpoint issue)")
                logger.warning(f"Health check failed but continuing: {e}")
            
            print_success("Initialization complete!")
            pause()
            
            return True
            
        except Exception as e:
            print_error(f"Initialization failed: {str(e)}")
            logger.error(f"Initialization error: {str(e)}", exc_info=True)
            return False
    
    def run(self) -> None:
        """Run the main application loop"""
        clear_screen()
        
        if not self.initialize():
            print_error("Failed to initialize application. Exiting.")
            return
        
        while self.running:
            try:
                clear_screen()
                display_main_menu()
                choice = get_menu_choice(8, "Select an option")
                
                if choice == 1:
                    self.ingestion_scenario()
                elif choice == 2:
                    self.search_scenario()
                elif choice == 3:
                    self.management_scenario()
                elif choice == 4:
                    self.topology_scenario()
                elif choice == 5:
                    self.health_scenario()
                elif choice == 6:
                    self.mapping_scenario()
                elif choice == 7:
                    self.system_info_scenario()
                elif choice == 8:
                    self.exit_application()
                
            except KeyboardInterrupt:
                print_warning("\nOperation cancelled by user")
                if get_confirmation("Exit application?", default=False):
                    self.exit_application()
                else:
                    pause()
            
            except Exception as e:
                print_error(f"Unexpected error: {str(e)}")
                logger.error(f"Application error: {str(e)}", exc_info=True)
                pause()
    
    def ingestion_scenario(self) -> None:
        """Handle ingestion operations"""
        while True:
            clear_screen()
            display_ingestion_menu()
            choice = get_menu_choice(5, "Select an option")
            
            if choice == 1:
                self.ingest_single_file()
            elif choice == 2:
                self.ingest_large_file()
            elif choice == 3:
                self.batch_ingest_files()
            elif choice == 4:
                self.view_ingestion_status()
            elif choice == 5:
                break
            
            pause()
    
    def ingest_single_file(self) -> None:
        """Ingest a single file"""
        try:
            print_header("Ingest Single File")
            
            file_path = get_file_path("Enter file path")
            if not file_path:
                return
            
            file_name = os.path.basename(file_path)
            
            # Get metadata
            print_info("Enter file metadata (press Enter to skip optional fields)")
            metadata = {
                'file_name': file_name,
                'product_name': get_text_input("Product name", default="Unknown"),
                'product_version': get_text_input("Product version", default=None),
                'os_version': get_text_input("OS version", default=None),
                'source': get_text_input("Source", default="manual_upload"),
                'description': get_text_input("Description", default=None)
            }
            
            # Remove None values
            metadata = {k: v for k, v in metadata.items() if v is not None}
            
            display_loading("Ingesting file...")
            result = self.ingestion_service.ingest_file(file_path, metadata)
            
            print_success(f"File ingested successfully!")
            print_info(f"File ID: {result.get('file_id')}")
            print_info(f"Bytes received: {result.get('bytes_received'):,}")
            print_info(f"Chunks created: {result.get('chunks_created')}")
            print_info(f"Embeddings created: {result.get('embeddings_created')}")
            
        except Exception as e:
            print_error(f"Ingestion failed: {str(e)}")
            logger.error(f"Ingestion error: {str(e)}", exc_info=True)
    
    def ingest_large_file(self) -> None:
        """Ingest a large file using chunked upload"""
        try:
            print_header("Ingest Large File (Chunked Upload)")
            
            file_path = get_file_path("Enter file path")
            if not file_path:
                return
            
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            print_info(f"File size: {file_size:,} bytes")
            
            # Get metadata
            metadata = {
                'file_name': file_name,
                'product_name': get_text_input("Product name", default="Unknown"),
                'source': get_text_input("Source", default="manual_upload")
            }
            
            def progress_callback(current, total, percent):
                print_info(f"Progress: {current}/{total} chunks ({percent:.1f}%)")
            
            display_loading("Starting chunked upload...")
            result = self.ingestion_service.ingest_large_file(
                file_path,
                metadata,
                progress_callback=progress_callback
            )
            
            print_success(f"Large file ingested successfully!")
            print_info(f"File ID: {result.get('file_id')}")
            
        except Exception as e:
            print_error(f"Large file ingestion failed: {str(e)}")
            logger.error(f"Large file ingestion error: {str(e)}", exc_info=True)
    
    def batch_ingest_files(self) -> None:
        """Batch ingest multiple files"""
        try:
            print_header("Batch Ingest Files")
            
            print_info("Enter file paths (one per line, empty line to finish):")
            file_paths = []
            
            while True:
                path = get_text_input(f"File {len(file_paths) + 1} path (or press Enter to finish)")
                if not path:
                    break
                
                path = os.path.expanduser(path)
                if os.path.exists(path) and os.path.isfile(path):
                    file_paths.append(path)
                else:
                    print_error(f"File not found: {path}")
            
            if not file_paths:
                print_warning("No files to ingest")
                return
            
            # Create metadata for each file
            metadata_list = []
            for path in file_paths:
                metadata_list.append({
                    'file_name': os.path.basename(path),
                    'source': 'batch_upload'
                })
            
            def progress_callback(current, total, percent):
                print_info(f"Progress: {current}/{total} files ({percent:.1f}%)")
            
            display_loading(f"Ingesting {len(file_paths)} files...")
            results = self.ingestion_service.batch_ingest(
                file_paths,
                metadata_list,
                progress_callback=progress_callback
            )
            
            successful = sum(1 for r in results if r['success'])
            print_success(f"Batch ingestion complete: {successful}/{len(results)} successful")
            
        except Exception as e:
            print_error(f"Batch ingestion failed: {str(e)}")
            logger.error(f"Batch ingestion error: {str(e)}", exc_info=True)
    
    def view_ingestion_status(self) -> None:
        """View ingestion status and statistics"""
        try:
            print_header("Ingestion Status")
            
            display_loading("Fetching statistics...")
            stats = self.management_service.get_file_statistics()
            
            display_statistics(stats, "Ingestion Statistics")
            
        except Exception as e:
            print_error(f"Failed to get ingestion status: {str(e)}")
            logger.error(f"Ingestion status error: {str(e)}", exc_info=True)
    
    def search_scenario(self) -> None:
        """Handle search operations"""
        while True:
            clear_screen()
            display_search_menu()
            choice = get_menu_choice(5, "Select an option")
            
            if choice == 1:
                self.semantic_search()
            elif choice == 2:
                self.ai_query()
            elif choice == 3:
                self.advanced_search()
            elif choice == 4:
                self.search_by_file_type()
            elif choice == 5:
                break
            
            pause()
    
    def semantic_search(self) -> None:
        """Perform semantic search"""
        try:
            print_header("Semantic Search")
            
            query = get_text_input("Enter search query")
            if not query:
                return
            
            max_results = get_integer_input("Maximum results", default=10, min_value=1, max_value=100)
            
            display_loading("Searching...")
            response = self.search_service.search(query, max_results=max_results)
            
            results = response.get('results', [])
            display_search_results(results, query)
            
            if response.get('ai_summary'):
                print_info(f"\nAI Summary: {response['ai_summary']}")
            
        except Exception as e:
            print_error(f"Search failed: {str(e)}")
            logger.error(f"Search error: {str(e)}", exc_info=True)
    
    def ai_query(self) -> None:
        """Perform AI-powered query"""
        try:
            print_header("AI-Powered Query")
            
            query = get_text_input("Enter your question")
            if not query:
                return
            
            display_loading("Querying AI...")
            response = self.search_service.query_with_ai(query)
            
            print_success("AI Response:")
            print_info(response.get('answer', 'No answer generated'))
            
            sources = response.get('sources', [])
            if sources:
                print_info(f"\nBased on {len(sources)} sources:")
                for idx, source in enumerate(sources, 1):
                    print_info(f"  {idx}. {source.get('file_name')} (similarity: {source.get('similarity_score', 0):.2%})")
            
        except Exception as e:
            print_error(f"AI query failed: {str(e)}")
            logger.error(f"AI query error: {str(e)}", exc_info=True)
    
    def advanced_search(self) -> None:
        """Perform advanced search with filters"""
        try:
            print_header("Advanced Search")
            
            query = get_text_input("Enter search query")
            if not query:
                return
            
            print_info("Enter filters (press Enter to skip):")
            
            product_name = get_text_input("Product name", default=None)
            backup_type = get_text_input("Backup type (full/differential/incremental)", default=None)
            
            response = self.search_service.advanced_search(
                query=query,
                product_name=product_name if product_name else None,
                backup_type=backup_type if backup_type else None
            )
            
            results = response.get('results', [])
            display_search_results(results, query)
            
        except Exception as e:
            print_error(f"Advanced search failed: {str(e)}")
            logger.error(f"Advanced search error: {str(e)}", exc_info=True)
    
    def search_by_file_type(self) -> None:
        """Search by file type"""
        try:
            print_header("Search by File Type")
            
            query = get_text_input("Enter search query")
            if not query:
                return
            
            file_type = get_text_input("File type (e.g., txt, pdf, log)")
            if not file_type:
                return
            
            display_loading("Searching...")
            results = self.search_service.search_by_file_type(query, file_type)
            
            display_search_results(results, f"{query} (type: {file_type})")
            
        except Exception as e:
            print_error(f"File type search failed: {str(e)}")
            logger.error(f"File type search error: {str(e)}", exc_info=True)
    
    def management_scenario(self) -> None:
        """Handle management operations"""
        while True:
            clear_screen()
            display_management_menu()
            choice = get_menu_choice(7, "Select an option")
            
            if choice == 1:
                self.list_files()
            elif choice == 2:
                self.view_file_details()
            elif choice == 3:
                self.delete_file()
            elif choice == 4:
                self.list_documents()
            elif choice == 5:
                self.view_document_details()
            elif choice == 6:
                self.file_statistics()
            elif choice == 7:
                break
            
            pause()
    
    def list_files(self) -> None:
        """List all files"""
        try:
            print_header("File List")
            
            limit = get_integer_input("Number of files to display", default=20, min_value=1, max_value=100)
            
            display_loading("Fetching files...")
            response = self.management_service.list_files(limit=limit)
            
            files = response.get('files', [])
            display_file_list(files)
            
            print_info(f"Showing {len(files)} of {response.get('total', 0)} total files")
            
        except Exception as e:
            print_error(f"Failed to list files: {str(e)}")
            logger.error(f"List files error: {str(e)}", exc_info=True)
    
    def view_file_details(self) -> None:
        """View file details"""
        try:
            print_header("File Details")
            
            file_id = get_integer_input("Enter file ID", min_value=1)
            if file_id is None:
                return
            
            display_loading("Fetching file details...")
            file = self.management_service.get_file(file_id)
            
            display_file_details(file)
            
        except Exception as e:
            print_error(f"Failed to get file details: {str(e)}")
            logger.error(f"File details error: {str(e)}", exc_info=True)
    
    def delete_file(self) -> None:
        """Delete a file"""
        try:
            print_header("Delete File")
            
            file_id = get_integer_input("Enter file ID to delete", min_value=1)
            if file_id is None:
                return
            
            if not get_confirmation(f"Are you sure you want to delete file {file_id}?", default=False):
                print_warning("Deletion cancelled")
                return
            
            display_loading("Deleting file...")
            self.management_service.delete_file(file_id)
            
            print_success(f"File {file_id} deleted successfully")
            
        except Exception as e:
            print_error(f"Failed to delete file: {str(e)}")
            logger.error(f"Delete file error: {str(e)}", exc_info=True)
    
    def list_documents(self) -> None:
        """List all documents"""
        try:
            print_header("Document List")
            
            limit = get_integer_input("Number of documents to display", default=20, min_value=1, max_value=100)
            
            display_loading("Fetching documents...")
            response = self.management_service.list_documents(limit=limit)
            
            documents = response.get('documents', [])
            
            if documents:
                print_success(f"Found {len(documents)} documents")
                for doc in documents:
                    print_info(f"ID: {doc.get('id')} - {doc.get('file_name')}")
            else:
                print_info("No documents found")
            
            print_info(f"Showing {len(documents)} of {response.get('total', 0)} total documents")
            
        except Exception as e:
            print_error(f"Failed to list documents: {str(e)}")
            logger.error(f"List documents error: {str(e)}", exc_info=True)
    
    def view_document_details(self) -> None:
        """View document details"""
        try:
            print_header("Document Details")
            
            doc_id = get_integer_input("Enter document ID", min_value=1)
            if doc_id is None:
                return
            
            display_loading("Fetching document details...")
            document = self.management_service.get_document(doc_id)
            
            print_success(f"Document: {document.get('file_name')}")
            print_info(f"File ID: {document.get('file_id')}")
            print_info(f"Created: {document.get('created_at')}")
            print_info(f"\nContent preview:")
            content = document.get('content', '')
            print_info(content[:500] + "..." if len(content) > 500 else content)
            
        except Exception as e:
            print_error(f"Failed to get document details: {str(e)}")
            logger.error(f"Document details error: {str(e)}", exc_info=True)
    
    def file_statistics(self) -> None:
        """Display file statistics"""
        try:
            print_header("File Statistics")
            
            display_loading("Calculating statistics...")
            stats = self.management_service.get_file_statistics()
            
            display_statistics(stats, "File Statistics")
            
        except Exception as e:
            print_error(f"Failed to get file statistics: {str(e)}")
            logger.error(f"File statistics error: {str(e)}", exc_info=True)
    
    def topology_scenario(self) -> None:
        """Handle topology operations"""
        while True:
            clear_screen()
            display_topology_menu()
            choice = get_menu_choice(5, "Select an option")
            
            if choice == 1:
                self.view_topology_tree()
            elif choice == 2:
                self.view_topology_statistics()
            elif choice == 3:
                self.search_component()
            elif choice == 4:
                self.view_components_by_type()
            elif choice == 5:
                break
            
            pause()
    
    def view_topology_tree(self) -> None:
        """View topology as a tree"""
        try:
            print_header("Topology Tree")
            
            display_loading("Fetching topology...")
            topology = self.topology_service.get_topology()
            
            components = topology.get('components', [])
            display_topology_tree(components)
            
        except Exception as e:
            print_error(f"Failed to get topology: {str(e)}")
            logger.error(f"Topology error: {str(e)}", exc_info=True)
    
    def view_topology_statistics(self) -> None:
        """View topology statistics"""
        try:
            print_header("Topology Statistics")
            
            display_loading("Fetching statistics...")
            summary = self.topology_service.get_topology_summary()
            
            display_statistics(summary, "Topology Statistics")
            
        except Exception as e:
            print_error(f"Failed to get topology statistics: {str(e)}")
            logger.error(f"Topology statistics error: {str(e)}", exc_info=True)
    
    def search_component(self) -> None:
        """Search for a component"""
        try:
            print_header("Search Component")
            
            component_id = get_text_input("Enter component ID")
            if not component_id:
                return
            
            display_loading("Searching...")
            component = self.topology_service.find_component_by_id(component_id)
            
            if component:
                print_success(f"Found component: {component.get('name')}")
                print_info(f"Type: {component.get('component_type')}")
                print_info(f"Health: {component.get('health_status', 'unknown')}")
                
                # Show path
                path = self.topology_service.get_component_path(component_id)
                if path:
                    print_info(f"Path: {' > '.join(path)}")
            else:
                print_warning(f"Component not found: {component_id}")
            
        except Exception as e:
            print_error(f"Component search failed: {str(e)}")
            logger.error(f"Component search error: {str(e)}", exc_info=True)
    
    def view_components_by_type(self) -> None:
        """View components by type"""
        try:
            print_header("Components by Type")
            
            comp_type = get_text_input("Enter component type (server/storage_pool/storage_volume/workload)")
            if not comp_type:
                return
            
            display_loading("Fetching components...")
            components = self.topology_service.get_components_by_type(comp_type)
            
            if components:
                print_success(f"Found {len(components)} components of type '{comp_type}'")
                for comp in components:
                    print_info(f"- {comp.get('name')} (ID: {comp.get('component_id')})")
            else:
                print_info(f"No components found of type '{comp_type}'")
            
        except Exception as e:
            print_error(f"Failed to get components by type: {str(e)}")
            logger.error(f"Components by type error: {str(e)}", exc_info=True)
    
    def health_scenario(self) -> None:
        """Handle health monitoring operations"""
        while True:
            clear_screen()
            display_health_menu()
            choice = get_menu_choice(5, "Select an option")
            
            if choice == 1:
                self.system_health_check()
            elif choice == 2:
                self.component_health_status()
            elif choice == 3:
                self.service_status()
            elif choice == 4:
                self.health_summary()
            elif choice == 5:
                break
            
            pause()
    
    def system_health_check(self) -> None:
        """Perform system health check"""
        try:
            print_header("System Health Check")
            
            display_loading("Checking system health...")
            health = self.health_service.check_system_health()
            
            display_health_dashboard(health)
            
        except Exception as e:
            print_error(f"Health check failed: {str(e)}")
            logger.error(f"Health check error: {str(e)}", exc_info=True)
    
    def component_health_status(self) -> None:
        """Check component health status"""
        try:
            print_header("Component Health Status")
            
            comp_id = get_integer_input("Enter component ID", min_value=1)
            if comp_id is None:
                return
            
            display_loading("Fetching component health...")
            health = self.health_service.get_component_health(comp_id)
            
            print_success(f"Component: {health.get('component_name')}")
            print_info(f"Status: {health.get('current_status')}")
            
            metrics = health.get('latest_metrics', {})
            if metrics:
                print_info("\nLatest Metrics:")
                for key, value in metrics.items():
                    print_info(f"  {key}: {value}")
            
        except Exception as e:
            print_error(f"Failed to get component health: {str(e)}")
            logger.error(f"Component health error: {str(e)}", exc_info=True)
    
    def service_status(self) -> None:
        """Check service status"""
        try:
            print_header("Service Status")
            
            display_loading("Checking services...")
            
            db_status = self.health_service.get_database_status()
            embedding_status = self.health_service.get_embedding_service_status()
            ollama_status = self.health_service.get_ollama_service_status()
            
            print_info(f"Database: {db_status}")
            print_info(f"Embedding Service: {embedding_status}")
            print_info(f"Ollama Service: {ollama_status}")
            
            if self.health_service.check_all_services_healthy():
                print_success("\nAll services are healthy!")
            else:
                print_warning("\nSome services are not healthy")
            
        except Exception as e:
            print_error(f"Failed to check service status: {str(e)}")
            logger.error(f"Service status error: {str(e)}", exc_info=True)
    
    def health_summary(self) -> None:
        """Display health summary"""
        try:
            print_header("Health Summary")
            
            display_loading("Fetching health summary...")
            summary = self.health_service.get_health_summary()
            
            display_statistics(summary, "Health Summary")
            
        except Exception as e:
            print_error(f"Failed to get health summary: {str(e)}")
            logger.error(f"Health summary error: {str(e)}", exc_info=True)
    
    def mapping_scenario(self) -> None:
        """Handle mapping operations"""
        while True:
            clear_screen()
            display_mapping_menu()
            choice = get_menu_choice(7, "Select an option")
            
            if choice == 1:
                self.list_mappings()
            elif choice == 2:
                self.create_mapping()
            elif choice == 3:
                self.view_file_mappings()
            elif choice == 4:
                self.view_component_mappings()
            elif choice == 5:
                self.delete_mapping()
            elif choice == 6:
                self.mapping_statistics()
            elif choice == 7:
                break
            
            pause()
    
    def list_mappings(self) -> None:
        """List all mappings"""
        try:
            print_header("Mapping List")
            
            limit = get_integer_input("Number of mappings to display", default=20, min_value=1, max_value=100)
            
            display_loading("Fetching mappings...")
            response = self.mappings_service.list_mappings(limit=limit)
            
            mappings = response.get('mappings', [])
            display_mappings_table(mappings)
            
            print_info(f"Showing {len(mappings)} of {response.get('total', 0)} total mappings")
            
        except Exception as e:
            print_error(f"Failed to list mappings: {str(e)}")
            logger.error(f"List mappings error: {str(e)}", exc_info=True)
    
    def create_mapping(self) -> None:
        """Create a new mapping"""
        try:
            print_header("Create Mapping")
            
            file_id = get_integer_input("Enter file ID", min_value=1)
            if file_id is None:
                return
            
            comp_id = get_integer_input("Enter component ID", min_value=1)
            if comp_id is None:
                return
            
            print_info("Relationship types:")
            print_info("  1. backed_up_by")
            print_info("  2. stored_in_pool")
            print_info("  3. stored_on_volume")
            print_info("  4. generated_by")
            print_info("  5. managed_by")
            
            rel_choice = get_integer_input("Select relationship type", min_value=1, max_value=5)
            if rel_choice is None:
                return
            
            rel_types = ['backed_up_by', 'stored_in_pool', 'stored_on_volume', 'generated_by', 'managed_by']
            rel_type = rel_types[rel_choice - 1]
            
            display_loading("Creating mapping...")
            mapping = self.mappings_service.create_mapping(file_id, comp_id, rel_type)
            
            print_success(f"Mapping created successfully!")
            print_info(f"Mapping ID: {mapping.get('id')}")
            
        except Exception as e:
            print_error(f"Failed to create mapping: {str(e)}")
            logger.error(f"Create mapping error: {str(e)}", exc_info=True)
    
    def view_file_mappings(self) -> None:
        """View mappings for a file"""
        try:
            print_header("File Mappings")
            
            file_id = get_integer_input("Enter file ID", min_value=1)
            if file_id is None:
                return
            
            display_loading("Fetching mappings...")
            mappings = self.mappings_service.get_file_mappings(file_id)
            
            display_mappings_table(mappings)
            
        except Exception as e:
            print_error(f"Failed to get file mappings: {str(e)}")
            logger.error(f"File mappings error: {str(e)}", exc_info=True)
    
    def view_component_mappings(self) -> None:
        """View mappings for a component"""
        try:
            print_header("Component Mappings")
            
            comp_id = get_integer_input("Enter component ID", min_value=1)
            if comp_id is None:
                return
            
            display_loading("Fetching mappings...")
            mappings = self.mappings_service.get_component_mappings(comp_id)
            
            display_mappings_table(mappings)
            
        except Exception as e:
            print_error(f"Failed to get component mappings: {str(e)}")
            logger.error(f"Component mappings error: {str(e)}", exc_info=True)
    
    def delete_mapping(self) -> None:
        """Delete a mapping"""
        try:
            print_header("Delete Mapping")
            
            mapping_id = get_integer_input("Enter mapping ID to delete", min_value=1)
            if mapping_id is None:
                return
            
            if not get_confirmation(f"Are you sure you want to delete mapping {mapping_id}?", default=False):
                print_warning("Deletion cancelled")
                return
            
            display_loading("Deleting mapping...")
            self.mappings_service.delete_mapping(mapping_id)
            
            print_success(f"Mapping {mapping_id} deleted successfully")
            
        except Exception as e:
            print_error(f"Failed to delete mapping: {str(e)}")
            logger.error(f"Delete mapping error: {str(e)}", exc_info=True)
    
    def mapping_statistics(self) -> None:
        """Display mapping statistics"""
        try:
            print_header("Mapping Statistics")
            
            display_loading("Calculating statistics...")
            stats = self.mappings_service.get_mapping_statistics()
            
            display_statistics(stats, "Mapping Statistics")
            
        except Exception as e:
            print_error(f"Failed to get mapping statistics: {str(e)}")
            logger.error(f"Mapping statistics error: {str(e)}", exc_info=True)
    
    def system_info_scenario(self) -> None:
        """Display system information"""
        try:
            clear_screen()
            print_header("System Information")
            
            display_loading("Fetching system information...")
            
            # Get health info
            health = self.health_service.check_system_health()
            
            # Get file stats
            file_stats = self.management_service.get_file_statistics()
            
            # Get topology summary
            topo_summary = self.topology_service.get_topology_summary()
            
            # Display information
            print_info(f"Backend Version: {health.get('version', 'unknown')}")
            print_info(f"Backend Status: {health.get('status', 'unknown')}")
            print_info(f"Total Files: {file_stats.get('total_files', 0)}")
            print_info(f"Total Size: {file_stats.get('total_size_mb', 0)} MB")
            print_info(f"Total Components: {topo_summary.get('total_components', 0)}")
            
            print_info(f"\nClient Configuration:")
            print_info(f"Base URL: {self.config.base_url}")
            print_info(f"Environment: {self.config.environment}")
            print_info(f"Log Level: {self.config.log_level}")
            
            pause()
            
        except Exception as e:
            print_error(f"Failed to get system information: {str(e)}")
            logger.error(f"System info error: {str(e)}", exc_info=True)
            pause()
    
    def exit_application(self) -> None:
        """Exit the application"""
        print_header("Exit", "Thank you for using CABP Client!")
        self.running = False


def main():
    """Main entry point"""
    try:
        app = CABPClientApp()
        app.run()
    except KeyboardInterrupt:
        print_warning("\nApplication terminated by user")
    except Exception as e:
        print_error(f"Fatal error: {str(e)}")
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
