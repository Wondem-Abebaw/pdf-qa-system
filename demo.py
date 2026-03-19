"""
Demo script to test the PDF Q&A system programmatically.
Use this to understand how to integrate the system into other applications.
"""
from pathlib import Path
from src.document_processor import PDFProcessor
from src.vector_store import VectorStoreManager
from src.qa_chain import QAChain


def demo_basic_workflow():
    """Demonstrate basic document processing and Q&A workflow."""
    
    print("=" * 60)
    print("PDF Q&A System - Programmatic Demo")
    print("=" * 60)
    
    # Initialize components
    print("\n1. Initializing system components...")
    processor = PDFProcessor()
    vector_store = VectorStoreManager()
    qa_chain = QAChain(vector_store)
    print("✓ System initialized")
    
    # Check if we have documents
    stats = vector_store.get_collection_stats()
    print(f"\n2. Current knowledge base:")
    print(f"   - Documents: {stats.get('unique_documents', 0)}")
    print(f"   - Total chunks: {stats.get('total_chunks', 0)}")
    
    if stats.get('total_chunks', 0) == 0:
        print("\n⚠️  No documents in the knowledge base.")
        print("   Please add PDF files using the Streamlit UI first.")
        return
    
    # Show available documents
    if stats.get('document_names'):
        print(f"\n3. Available documents:")
        for doc in stats['document_names']:
            print(f"   - {doc}")
    
    # Interactive Q&A
    print("\n4. Interactive Q&A (type 'quit' to exit, 'history' to see chat history)")
    print("-" * 60)
    
    while True:
        question = input("\nYour question: ").strip()
        
        if not question:
            continue
        
        if question.lower() == 'quit':
            print("Goodbye!")
            break
        
        if question.lower() == 'history':
            history = qa_chain.get_conversation_history()
            if history:
                print("\n--- Conversation History ---")
                for turn in history:
                    print(f"{turn['role'].upper()}: {turn['content']}")
                print("-" * 60)
            else:
                print("No conversation history yet.")
            continue
        
        try:
            # Get answer
            result = qa_chain.ask_with_sources(question)
            
            # Display answer
            print(f"\nAnswer: {result['answer']}")
            
            # Display sources
            if result['sources']:
                print(f"\nSources ({len(result['sources'])} chunks):")
                for idx, source in enumerate(result['sources'], 1):
                    print(f"  [{idx}] {source['filename']} (chunk {source['chunk_index']})")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


def demo_document_filtering():
    """Demonstrate document-specific queries."""
    
    print("\n" + "=" * 60)
    print("Document Filtering Demo")
    print("=" * 60)
    
    vector_store = VectorStoreManager()
    qa_chain = QAChain(vector_store)
    
    stats = vector_store.get_collection_stats()
    available_docs = stats.get('document_names', [])
    
    if not available_docs:
        print("No documents available for filtering demo.")
        return
    
    print(f"\nAvailable documents:")
    for idx, doc in enumerate(available_docs, 1):
        print(f"{idx}. {doc}")
    
    # Example filtered query
    if len(available_docs) >= 1:
        target_doc = available_docs[0]
        print(f"\nQuerying only '{target_doc}'...")
        
        question = "What is this document about?"
        result = qa_chain.ask_with_sources(
            question,
            metadata_filter={"filename": target_doc}
        )
        
        print(f"\nQuestion: {question}")
        print(f"Answer: {result['answer']}")
        print(f"Sources: {len(result['sources'])} chunks from {target_doc}")


def demo_collection_management():
    """Demonstrate collection statistics and management."""
    
    print("\n" + "=" * 60)
    print("Collection Management Demo")
    print("=" * 60)
    
    vector_store = VectorStoreManager()
    
    # Get comprehensive stats
    stats = vector_store.get_collection_stats()
    
    print("\nCollection Statistics:")
    print(f"  Collection name: {stats.get('collection_name', 'N/A')}")
    print(f"  Persist directory: {stats.get('persist_directory', 'N/A')}")
    print(f"  Total chunks: {stats.get('total_chunks', 0)}")
    print(f"  Unique documents: {stats.get('unique_documents', 0)}")
    
    # Show document details
    if stats.get('document_names'):
        print("\nDocument Details:")
        for doc_name in stats['document_names']:
            chunks = vector_store.filter_by_filename(doc_name)
            if chunks:
                metadata = chunks[0].metadata
                print(f"\n  📄 {doc_name}")
                print(f"     - Chunks: {len(chunks)}")
                print(f"     - Size: {metadata.get('file_size_mb', 'N/A')} MB")
                print(f"     - Pages: {metadata.get('num_pages', 'N/A')}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "filter":
            demo_document_filtering()
        elif mode == "stats":
            demo_collection_management()
        else:
            print(f"Unknown mode: {mode}")
            print("Available modes: filter, stats")
    else:
        # Default: run basic workflow
        demo_basic_workflow()
