"""
Metadata Intelligence Engine

Extracts, analyzes, and manages metadata from all discovered entities.
Provides metadata-based insights and relationship discovery.
"""

from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import json

from logger import get_logger

logger = get_logger(__name__)


class MetadataEngine:
    """
    Intelligent metadata extraction and analysis engine
    
    Automatically extracts metadata from all entities and discovers
    patterns, relationships, and anomalies.
    """
    
    def __init__(self):
        """Initialize Metadata Engine"""
        self.metadata_store: Dict[str, List[Dict[str, Any]]] = {
            "files": [],
            "documents": [],
            "components": [],
            "servers": [],
            "storage_pools": [],
            "volumes": [],
            "backup_objects": []
        }
        
        self.metadata_index: Dict[str, Set[str]] = {}
        self.entity_relationships: List[Dict[str, Any]] = []
        
        logger.info("Metadata Engine initialized")
    
    def extract_metadata(self, entities: Dict[str, List[Any]]) -> Dict[str, Any]:
        """
        Extract metadata from discovered entities
        
        Args:
            entities: Dictionary of discovered entities
            
        Returns:
            Dictionary with extracted metadata and statistics
        """
        logger.info("Extracting metadata from entities...")
        start_time = datetime.now()
        
        total_extracted = 0
        
        # Extract from files
        if entities.get("files"):
            file_metadata = self._extract_file_metadata(entities["files"])
            self.metadata_store["files"] = file_metadata
            total_extracted += len(file_metadata)
        
        # Extract from documents
        if entities.get("documents"):
            doc_metadata = self._extract_document_metadata(entities["documents"])
            self.metadata_store["documents"] = doc_metadata
            total_extracted += len(doc_metadata)
        
        # Extract from components
        if entities.get("components"):
            comp_metadata = self._extract_component_metadata(entities["components"])
            self.metadata_store["components"] = comp_metadata
            total_extracted += len(comp_metadata)
        
        # Build metadata index
        self._build_metadata_index()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Extracted {total_extracted} metadata records in {duration:.2f}s")
        
        return {
            "total_records": total_extracted,
            "by_type": {
                key: len(value) for key, value in self.metadata_store.items()
            },
            "index_size": len(self.metadata_index),
            "duration": duration
        }
    
    def _extract_file_metadata(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract metadata from files"""
        metadata = []
        
        for file in files:
            meta = {
                "entity_type": "file",
                "entity_id": file.get("id"),
                "name": file.get("name"),
                "path": file.get("path"),
                "size": file.get("size"),
                "created_at": file.get("created_at"),
                "modified_at": file.get("modified_at"),
                "file_type": file.get("file_type"),
                "mime_type": file.get("mime_type"),
                "checksum": file.get("checksum"),
                "tags": file.get("tags", []),
                "custom_metadata": file.get("metadata", {})
            }
            metadata.append(meta)
        
        return metadata
    
    def _extract_document_metadata(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract metadata from documents"""
        metadata = []
        
        for doc in documents:
            meta = {
                "entity_type": "document",
                "entity_id": doc.get("id"),
                "title": doc.get("title"),
                "content_type": doc.get("content_type"),
                "source_file_id": doc.get("file_id"),
                "chunk_count": doc.get("chunk_count"),
                "created_at": doc.get("created_at"),
                "indexed_at": doc.get("indexed_at"),
                "embedding_model": doc.get("embedding_model"),
                "tags": doc.get("tags", []),
                "custom_metadata": doc.get("metadata", {})
            }
            metadata.append(meta)
        
        return metadata
    
    def _extract_component_metadata(self, components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract metadata from components"""
        metadata = []
        
        for comp in components:
            meta = {
                "entity_type": "component",
                "entity_id": comp.get("id"),
                "name": comp.get("name"),
                "component_type": comp.get("type"),
                "parent_id": comp.get("parent_id"),
                "properties": comp.get("properties", {}),
                "created_at": comp.get("created_at"),
                "updated_at": comp.get("updated_at"),
                "tags": comp.get("tags", []),
                "custom_metadata": comp.get("metadata", {})
            }
            metadata.append(meta)
        
        return metadata
    
    def _build_metadata_index(self) -> None:
        """Build searchable metadata index"""
        logger.info("Building metadata index...")
        
        self.metadata_index.clear()
        
        for entity_type, records in self.metadata_store.items():
            for record in records:
                # Index by entity ID
                entity_id = record.get("entity_id")
                if entity_id:
                    if entity_id not in self.metadata_index:
                        self.metadata_index[entity_id] = set()
                    self.metadata_index[entity_id].add(entity_type)
                
                # Index by name
                name = record.get("name") or record.get("title")
                if name:
                    if name not in self.metadata_index:
                        self.metadata_index[name] = set()
                    self.metadata_index[name].add(entity_type)
        
        logger.info(f"Built index with {len(self.metadata_index)} entries")
    
    def discover_relationships(self) -> List[Dict[str, Any]]:
        """
        Discover relationships between entities based on metadata
        
        Returns:
            List of discovered relationships
        """
        logger.info("Discovering metadata-based relationships...")
        
        relationships = []
        
        # Discover file -> document relationships
        for doc_meta in self.metadata_store["documents"]:
            source_file_id = doc_meta.get("source_file_id")
            if source_file_id:
                relationships.append({
                    "type": "file_to_document",
                    "source_type": "file",
                    "source_id": source_file_id,
                    "target_type": "document",
                    "target_id": doc_meta.get("entity_id"),
                    "relationship": "generates",
                    "confidence": 1.0
                })
        
        # Discover component hierarchy relationships
        for comp_meta in self.metadata_store["components"]:
            parent_id = comp_meta.get("parent_id")
            if parent_id:
                relationships.append({
                    "type": "component_hierarchy",
                    "source_type": "component",
                    "source_id": parent_id,
                    "target_type": "component",
                    "target_id": comp_meta.get("entity_id"),
                    "relationship": "contains",
                    "confidence": 1.0
                })
        
        self.entity_relationships = relationships
        logger.info(f"Discovered {len(relationships)} relationships")
        
        return relationships
    
    def get_metadata_summary(self) -> Dict[str, Any]:
        """
        Get summary of metadata analysis
        
        Returns:
            Dictionary with metadata summary
        """
        return {
            "total_records": sum(len(v) for v in self.metadata_store.values()),
            "by_type": {k: len(v) for k, v in self.metadata_store.items()},
            "index_size": len(self.metadata_index),
            "relationships_discovered": len(self.entity_relationships)
        }
    
    def search_metadata(self, query: str) -> List[Dict[str, Any]]:
        """
        Search metadata by query
        
        Args:
            query: Search query
            
        Returns:
            List of matching metadata records
        """
        results = []
        query_lower = query.lower()
        
        for entity_type, records in self.metadata_store.items():
            for record in records:
                # Search in name/title
                name = (record.get("name") or record.get("title") or "").lower()
                if query_lower in name:
                    results.append(record)
                    continue
                
                # Search in tags
                tags = record.get("tags", [])
                if any(query_lower in str(tag).lower() for tag in tags):
                    results.append(record)
        
        return results

# Made with Bob
