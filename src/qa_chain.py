"""
Question-answering chain implementation using LangChain LCEL.
Implements RAG (Retrieval-Augmented Generation) pattern.
"""
from typing import List, Dict, Any, Optional
from operator import itemgetter

from langchain_openai import ChatOpenAI
from langchain.schema import Document
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage

from src.config import settings
from src.vector_store import VectorStoreManager


class QAChain:
    """Question-answering chain with conversation memory."""
    
    # System prompt for the QA chain
    SYSTEM_TEMPLATE = """You are a helpful AI assistant that answers questions based on the provided context from PDF documents.

Instructions:
- Answer the question based ONLY on the information in the context
- If the context doesn't contain enough information to answer, say so clearly
- Be concise but thorough
- If asked about specific documents, mention which document(s) the information came from
- If the context contains conflicting information, acknowledge it
- Cite page numbers when available in the metadata

Context from documents:
{context}

Question: {question}"""

    def __init__(
        self,
        vector_store_manager: VectorStoreManager,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        k_documents: int = 4
    ):
        """
        Initialize QA chain.
        
        Args:
            vector_store_manager: Vector store manager instance
            model_name: LLM model to use (defaults to settings)
            temperature: LLM temperature (defaults to settings)
            k_documents: Number of documents to retrieve
        """
        self.vector_store = vector_store_manager
        self.k_documents = k_documents
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name or settings.llm_model,
            temperature=temperature or settings.temperature,
            openai_api_key=settings.openai_api_key
        )
        
        # Initialize memory for conversation history
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Build the chain
        self.chain = self._build_chain()
    
    def _build_chain(self):
        """Build the RAG chain using LCEL."""
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.SYSTEM_TEMPLATE),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
        # Define the retrieval step
        retriever = self.vector_store.get_retriever(
            search_kwargs={"k": self.k_documents}
        )
        
        # Format documents for context
        def format_docs(docs: List[Document]) -> str:
            formatted = []
            for i, doc in enumerate(docs, 1):
                metadata = doc.metadata
                source = metadata.get("filename", "Unknown")
                page = metadata.get("page", "N/A")
                
                formatted.append(
                    f"[Document {i}: {source}]\n{doc.page_content}\n"
                )
            return "\n".join(formatted)
        
        # Build the LCEL chain
        chain = (
            RunnableParallel(
                context=retriever | format_docs,
                question=RunnablePassthrough(),
                chat_history=lambda x: self.memory.load_memory_variables({})["chat_history"]
            )
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return chain
    
    def ask(
        self,
        question: str,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ask a question and get an answer.
        
        Args:
            question: The question to ask
            metadata_filter: Optional metadata filter for document retrieval
            
        Returns:
            Dictionary with answer and source documents
        """
        try:
            # Update retriever with filter if provided
            if metadata_filter:
                retriever = self.vector_store.get_retriever(
                    search_kwargs={"k": self.k_documents, "filter": metadata_filter}
                )
                
                # Rebuild chain with filtered retriever
                def format_docs(docs: List[Document]) -> str:
                    formatted = []
                    for i, doc in enumerate(docs, 1):
                        metadata = doc.metadata
                        source = metadata.get("filename", "Unknown")
                        formatted.append(
                            f"[Document {i}: {source}]\n{doc.page_content}\n"
                        )
                    return "\n".join(formatted)
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", self.SYSTEM_TEMPLATE),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{question}")
                ])
                
                temp_chain = (
                    RunnableParallel(
                        context=retriever | format_docs,
                        question=RunnablePassthrough(),
                        chat_history=lambda x: self.memory.load_memory_variables({})["chat_history"]
                    )
                    | prompt
                    | self.llm
                    | StrOutputParser()
                )
                
                answer = temp_chain.invoke(question)
                source_docs = retriever.get_relevant_documents(question)
            else:
                # Use default chain
                answer = self.chain.invoke(question)
                
                # Get source documents
                retriever = self.vector_store.get_retriever(
                    search_kwargs={"k": self.k_documents}
                )
                source_docs = retriever.get_relevant_documents(question)
            
            # Update conversation memory
            self.memory.save_context(
                {"question": question},
                {"answer": answer}
            )
            
            return {
                "answer": answer,
                "source_documents": source_docs,
                "question": question
            }
            
        except Exception as e:
            raise Exception(f"Error processing question: {str(e)}")
    
    def ask_with_sources(
        self,
        question: str,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ask a question and get answer with detailed source information.
        
        Args:
            question: The question to ask
            metadata_filter: Optional metadata filter
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        result = self.ask(question, metadata_filter)
        
        # Format source information
        sources = []
        for doc in result["source_documents"]:
            metadata = doc.metadata
            sources.append({
                "filename": metadata.get("filename", "Unknown"),
                "chunk_index": metadata.get("chunk_index", 0),
                "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            })
        
        return {
            "answer": result["answer"],
            "sources": sources,
            "question": question,
            "num_sources": len(sources)
        }
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history.
        
        Returns:
            List of conversation turns
        """
        history = self.memory.load_memory_variables({})["chat_history"]
        
        formatted_history = []
        for msg in history:
            if isinstance(msg, HumanMessage):
                formatted_history.append({
                    "role": "human",
                    "content": msg.content
                })
            elif isinstance(msg, AIMessage):
                formatted_history.append({
                    "role": "assistant",
                    "content": msg.content
                })
        
        return formatted_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.memory.clear()
    
    def update_k_documents(self, k: int):
        """
        Update the number of documents to retrieve.
        
        Args:
            k: New number of documents
        """
        self.k_documents = k
        self.chain = self._build_chain()
