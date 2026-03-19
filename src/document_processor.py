"""
Document processing module for PDF parsing, text extraction, and chunking.
Uses PyMuPDF (fitz) for robust PDF handling.
"""
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import hashlib

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from src.config import settings


class PDFProcessor:
    """Handles PDF document processing with metadata extraction."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize PDF processor.
        
        Args:
            chunk_size: Size of text chunks (defaults to settings)
            chunk_overlap: Overlap between chunks (defaults to settings)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_path: Path) -> tuple[str, Dict[str, Any]]:
        """
        Extract text and metadata from a PDF file using PyMuPDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (extracted_text, metadata_dict)
        """
        try:
            doc = fitz.open(pdf_path)
            
            # Extract metadata
            metadata = {
                "filename": pdf_path.name,
                "filepath": str(pdf_path.absolute()),
                "num_pages": doc.page_count,
                "file_size_mb": round(pdf_path.stat().st_size / (1024 * 1024), 2),
                "upload_timestamp": datetime.now().isoformat(),
                "file_hash": self._compute_file_hash(pdf_path),
            }
            
            # Extract PDF metadata
            pdf_metadata = doc.metadata
            if pdf_metadata:
                metadata.update({
                    "title": pdf_metadata.get("title", ""),
                    "author": pdf_metadata.get("author", ""),
                    "subject": pdf_metadata.get("subject", ""),
                    "creator": pdf_metadata.get("creator", ""),
                })
            
            # Extract text from all pages
            full_text = ""
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text()
                full_text += f"\n--- Page {page_num} ---\n{text}"
            
            doc.close()
            
            return full_text.strip(), metadata
            
        except Exception as e:
            raise Exception(f"Error processing PDF {pdf_path.name}: {str(e)}")
    
    def process_pdf(self, pdf_path: Path) -> List[Document]:
        """
        Process a PDF file into chunked LangChain Documents.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of LangChain Document objects with metadata
        """
        # Extract text and metadata
        text, metadata = self.extract_text_from_pdf(pdf_path)
        
        if not text.strip():
            raise ValueError(f"No text extracted from {pdf_path.name}")
        
        # Create chunks
        chunks = self.text_splitter.split_text(text)
        
        # Create Document objects with metadata
        documents = []
        for idx, chunk in enumerate(chunks):
            doc_metadata = metadata.copy()
            doc_metadata.update({
                "chunk_index": idx,
                "total_chunks": len(chunks),
                "chunk_size": len(chunk)
            })
            
            documents.append(Document(
                page_content=chunk,
                metadata=doc_metadata
            ))
        
        return documents
    
    def process_multiple_pdfs(self, pdf_paths: List[Path]) -> Dict[str, List[Document]]:
        """
        Process multiple PDF files.
        
        Args:
            pdf_paths: List of paths to PDF files
            
        Returns:
            Dictionary mapping filenames to their Document lists
        """
        results = {}
        errors = []
        
        for pdf_path in pdf_paths:
            try:
                documents = self.process_pdf(pdf_path)
                results[pdf_path.name] = documents
            except Exception as e:
                errors.append(f"{pdf_path.name}: {str(e)}")
        
        if errors:
            print(f"Errors processing {len(errors)} files:")
            for error in errors:
                print(f"  - {error}")
        
        return results
    
    @staticmethod
    def _compute_file_hash(file_path: Path) -> str:
        """
        Compute SHA256 hash of a file for deduplication.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hexadecimal hash string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def get_document_stats(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Get statistics about processed documents.
        
        Args:
            documents: List of LangChain Documents
            
        Returns:
            Dictionary with statistics
        """
        if not documents:
            return {}
        
        total_chars = sum(len(doc.page_content) for doc in documents)
        
        # Get unique files
        unique_files = set(doc.metadata.get("filename", "unknown") for doc in documents)
        
        return {
            "total_chunks": len(documents),
            "total_characters": total_chars,
            "avg_chunk_size": round(total_chars / len(documents)),
            "unique_files": len(unique_files),
            "files": list(unique_files)
        }
