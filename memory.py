import os
import requests
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

class AzureOpenAIEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """
    Custom embedding function to use Azure OpenAI embeddings if configuration is set.
    """
    def __init__(self, api_key: str, endpoint: str, deployment: str):
        self.api_key = api_key
        self.endpoint = endpoint
        self.deployment = deployment

    def __call__(self, texts):
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/embeddings?api-version=2023-05-15"
        data = {"input": texts}
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        embeddings = response.json()["data"]
        return [d["embedding"] for d in embeddings]

def get_embedding_function():
    """
    Returns the appropriate embedding function based on Azure environment variables or local fallback.
    """
    azure_deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    azure_api_key = os.environ.get("AZURE_OPENAI_API_KEY")

    if azure_deployment and azure_endpoint and azure_api_key:
        return AzureOpenAIEmbeddingFunction(
            api_key=azure_api_key,
            endpoint=azure_endpoint,
            deployment=azure_deployment
        )
    else:
        return embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

def get_chroma_client():
    """
    Returns a ChromaDB client with persistence to store/restore embeddings.
    """
    return chromadb.Client(
        Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="chroma_db"
        )
    )

def add_text_to_memory(text: str, doc_id: str, collection_name: str):
    """
    Adds a text document to the specified collection in ChromaDB with the provided doc_id.
    """
    client = get_chroma_client()
    embedding_fn = get_embedding_function()
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn
    )
    collection.add(
        documents=[text],
        metadatas=[{}],
        ids=[doc_id]
    )

def retrieve_relevant_context(query: str, n_results: int):
    """
    Queries all existing collections for the most relevant documents to the provided query,
    then returns a formatted string of the top results across collections.
    """
    client = get_chroma_client()
    embedding_fn = get_embedding_function()
    all_collections = client.list_collections()
    all_results = []

    for c_meta in all_collections:
        c = client.get_collection(c_meta.name, embedding_function=embedding_fn)
        query_result = c.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "distances"]
        )
        if query_result.get("documents") and query_result.get("distances"):
            docs = query_result["documents"][0]
            dists = query_result["distances"][0]
            for doc, dist in zip(docs, dists):
                all_results.append((doc, dist))

    # Sort results by ascending distance and pick the global top n
    all_results.sort(key=lambda x: x[1])
    top_results = all_results[:n_results]

    # Format the output as a single string with each document on a new line
    return "\n".join([doc for doc, _ in top_results])