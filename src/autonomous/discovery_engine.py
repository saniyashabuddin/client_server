"""
Discovery Engine for Autonomous CABP Platform

Automatically discovers all entities in the system:
- Servers
- Storage Pools
- Volumes
- Backup Objects
- Files
- Documents
- Metadata
- Components
- Relationships
- Mappings
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from logger import get_logger
from api_client import APIClient
from services.management_service import ManagementService
from services.topology_service import TopologyService
from services.components_service import ComponentsService
from services.mappings_service import MappingsService

logger = get_logger(__name__)


class DiscoveryEngine:
    """Automatically discovers all entities in the CABP system"""
    
    def __init__(
        self,
        api_client: APIClient,
        management_service: ManagementService,
        topology_service: TopologyService,
        components_service: ComponentsService,
        mappings_service: MappingsService
    ):
        """
        Initialize Discovery Engine
        
        Args:
            api_client: API client instance
            management_service: Management service instance
            topology_service: Topology service instance
            components_service: Components service instance
            mappings_service: Mappings service instance
        """
        self.api_client = api_client
        self.management_service = management_service
        self.topology_service = topology_service
        self.components_service = components_service
        self.mappings_service = mappings_service
        
        self.discovered_entities: Dict[str, List[Any]] = {
            "files": [],
            "documents": [],
            "components": [],
            "mappings": [],
            "topology_nodes": [],
            "metadata_records": []
        }
        
        self.discovery_stats: Dict[str, int] = {}
        self.discovery_errors: List[str] = []
        
        logger.info("Discovery Engine initialized")
    
    async def discover_all(self) -> Dict[str, Any]:
        """
        Discover all entities in the system
        
        Returns:
            Dictionary with discovery results
        """
        logger.info("Starting comprehensive discovery...")
        start_time = datetime.now()
        
        # Discover files
        await self._discover_files()
        
        # Discover documents
        await self._discover_documents()
        
        # Discover components
        await self._discover_components()
        
        # Discover mappings
        await self._discover_mappings()
        
        # Discover topology
        await self._discover_topology()
        
        # Calculate statistics
        self._calculate_stats()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Discovery completed in {duration:.2f}s")
        
        return {
            "entities": self.discovered_entities,
            "stats": self.discovery_stats,
            "errors": self.discovery_errors,
            "duration": duration
        }
    
    async def _discover_files(self) -> None:
        """Discover all files"""
        try:
            logger.info("Discovering files...")
            
            # Get all files (paginated)
            skip = 0
            limit = 100
            total_files = 0
            
            while True:
                try:
                    response = self.management_service.list_files(skip=skip, limit=limit)
                    files = response.get('files', [])
                    
                    if not files:
                        break
                    
                    self.discovered_entities["files"].extend(files)
                    total_files += len(files)
                    skip += limit
                    
                    logger.debug(f"Discovered {total_files} files so far...")
                    
                except Exception as e:
                    logger.warning(f"Error discovering files at skip={skip}: {e}")
                    self.discovery_errors.append(f"Files discovery error: {str(e)}")
                    break
            
            logger.info(f"Discovered {total_files} files")
            
        except Exception as e:
            logger.error(f"Failed to discover files: {e}")
            self.discovery_errors.append(f"Files discovery failed: {str(e)}")
    
    async def _discover_documents(self) -> None:
        """Discover all documents"""
        try:
            logger.info("Discovering documents...")
            
            skip = 0
            limit = 100
            total_docs = 0
            
            while True:
                try:
                    response = self.management_service.list_documents(skip=skip, limit=limit)
                    documents = response.get('documents', [])
                    
                    if not documents:
                        break
                    
                    self.discovered_entities["documents"].extend(documents)
                    total_docs += len(documents)
                    skip += limit
                    
                    logger.debug(f"Discovered {total_docs} documents so far...")
                    
                except Exception as e:
                    logger.warning(f"Error discovering documents at skip={skip}: {e}")
                    self.discovery_errors.append(f"Documents discovery error: {str(e)}")
                    break
            
            logger.info(f"Discovered {total_docs} documents")
            
        except Exception as e:
            logger.error(f"Failed to discover documents: {e}")
            self.discovery_errors.append(f"Documents discovery failed: {str(e)}")
    
    async def _discover_components(self) -> None:
        """Discover all components"""
        try:
            logger.info("Discovering components...")
            
            skip = 0
            limit = 100
            total_components = 0
            
            while True:
                try:
                    response = self.components_service.list_components(skip=skip, limit=limit)
                    components = response.get('components', [])
                    
                    if not components:
                        break
                    
                    self.discovered_entities["components"].extend(components)
                    total_components += len(components)
                    skip += limit
                    
                    logger.debug(f"Discovered {total_components} components so far...")
                    
                except Exception as e:
                    logger.warning(f"Error discovering components at skip={skip}: {e}")
                    self.discovery_errors.append(f"Components discovery error: {str(e)}")
                    break
            
            logger.info(f"Discovered {total_components} components")
            
        except Exception as e:
            logger.error(f"Failed to discover components: {e}")
            self.discovery_errors.append(f"Components discovery failed: {str(e)}")
    
    async def _discover_mappings(self) -> None:
        """Discover all mappings"""
        try:
            logger.info("Discovering mappings...")
            
            skip = 0
            limit = 100
            total_mappings = 0
            
            while True:
                try:
                    response = self.mappings_service.list_mappings(skip=skip, limit=limit)
                    mappings = response.get('mappings', [])
                    
                    if not mappings:
                        break
                    
                    self.discovered_entities["mappings"].extend(mappings)
                    total_mappings += len(mappings)
                    skip += limit
                    
                    logger.debug(f"Discovered {total_mappings} mappings so far...")
                    
                except Exception as e:
                    logger.warning(f"Error discovering mappings at skip={skip}: {e}")
                    self.discovery_errors.append(f"Mappings discovery error: {str(e)}")
                    break
            
            logger.info(f"Discovered {total_mappings} mappings")
            
        except Exception as e:
            logger.error(f"Failed to discover mappings: {e}")
            self.discovery_errors.append(f"Mappings discovery failed: {str(e)}")
    
    async def _discover_topology(self) -> None:
        """Discover topology structure"""
        try:
            logger.info("Discovering topology...")
            
            topology = self.topology_service.get_topology()
            
            if topology:
                nodes = topology.get('nodes', [])
                self.discovered_entities["topology_nodes"] = nodes
                logger.info(f"Discovered {len(nodes)} topology nodes")
            else:
                logger.warning("No topology data available")
                self.discovery_errors.append("Topology discovery returned no data")
            
        except Exception as e:
            logger.error(f"Failed to discover topology: {e}")
            self.discovery_errors.append(f"Topology discovery failed: {str(e)}")
    
    def _calculate_stats(self) -> None:
        """Calculate discovery statistics"""
        self.discovery_stats = {
            "total_files": len(self.discovered_entities["files"]),
            "total_documents": len(self.discovered_entities["documents"]),
            "total_components": len(self.discovered_entities["components"]),
            "total_mappings": len(self.discovered_entities["mappings"]),
            "total_topology_nodes": len(self.discovered_entities["topology_nodes"]),
            "total_errors": len(self.discovery_errors)
        }
        
        logger.info(f"Discovery stats: {self.discovery_stats}")
    
    def get_discovery_summary(self) -> Dict[str, Any]:
        """
        Get summary of discovery results
        
        Returns:
            Dictionary with discovery summary
        """
        return {
            "stats": self.discovery_stats,
            "errors": self.discovery_errors,
            "entities_discovered": {
                key: len(value) 
                for key, value in self.discovered_entities.items()
            }
        }

# Made with Bob
