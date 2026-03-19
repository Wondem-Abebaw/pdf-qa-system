"""
Generate a sample PDF for testing the PDF Q&A System.
Run this script to create a test PDF with sample content.
"""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from pathlib import Path


def create_sample_pdf():
    """Create a sample PDF document for testing."""
    
    output_dir = Path("sample_documents")
    output_dir.mkdir(exist_ok=True)
    
    pdf_path = output_dir / "ai_engineering_guide.pdf"
    
    # Create PDF
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        title="AI Engineering Guide",
        author="PDF Q&A System",
        subject="Sample Document"
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1f77b4',
        spaceAfter=30
    )
    heading_style = styles['Heading2']
    body_style = styles['BodyText']
    
    # Content
    story = []
    
    # Title
    story.append(Paragraph("AI Engineering Guide", title_style))
    story.append(Spacer(1, 0.5 * inch))
    
    # Introduction
    story.append(Paragraph("Introduction", heading_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "This document provides a comprehensive overview of AI engineering concepts, "
        "including Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), "
        "and production deployment strategies. It serves as a reference guide for "
        "building scalable AI applications.",
        body_style
    ))
    story.append(Spacer(1, 0.3 * inch))
    
    # Section 1
    story.append(Paragraph("1. Large Language Models (LLMs)", heading_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "Large Language Models are neural networks trained on vast amounts of text data. "
        "They can generate human-like text, answer questions, summarize documents, and "
        "perform various natural language processing tasks. Common LLMs include GPT-4, "
        "Claude, Gemini, and Llama. These models work by predicting the next token in a "
        "sequence based on the context of previous tokens.",
        body_style
    ))
    story.append(Spacer(1, 0.3 * inch))
    
    # Section 2
    story.append(Paragraph("2. Retrieval-Augmented Generation (RAG)", heading_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "RAG is a technique that combines information retrieval with text generation. "
        "Instead of relying solely on the LLM's training data, RAG systems retrieve "
        "relevant information from a knowledge base and use it as context for generating "
        "responses. This approach reduces hallucinations, provides up-to-date information, "
        "and enables source attribution. The RAG pipeline typically includes document "
        "chunking, embedding generation, vector storage, similarity search, and "
        "context-aware generation.",
        body_style
    ))
    story.append(Spacer(1, 0.3 * inch))
    
    story.append(PageBreak())
    
    # Section 3
    story.append(Paragraph("3. Vector Databases", heading_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "Vector databases store and index high-dimensional embeddings for efficient "
        "similarity search. Popular vector databases include ChromaDB, Pinecone, Weaviate, "
        "Qdrant, and FAISS. They use algorithms like HNSW (Hierarchical Navigable Small "
        "World) and IVF (Inverted File Index) to enable fast approximate nearest neighbor "
        "search. Key considerations when choosing a vector database include query latency, "
        "scalability, persistence, and metadata filtering capabilities.",
        body_style
    ))
    story.append(Spacer(1, 0.3 * inch))
    
    # Section 4
    story.append(Paragraph("4. Embedding Models", heading_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "Embedding models convert text into dense vector representations that capture "
        "semantic meaning. OpenAI's text-embedding-3-small and text-embedding-3-large are "
        "popular choices, offering a good balance of quality and cost. Other options "
        "include Cohere embeddings, Google's Vertex AI embeddings, and open-source models "
        "like sentence-transformers. The quality of embeddings directly impacts retrieval "
        "accuracy in RAG systems.",
        body_style
    ))
    story.append(Spacer(1, 0.3 * inch))
    
    # Section 5
    story.append(Paragraph("5. Prompt Engineering", heading_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "Effective prompt engineering is crucial for getting good results from LLMs. "
        "Key techniques include: providing clear instructions, using few-shot examples, "
        "implementing chain-of-thought reasoning, specifying output format, and including "
        "relevant context. System prompts define the LLM's behavior and constraints, while "
        "user prompts contain the actual task or question. Experimenting with different "
        "prompt formulations can significantly improve output quality.",
        body_style
    ))
    story.append(Spacer(1, 0.3 * inch))
    
    story.append(PageBreak())
    
    # Section 6
    story.append(Paragraph("6. Production Deployment", heading_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "Deploying AI applications to production requires careful consideration of "
        "scalability, monitoring, cost optimization, and security. Common deployment "
        "platforms include Google Cloud Run, AWS Lambda, Azure Container Apps, and "
        "Kubernetes. Key production concerns include: API rate limiting, error handling, "
        "logging and monitoring, caching strategies, and cost management. Using managed "
        "services can reduce operational overhead while maintaining reliability.",
        body_style
    ))
    story.append(Spacer(1, 0.3 * inch))
    
    # Conclusion
    story.append(Paragraph("Conclusion", heading_style))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "Building production-ready AI applications requires a solid understanding of LLMs, "
        "RAG architectures, vector databases, and deployment best practices. By combining "
        "these technologies effectively, developers can create powerful, accurate, and "
        "scalable AI systems that provide real business value. Continuous learning and "
        "experimentation are essential as the field of AI engineering rapidly evolves.",
        body_style
    ))
    
    # Build PDF
    doc.build(story)
    
    print(f"✓ Sample PDF created: {pdf_path}")
    print(f"  Use this file to test the PDF Q&A System")
    return pdf_path


if __name__ == "__main__":
    # Note: This requires reportlab to be installed
    # pip install reportlab
    
    try:
        create_sample_pdf()
    except ImportError:
        print("Error: reportlab not installed")
        print("Install with: pip install reportlab")
