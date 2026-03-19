"""
Streamlit web application for PDF Document Q&A System.
Multi-tab interface with document management, Q&A, and analytics.
"""
import streamlit as st
from pathlib import Path
import tempfile
import os
from typing import List

from src.config import settings
from src.document_processor import PDFProcessor
from src.vector_store import VectorStoreManager
from src.qa_chain import QAChain


# Page configuration
st.set_page_config(
    page_title="PDF Q&A System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .document-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 0.5rem;
    }
    .source-box {
        padding: 1rem;
        border-left: 3px solid #1f77b4;
        background-color: #f8f9fa;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_system():
    """Initialize the document processing system (cached)."""
      # Create three objects that will do the work
    processor = PDFProcessor() # Reads PDFs
    vector_store = VectorStoreManager()  # Stores chunks
    qa_chain = QAChain(vector_store)  # Answers questions
    return processor, vector_store, qa_chain


def save_uploaded_file(uploaded_file) -> Path:
    """Save uploaded file to temporary directory."""
    temp_dir = Path(tempfile.gettempdir()) / "pdf_qa_uploads"
    temp_dir.mkdir(exist_ok=True)
    
    file_path = temp_dir / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path


def render_sidebar():
    """Render sidebar with settings and info."""
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Model settings
        st.markdown("**LLM Model**")
        st.text(settings.llm_model)
        
        st.markdown("**Embedding Model**")
        st.text(settings.embedding_model)
        
        # Retrieval settings
        st.markdown("---")
        st.markdown("**Retrieval Settings**")
        
        k_docs = st.slider(
            "Number of chunks to retrieve",
            min_value=1,
            max_value=10,
            value=4,
            help="More chunks = more context but slower"
        )
        
        st.markdown("---")
        st.markdown("**Chunk Settings**")
        st.text(f"Chunk Size: {settings.chunk_size}")
        st.text(f"Overlap: {settings.chunk_overlap}")
        
        return k_docs


def render_document_upload_tab(processor, vector_store):
    """Render document upload and management tab."""
    st.markdown('<p class="main-header">📤 Upload Documents</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload PDF files to add them to the knowledge base</p>', unsafe_allow_html=True)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more PDF files"
    )
    
    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected**")
        
        if st.button("Process and Add to Knowledge Base", type="primary"):
            with st.spinner("Processing documents..."):
                progress_bar = st.progress(0)
                all_documents = []
                
                for idx, uploaded_file in enumerate(uploaded_files):
                    st.text(f"Processing: {uploaded_file.name}")
                    
                    # Save file
                    file_path = save_uploaded_file(uploaded_file)
                    
                    try:
                        # Process PDF
                        documents = processor.process_pdf(file_path)
                        all_documents.extend(documents)
                        
                        st.success(f"✓ {uploaded_file.name}: {len(documents)} chunks created")
                        
                    except Exception as e:
                        st.error(f"✗ Error processing {uploaded_file.name}: {str(e)}")
                    
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                
                # Add to vector store
                if all_documents:
                    with st.spinner("Adding documents to vector store..."):
                        try:
                            vector_store.add_documents(all_documents)
                            st.success(f"✓ Successfully added {len(all_documents)} chunks to knowledge base!")
                            
                            # Show stats
                            stats = processor.get_document_stats(all_documents)
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Total Chunks", stats["total_chunks"])
                            col2.metric("Unique Files", stats["unique_files"])
                            col3.metric("Avg Chunk Size", stats["avg_chunk_size"])
                            
                        except Exception as e:
                            st.error(f"Error adding to vector store: {str(e)}")


