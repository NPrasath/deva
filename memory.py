import chromadb
from chromadb.config import Settings

CODE_COLLECTION_NAME = "code_collection"
REQUIREMENTS_COLLECTION_NAME = "requirements_collection"

CHROMA_DB_DIRECTORY = "./chroma_db_store"

def get_chroma_client():
    """
    Initializes and returns a persistent ChromaDB client.
    """
    return chromadb.Client(
        Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=CHROMA_DB_DIRECTORY
        )
    )