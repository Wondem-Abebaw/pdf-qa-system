"""
Configuration management using Pydantic Settings.
Loads and validates environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str
    
    # LangChain Configuration (optional)
    langchain_tracing_v2: bool = False
    langchain_api_key: str | None = None
    
    # Text Processing Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Model Configuration
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4-turbo-preview"
    temperature: float = 0.0
    
    # ChromaDB Settings
    chroma_persist_directory: str = "./data/chroma_db"
    collection_name: str = "pdf_documents"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def chroma_path(self) -> Path:
        """Get ChromaDB persistence path as Path object."""
        return Path(self.chroma_persist_directory)


# Global settings instance
settings = Settings()