def render_qa_tab(qa_chain, vector_store, k_docs):
    """Render Q&A interface tab."""
    st.markdown('<p class="main-header">💬 Ask Questions</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Query your documents using natural language</p>', unsafe_allow_html=True)
    
    # Get collection stats
    stats = vector_store.get_collection_stats()
    
    if stats.get("total_chunks", 0) == 0:
        st.warning("⚠️ No documents in the knowledge base. Please upload documents first.")
        return
    
    # Display stats
    col1, col2 = st.columns([3, 1])
    with col2:
        st.metric("Documents", stats.get("unique_documents", 0))
        st.metric("Total Chunks", stats.get("total_chunks", 0))
    
    # Document filter
    with col1:
        available_docs = stats.get("document_names", [])
        if available_docs:
            filter_option = st.selectbox(
                "Filter by document (optional)",
                ["All documents"] + available_docs,
                help="Optionally search within a specific document"
            )
        else:
            filter_option = "All documents"
    
    # Update k_docs in chain
    qa_chain.update_k_documents(k_docs)
    
    # Question input
    question = st.text_input(
        "Your Question",
        placeholder="What is this document about?",
        help="Ask a question about your documents"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        ask_button = st.button("Ask", type="primary")
    with col2:
        if st.button("Clear History"):
            qa_chain.clear_history()
            st.success("Conversation history cleared!")
    
    if ask_button and question:
        with st.spinner("Searching documents and generating answer..."):
            try:
                # Apply filter if selected
                metadata_filter = None
                if filter_option != "All documents":
                    metadata_filter = {"filename": filter_option}
                
                # Get answer
                result = qa_chain.ask_with_sources(question, metadata_filter)
                
                # Display answer
                st.markdown("### Answer")
                st.markdown(f'<div class="source-box">{result["answer"]}</div>', unsafe_allow_html=True)
                
                # Display sources
                st.markdown("### Sources")
                for idx, source in enumerate(result["sources"], 1):
                    with st.expander(f"📄 Source {idx}: {source['filename']} (Chunk {source['chunk_index']})"):
                        st.text(source["content_preview"])
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display conversation history
    if st.checkbox("Show Conversation History"):
        history = qa_chain.get_conversation_history()
        if history:
            st.markdown("### Conversation History")
            for turn in history:
                if turn["role"] == "human":
                    st.markdown(f"**You:** {turn['content']}")
                else:
                    st.markdown(f"**Assistant:** {turn['content']}")
                st.markdown("---")
        else:
            st.info("No conversation history yet.")


def render_analytics_tab(vector_store):
    """Render analytics and document management tab."""
    st.markdown('<p class="main-header">📊 Knowledge Base Analytics</p>', unsafe_allow_html=True)
    
    stats = vector_store.get_collection_stats()
    
    if stats.get("total_chunks", 0) == 0:
        st.info("No documents in the knowledge base yet.")
        return
    
    # Overall statistics
    st.markdown("### Overall Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Documents", stats.get("unique_documents", 0))
    col2.metric("Total Chunks", stats.get("total_chunks", 0))
    col3.metric("Collection Name", stats.get("collection_name", "N/A"))
    
    # Document list
    st.markdown("### Documents in Knowledge Base")
    docs = stats.get("document_names", [])
    
    for doc_name in docs:
        with st.expander(f"📄 {doc_name}"):
            try:
                doc_chunks = vector_store.filter_by_filename(doc_name)
                st.text(f"Number of chunks: {len(doc_chunks)}")
                
                if doc_chunks:
                    metadata = doc_chunks[0].metadata
                    st.text(f"File size: {metadata.get('file_size_mb', 'N/A')} MB")
                    st.text(f"Pages: {metadata.get('num_pages', 'N/A')}")
                    st.text(f"Uploaded: {metadata.get('upload_timestamp', 'N/A')}")
            except Exception as e:
                st.error(f"Error loading document info: {str(e)}")
    
    # Danger zone
    st.markdown("---")
    st.markdown("### ⚠️ Danger Zone")
    if st.button("Delete All Documents", type="secondary"):
        if st.checkbox("I understand this will delete all documents"):
            try:
                vector_store.delete_collection()
                st.success("All documents deleted successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting collection: {str(e)}")


def main():
    """Main application entry point."""
    
    # Header
    st.markdown('<p class="main-header">📚 PDF Document Q&A System</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-powered document search and question answering using RAG</p>', unsafe_allow_html=True)
    
    # Initialize system
    try:
        processor, vector_store, qa_chain = initialize_system()
    except Exception as e:
        st.error(f"Error initializing system: {str(e)}")
        st.info("Make sure your .env file is configured with OPENAI_API_KEY")
        return
    
    # Sidebar
    k_docs = render_sidebar()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload Documents", "💬 Ask Questions", "📊 Analytics"])
    
    with tab1:
        render_document_upload_tab(processor, vector_store)
    
    with tab2:
        render_qa_tab(qa_chain, vector_store, k_docs)
    
    with tab3:
        render_analytics_tab(vector_store)


if __name__ == "__main__":
    main()
