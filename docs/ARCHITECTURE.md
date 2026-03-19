# Technical Architecture

## System Overview

The PDF Q&A System is built using a modern RAG (Retrieval-Augmented Generation) architecture with production-ready components.

## Core Components

### 1. Document Processor (`document_processor.py`)

**Responsibilities:**
- PDF text extraction using PyMuPDF
- Metadata extraction (title, author, page count, etc.)
- Text chunking with RecursiveCharacterTextSplitter
- File hash computation for deduplication
- Multi-document batch processing

**Key Features:**
- Robust error handling for corrupted PDFs
- Hierarchical text splitting (paragraphs → sentences → words)
- Metadata propagation to all chunks
- Statistics calculation for processed documents

**Text Splitting Strategy:**
```python
separators = ["\n\n", "\n", ". ", " ", ""]
```
This ensures logical boundaries:
1. Paragraph breaks (highest priority)
2. Line breaks
3. Sentence endings
4. Word boundaries

### 2. Vector Store Manager (`vector_store.py`)

**Responsibilities:**
- ChromaDB initialization and management
- Document embedding and storage
- Similarity search with metadata filtering
- Collection statistics and management

**Key Features:**
- Persistent storage (survives restarts)
- Automatic collection creation/loading
- Metadata-based filtering
- Score-based retrieval

**ChromaDB Configuration:**
```python
ChromaSettings(
    anonymized_telemetry=False,  # Disable telemetry
    persist_directory="./data/chroma_db"
)
```

### 3. QA Chain (`qa_chain.py`)

**Responsibilities:**
- LangChain LCEL pipeline construction
- Conversation memory management
- Context formatting
- Answer generation with source attribution

**Key Features:**
- LCEL (LangChain Expression Language) for composability
- ConversationBufferMemory for multi-turn conversations
- Parallel retrieval and context formatting
- Metadata-based document filtering

**LCEL Pipeline:**
```python
chain = (
    RunnableParallel(
        context=retriever | format_docs,
        question=RunnablePassthrough(),
        chat_history=lambda x: memory.load_memory_variables({})
    )
    | prompt
    | llm
    | StrOutputParser()
)
```

### 4. Streamlit UI (`app.py`)

**Responsibilities:**
- User interface rendering
- File upload handling
- Interactive Q&A
- Analytics and document management

**Key Features:**
- Multi-tab interface
- Real-time processing feedback
- Document filtering
- Conversation history display
- Collection management

## Data Flow

### Document Ingestion Flow
```
User uploads PDF
    ↓
Save to temporary storage
    ↓
PDFProcessor extracts text + metadata
    ↓
Text split into chunks (RecursiveCharacterTextSplitter)
    ↓
Each chunk → Document with metadata
    ↓
VectorStoreManager creates embeddings (OpenAI)
    ↓
Store in ChromaDB with persistence
```

### Question Answering Flow
```
User asks question
    ↓
QAChain.ask() invoked
    ↓
Retriever searches ChromaDB (similarity search)
    ↓
Top k relevant chunks retrieved
    ↓
Chunks formatted as context
    ↓
Context + Question + Chat History → Prompt
    ↓
LLM generates answer (GPT-4)
    ↓
Answer + Source documents returned
    ↓
Update conversation memory
```

## Design Patterns

### 1. Repository Pattern
`VectorStoreManager` abstracts ChromaDB operations, making it easy to swap vector databases.

### 2. Strategy Pattern
`PDFProcessor` uses configurable chunking strategies via `RecursiveCharacterTextSplitter`.

### 3. Chain of Responsibility
LCEL pipeline processes queries through multiple stages (retrieval → formatting → generation).

### 4. Singleton Pattern
`Settings` class uses Pydantic's singleton behavior for configuration management.

## Configuration Management

### Environment-Based Configuration
Using `pydantic-settings` for type-safe configuration:

```python
class Settings(BaseSettings):
    openai_api_key: str  # Required
    chunk_size: int = 1000  # Default
    temperature: float = 0.0  # Default
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
```

**Benefits:**
- Type validation at runtime
- IDE autocomplete
- Environment variable override
- Default values
- Automatic `.env` file loading

## Memory Management

### Conversation Memory
- **Type**: ConversationBufferMemory
- **Storage**: In-memory (lost on restart)
- **Scope**: Per-session

**Future Enhancement:** Replace with persistent memory (Redis, PostgreSQL) for multi-session continuity.

### Vector Memory
- **Type**: Persistent ChromaDB
- **Storage**: Disk-based (survives restarts)
- **Scope**: Global (shared across all users)

## Error Handling Strategy

### Layered Error Handling
1. **Component Level**: Each module has try-except blocks
2. **UI Level**: Streamlit displays user-friendly error messages
3. **Logging**: Errors are logged (can be extended with proper logging framework)

### Example Error Propagation
```python
# Component level
try:
    documents = processor.process_pdf(pdf_path)
except Exception as e:
    raise Exception(f"Error processing PDF {pdf_path.name}: {str(e)}")

# UI level
try:
    vector_store.add_documents(documents)
    st.success("Documents added!")
except Exception as e:
    st.error(f"Error: {str(e)}")
```

## Performance Considerations

