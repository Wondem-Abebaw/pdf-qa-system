# 📚 PDF Document Q&A System

A production-ready **Retrieval-Augmented Generation (RAG)** application for intelligent question-answering across multiple PDF documents. Built with LangChain, ChromaDB, and Streamlit.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.1.16-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎯 Features

- **Multi-Document Processing**: Upload and process multiple PDF files simultaneously
- **Persistent Vector Storage**: ChromaDB for reliable, persistent embeddings storage
- **Advanced PDF Parsing**: PyMuPDF for robust text extraction with metadata
- **Intelligent Retrieval**: Similarity search with metadata filtering
- **Conversation Memory**: Context-aware responses using conversation history
- **Interactive UI**: Clean Streamlit interface with multiple tabs
- **Document Analytics**: View statistics and manage your knowledge base
- **Source Attribution**: Every answer cites specific document chunks
- **Production-Ready**: Proper error handling, logging, and configuration management

## 🏗️ Architecture

```
┌─────────────┐
│  Streamlit  │  User Interface
│     UI      │
└──────┬──────┘
       │
       v
┌─────────────┐
│  QA Chain   │  LangChain LCEL Pipeline
│   (LCEL)    │  + Conversation Memory
└──────┬──────┘
       │
       v
┌─────────────┐
│  Vector     │  ChromaDB
│   Store     │  + OpenAI Embeddings
└──────┬──────┘
       │
       v
┌─────────────┐
│  Document   │  PyMuPDF Parser
│  Processor  │  + Text Chunking
└─────────────┘
```

## 📋 Prerequisites

- Python 3.10 or higher
- OpenAI API key
- 2GB+ RAM (for vector operations)
- 1GB+ disk space (for ChromaDB persistence)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd pdf-qa-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Run the Application

```bash
streamlit run src/app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### Uploading Documents

1. Navigate to the **"Upload Documents"** tab
2. Click **"Browse files"** and select one or more PDF files
3. Click **"Process and Add to Knowledge Base"**
4. Wait for processing to complete

### Asking Questions

1. Go to the **"Ask Questions"** tab
2. (Optional) Filter by a specific document using the dropdown
3. Type your question in the text input
4. Click **"Ask"** to get an answer
5. View the answer and source citations

### Analytics & Management

1. Visit the **"Analytics"** tab to:
   - View collection statistics
   - Browse uploaded documents
   - See document metadata
   - Delete the entire knowledge base (if needed)

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | *Required* |
| `CHUNK_SIZE` | Text chunk size for splitting | 1000 |
| `CHUNK_OVERLAP` | Overlap between chunks | 200 |
| `EMBEDDING_MODEL` | OpenAI embedding model | text-embedding-3-small |
| `LLM_MODEL` | OpenAI LLM model | gpt-4-turbo-preview |
| `TEMPERATURE` | LLM temperature | 0.0 |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB storage path | ./data/chroma_db |
| `COLLECTION_NAME` | ChromaDB collection name | pdf_documents |

### Customizing Chunk Size

For different document types, you may want to adjust chunk size:

- **Research Papers**: 1000-1500 (default works well)
- **Legal Documents**: 1500-2000 (longer context)
- **Short Articles**: 500-800 (smaller chunks)

Edit in `.env`:
```
CHUNK_SIZE=1500
CHUNK_OVERLAP=300
```

## 🏗️ Project Structure

```
pdf-qa-system/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration management
│   ├── document_processor.py # PDF processing logic
│   ├── vector_store.py       # ChromaDB operations
│   ├── qa_chain.py           # RAG chain implementation
│   └── app.py                # Streamlit UI
├── data/
│   └── chroma_db/            # ChromaDB persistence (auto-created)
├── docs/                     # Additional documentation
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🧪 Key Technologies

### Core Stack

- **LangChain (0.1.16)**: Framework for LLM applications
- **OpenAI**: GPT-4 Turbo for generation, text-embedding-3-small for embeddings
- **ChromaDB (0.4.24)**: Vector database with persistence
- **Streamlit (1.32.2)**: Web UI framework
- **PyMuPDF (1.24.1)**: PDF parsing library

### Design Patterns

- **RAG (Retrieval-Augmented Generation)**: Core pattern for grounded responses
- **LCEL (LangChain Expression Language)**: For building composable chains
- **Pydantic Settings**: Type-safe configuration management
- **Conversation Memory**: For context-aware multi-turn conversations

## 📊 Performance Considerations

### Embedding Cost Calculation

Using `text-embedding-3-small`:
- Cost: $0.02 per 1M tokens
- Average PDF (20 pages): ~10,000 tokens
- 100 PDFs: ~$0.02

### LLM Cost Calculation

Using `gpt-4-turbo-preview`:
- Input: $10 per 1M tokens
- Output: $30 per 1M tokens
- Average query: ~2,000 input tokens, ~500 output tokens
- 1,000 queries: ~$35

## 🔒 Security Best Practices

1. **Never commit `.env`**: Your API keys should stay private
2. **Use environment variables**: For all sensitive configuration
3. **API key rotation**: Regularly rotate your OpenAI API key
4. **Input validation**: The app validates all user inputs
5. **Error handling**: Proper error messages without exposing internals

## 🐛 Troubleshooting

### "No module named 'src'"

Run the app from the project root directory:
```bash
cd pdf-qa-system
streamlit run src/app.py
```

### "ChromaDB connection error"

Ensure the data directory is writable:
```bash
mkdir -p data/chroma_db
chmod 755 data/chroma_db
```

### "OpenAI API key not found"

Check your `.env` file:
```bash
cat .env | grep OPENAI_API_KEY
```

### "PDF parsing failed"

Some PDFs may be scanned images. For OCR support, you'll need additional tools (Google Document AI or Tesseract).

## 🚀 Advanced Features

### Custom Retrieval Strategies

Modify `src/vector_store.py` to implement:
- **MMR (Maximal Marginal Relevance)**: For diverse results
- **Hybrid Search**: Combine semantic + keyword search
- **Reranking**: Use a cross-encoder for better ranking

### Multi-Agent Patterns

Extend this project to include:
- **Summarizer Agent**: Summarize documents before Q&A
- **Fact-Checker Agent**: Verify answers against sources
- **Router Agent**: Route questions to specialized agents

## 📈 Next Steps

To evolve this into Project 3-7:

1. **Add Tools** → Project 3: Web search, code execution
2. **Cloud Deployment** → Project 4: Google Cloud Storage + Cloud Run
3. **Vertex AI Integration** → Project 5: Use Vertex AI Gemini
4. **Multi-Agent System** → Project 6: LangGraph orchestration
5. **Production Backend** → Project 7: FastAPI + monitoring

## 📝 License

MIT License - feel free to use this for learning and portfolio projects!

## 🤝 Contributing

This is a learning project, but contributions are welcome:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📧 Support

For issues or questions:
- Open a GitHub issue
- Check existing issues for solutions

## 🎓 Learning Resources

- [LangChain Documentation](https://docs.langchain.com)
- [ChromaDB Documentation](https://docs.trychroma.com)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io)

---

**Built with ❤️ for AI Engineers**

Perfect for portfolios, interviews, and learning production RAG systems!
