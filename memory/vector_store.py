"""
Vector store for semantic search capabilities.
"""
import os
import logging
import datetime
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.docstore.document import Document

class VectorStore:
    """ChromaDB vector store for semantic memory"""
    
    def __init__(self, persist_directory):
        """Initialize the vector store"""
        self.logger = logging.getLogger(__name__)
        self.persist_directory = persist_directory
        
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings()
        
        # Initialize ChromaDB
        self.store = Chroma(
            collection_name="memories",
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
        
        self.logger.info(f"Vector store initialized at {persist_directory}")
    
    def add_texts(self, texts, metadatas=None):
        """Add texts to the vector store"""
        if not metadatas:
            metadatas = [{"timestamp": datetime.datetime.now().isoformat()} for _ in texts]
        
        try:
            ids = self.store.add_texts(texts=texts, metadatas=metadatas)
            self.store.persist()
            return ids
        except Exception as e:
            self.logger.error(f"Error adding texts to vector store: {e}", exc_info=True)
            return []
    
    def similarity_search(self, query, k=5):
        """Search for similar documents"""
        try:
            results = self.store.similarity_search(query, k=k)
            return results
        except Exception as e:
            self.logger.error(f"Error in similarity search: {e}", exc_info=True)
            return []
    
    def get_document_by_id(self, doc_id):
        """Retrieve a document by ID"""
        try:
            return self.store.get(ids=[doc_id])
        except Exception as e:
            self.logger.error(f"Error retrieving document by ID: {e}", exc_info=True)
            return None
    
    def close(self):
        """Close the vector store"""
        try:
            self.store.persist()
        except Exception as e:
            self.logger.error(f"Error closing vector store: {e}", exc_info=True)