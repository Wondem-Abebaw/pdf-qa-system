"""
Vector store management using ChromaDB with persistence.
Handles document embedding, storage, and retrieval.
"""
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from src.config import settings


class VectorStoreManager:
    """Manages ChromaDB vector store operations."""
    
    def __init__(self, persist_directory: Optional[Path] = None, collection_name: Optional[str] = None):
        """
        Initialize vector store manager.
        
        Args:
            persist_directory: Path to ChromaDB persistence directory
            collection_name: Name of the ChromaDB collection
        """
        self.persist_directory = persist_directory or settings.chroma_path
        self.collection_name = collection_name or settings.collection_name
        
        # Ensure directory exists
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # Initialize or load vector store
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize or load existing ChromaDB vector store."""
        try:
            # Check if collection already exists
            client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            
            existing_collections = [col.name for col in client.list_collections()]
            
            if self.collection_name in existing_collections:
                # Load existing collection
                self.vectorstore = Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=str(self.persist_directory)
                )
                print(f"✓ Loaded existing collection '{self.collection_name}'")
            else:
                # Create new collection
                self.vectorstore = Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=str(self.persist_directory)
                )
                print(f"✓ Created new collection '{self.collection_name}'")
                
        except Exception as e:
            raise Exception(f"Error initializing vector store: {str(e)}")
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of LangChain Documents to add
            
        Returns:
            List of document IDs
        """
        if not documents:
            raise ValueError("No documents provided")
        
        try:
            # Add documents and get IDs
            ids = self.vectorstore.add_documents(documents)
            
            # ChromaDB automatically persists, but we can explicitly persist
            # Note: Chroma.from_documents handles persistence automatically
            
            print(f"✓ Added {len(documents)} document chunks to vector store")
            return ids
            
        except Exception as e:
            raise Exception(f"Error adding documents to vector store: {str(e)}")
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Perform similarity search.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Metadata filter (e.g., {"filename": "report.pdf"})
            
        Returns:
            List of relevant Documents
        """
        try:
            if filter:
                results = self.vectorstore.similarity_search(
                    query=query,
                    k=k,
                    filter=filter
                )
            else:
                results = self.vectorstore.similarity_search(
                    query=query,
                    k=k
                )
            return results
            
        except Exception as e:
            raise Exception(f"Error performing similarity search: {str(e)}")
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple[Document, float]]:
        """
        Perform similarity search with relevance scores.
        
        Args:
            query: Search query
            k: Number of results to return
            filter: Metadata filter
            
        Returns:
            List of (Document, score) tuples
        """
        try:
            if filter:
                results = self.vectorstore.similarity_search_with_score(
                    query=query,
                    k=k,
                    filter=filter
                )
            else:
                results = self.vectorstore.similarity_search_with_score(
                    query=query,
                    k=k
                )
            return results
            
        except Exception as e:
            raise Exception(f"Error performing similarity search with score: {str(e)}")
    
    def get_retriever(self, search_kwargs: Optional[Dict[str, Any]] = None):
        """
        Get a retriever for use in chains.
        
        Args:
            search_kwargs: Keyword arguments for search (k, filter, etc.)
            
        Returns:
            LangChain retriever object
        """
        if search_kwargs is None:
            search_kwargs = {"k": 4}
        
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)
    
    def delete_collection(self):
        """Delete the entire collection (use with caution!)."""
        try:
            self.vectorstore.delete_collection()
            print(f"✓ Deleted collection '{self.collection_name}'")
            # Reinitialize
            self._initialize_vectorstore()
        except Exception as e:
            raise Exception(f"Error deleting collection: {str(e)}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            
            # Get unique filenames
            if count > 0:
                results = collection.get(limit=count)
                filenames = set()
                if results and "metadatas" in results:
                    for metadata in results["metadatas"]:
                        if metadata and "filename" in metadata:
                            filenames.add(metadata["filename"])
            else:
                filenames = set()
            
            return {
                "total_chunks": count,
                "unique_documents": len(filenames),
                "collection_name": self.collection_name,
                "persist_directory": str(self.persist_directory),
                "document_names": sorted(list(filenames))
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "collection_name": self.collection_name
            }
    
    def filter_by_filename(self, filename: str) -> List[Document]:
        """
        Get all chunks from a specific document.
        
        Args:
            filename: Name of the document
            
        Returns:
            List of Documents from that file
        """
        try:
            collection = self.vectorstore._collection
            results = collection.get(
                where={"filename": filename}
            )
            
            documents = []
            if results and "documents" in results and "metadatas" in results:
                for doc_text, metadata in zip(results["documents"], results["metadatas"]):
                    documents.append(Document(
                        page_content=doc_text,
                        metadata=metadata
                    ))
            
            return documents
            
        except Exception as e:
            raise Exception(f"Error filtering by filename: {str(e)}")
