import os
import logging
from typing import Dict, List, Any, Optional

from integrations.openai_client import OpenAIClient

class VectorStore:
    """Vector database for semantic search capabilities."""
    
    def __init__(self, collection_name: str = "conversations", persist_directory: str = "memory/vector_data"):
        """Initialize the vector store.
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist the vector database
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.logger = logging.getLogger("assistant.vector_store")
        
        # Ensure directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB
        try:
            import chromadb
            from chromadb.config import Settings
            
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(name=collection_name)
                self.logger.info(f"Using existing collection: {collection_name}")
            except:
                self.collection = self.client.create_collection(name=collection_name)
                self.logger.info(f"Created new collection: {collection_name}")
                
            self.openai_client = OpenAIClient()
            
        except ImportError:
            self.logger.error("ChromaDB not installed. Please install with: pip install chromadb")
            raise
            
        self.logger.info(f"Vector store initialized with collection '{collection_name}' at '{persist_directory}'")
    
    def add_text(self, text: str, metadata: Dict[str, Any]) -> str:
        """Add text to the vector store.
        
        Args:
            text: Text to add
            metadata: Metadata for the text
            
        Returns:
            ID of the added document
        """
        # Generate embeddings using OpenAI
        embeddings = self.openai_client.generate_embeddings(text)
        
        # Generate a unique ID based on timestamp and content
        import hashlib
        import time
        
        unique_id = hashlib.md5(f"{time.time()}-{text[:100]}".encode()).hexdigest()
        
        # Add to collection
        self.collection.add(
            ids=[unique_id],
            embeddings=[embeddings],
            metadatas=[metadata],
            documents=[text]
        )
        
        self.logger.debug(f"Added text to vector store with ID {unique_id}")
        return unique_id
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar texts.
        
        Args:
            query: Query text
            limit: Maximum number of results
            
        Returns:
            List of result dictionaries with text and metadata
        """
        # Generate embeddings for the query
        query_embedding = self.openai_client.generate_embeddings(query)
        
        # Search the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else None
                
                # Parse document to extract user message and assistant response
                parts = doc.split("User: ", 1)
                if len(parts) > 1:
                    user_part = parts[1].split("Assistant: ", 1)
                    if len(user_part) > 1:
                        user_message = user_part[0].strip()
                        assistant_response = user_part[1].strip()
                        
                        formatted_results.append({
                            "message": user_message,
                            "response": assistant_response,
                            "timestamp": metadata.get("timestamp", ""),
                            "similarity": 1.0 - (distance or 0) if distance is not None else 1.0
                        })
        
        self.logger.debug(f"Found {len(formatted_results)} relevant results for query")
        return formatted_results