### Chunking Optimization
- **Chunk Size**: 1000 characters balances context vs. precision
- **Overlap**: 200 characters prevents information loss at boundaries
- **Separators**: Hierarchical splitting maintains semantic coherence

### Embedding Optimization
- **Model**: `text-embedding-3-small` for cost efficiency
- **Batch Processing**: Process multiple documents in parallel
- **Caching**: ChromaDB automatically caches embeddings

### Retrieval Optimization
- **k-value**: Default 4 chunks balances context vs. noise
- **Metadata Filtering**: Pre-filter by filename to reduce search space
- **Score Threshold**: Can be added for quality filtering

## Security Considerations

### API Key Management
- Stored in `.env` file (not committed to Git)
- Loaded via `pydantic-settings`
- Never exposed in logs or UI

### Input Validation
- File type validation (PDF only)
- File size limits (implicit via Streamlit)
- Query length limits (via LLM max tokens)

### Data Persistence
- ChromaDB stored locally (user-controlled)
- No data sent to third parties except OpenAI API
- Temporary uploads cleaned up (in `/tmp`)

## Extensibility Points

### 1. Add New Document Types
Extend `PDFProcessor` to support DOCX, TXT, HTML:
```python
class DocumentProcessor:
    def process_file(self, file_path: Path):
        if file_path.suffix == '.pdf':
            return self._process_pdf(file_path)
        elif file_path.suffix == '.docx':
            return self._process_docx(file_path)
```

### 2. Add New Vector Stores
Implement new `VectorStoreManager` for Pinecone, Weaviate:
```python
class PineconeVectorStore(VectorStoreManager):
    def __init__(self):
        # Pinecone-specific initialization
        pass
```

### 3. Add New LLMs
Swap OpenAI for other providers:
```python
# In qa_chain.py
from langchain_google_vertexai import ChatVertexAI
self.llm = ChatVertexAI(model="gemini-pro")
```

### 4. Add Authentication
Add user authentication to Streamlit:
```python
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(...)
name, authentication_status, username = authenticator.login()
```

## Testing Strategy

### Unit Tests (Future)
- Test document processing logic
- Test chunking strategies
- Test vector store operations
- Test QA chain logic

### Integration Tests (Future)
- Test end-to-end document ingestion
- Test end-to-end Q&A flow
- Test error handling

### Example Test Structure
```python
def test_pdf_processing():
    processor = PDFProcessor()
    docs = processor.process_pdf(Path("test.pdf"))
    assert len(docs) > 0
    assert all(doc.metadata.get("filename") for doc in docs)
```

## Monitoring and Observability

### Metrics to Track (Future)
- Query latency (retrieval + generation)
- Token usage per query
- Error rates
- User satisfaction (thumbs up/down)
- Document upload success rate

### LangSmith Integration (Optional)
Enable tracing for debugging:
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
```

## Scaling Considerations

### Current Limitations
- In-memory conversation history (lost on restart)
- Single ChromaDB instance (no multi-user isolation)
- No authentication (anyone can access)

### Scaling to Production
1. **Database**: Migrate to managed vector DB (Pinecone, Weaviate)
2. **Memory**: Use Redis for conversation persistence
3. **Auth**: Add user authentication and authorization
4. **Multi-tenancy**: Isolate users with namespace/collection per user
5. **Caching**: Cache frequent queries with Redis
6. **Load Balancing**: Deploy multiple instances behind load balancer

## Cost Analysis

### Per-Document Cost
- **Embedding**: ~10,000 tokens × $0.02/1M = $0.0002
- **Storage**: ChromaDB is free (local storage cost only)

### Per-Query Cost
- **Retrieval**: Free (local vector search)
- **Generation**: ~2,000 input + 500 output tokens
  - Input: 2,000 × $10/1M = $0.02
  - Output: 500 × $30/1M = $0.015
  - Total: ~$0.035 per query

### Monthly Cost Estimate (1000 queries/month, 100 documents)
- Documents: $0.02
- Queries: $35
- **Total: ~$35/month**

## Technology Stack Rationale

| Technology | Why Chosen |
|-----------|------------|
| **LangChain** | Industry-standard RAG framework, extensive ecosystem |
| **ChromaDB** | Easy setup, persistent storage, good for prototyping |
| **PyMuPDF** | Best PDF parsing library, handles complex layouts |
| **Streamlit** | Rapid UI development, Python-native, great for demos |
| **Pydantic** | Type safety, validation, auto-documentation |
| **OpenAI** | High-quality embeddings and generation, reliable API |

## Future Enhancements

### Short-term
1. Add document deletion feature
2. Export conversation history
3. Batch document upload
4. Advanced search filters

### Medium-term
1. Multi-user authentication
2. Document tagging/categorization
3. Custom embedding models
4. Query caching

### Long-term
1. Multi-modal support (images in PDFs)
2. Agent-based question decomposition
3. Fact verification
4. Citation linking to exact PDF locations

---

This architecture is designed for:
- **Learning**: Clear separation of concerns, well-documented
- **Extensibility**: Easy to add new features and providers
- **Production-readiness**: Error handling, configuration management, persistence
- **Performance**: Optimized chunking, efficient retrieval, caching-ready

Perfect foundation for building more advanced AI applications!
