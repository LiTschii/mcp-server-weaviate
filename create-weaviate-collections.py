import weaviate
import weaviate.classes as wvc
from weaviate.auth import Auth
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def create_collections(
    weaviate_api_key: Optional[str],
    search_collection_name: str,
    store_collection_name: str,
    weaviate_url: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    cohere_api_key: Optional[str] = None,
    port: Optional[int] = 8080,
    grpc_port: Optional[int] = 50051
):
    """
    Create the collections needed for the Weaviate functionality.
    """
    # Set up headers for vectorization
    headers = {}
    if openai_api_key:
        headers["X-OpenAI-Api-Key"] = openai_api_key
    if cohere_api_key:
        headers["X-Cohere-Api-Key"] = cohere_api_key

    # Connect to Weaviate
    client = weaviate.connect_to_local(
        port=8080,
        grpc_port=50051,
        auth_credentials=wvc.init.Auth.api_key(os.getenv('PASSWORD'))
    )


    # Delete existing collections if they exist
    for collection_name in [search_collection_name, store_collection_name]:
        if client.collections.exists(collection_name):
            client.collections.delete(collection_name)

    # Create search collection for knowledge base
    search_collection = client.collections.create(
        name=search_collection_name,
        vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai() if openai_api_key else wvc.config.Configure.Vectorizer.text2vec_cohere(),
        properties=[
            wvc.config.Property(
                name="content",
                data_type=wvc.config.DataType.TEXT,
                description="The content of the knowledge base entry"
            )
        ]
    )

    # Create store collection for memories
    store_collection = client.collections.create(
        name=store_collection_name,
        vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai() if openai_api_key else wvc.config.Configure.Vectorizer.text2vec_cohere(),
        properties=[
            wvc.config.Property(
                name="content",
                data_type=wvc.config.DataType.TEXT,
                description="The content of the stored memory"
            )
        ]
    )

    client.close()

if __name__ == "__main__":
    # Get configuration from environment variables
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
    search_collection_name = os.getenv("SEARCH_COLLECTION_NAME")
    store_collection_name = os.getenv("STORE_COLLECTION_NAME")
    weaviate_url = os.getenv("WEAVIATE_URL")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    cohere_api_key = os.getenv("COHERE_API_KEY")
    port = os.getenv('WEAVIATE_PORT')
    grpc_port = os.getenv('WEAVIATE_GRPC_PORT')

    if not search_collection_name or not store_collection_name:
        raise ValueError("Collection names must be provided")
    
    if not (openai_api_key or cohere_api_key):
        raise ValueError("Either OpenAI or Cohere API key must be provided")

    create_collections(
        weaviate_api_key,
        search_collection_name,
        store_collection_name,
        weaviate_url,
        openai_api_key,
        cohere_api_key,
        port,
        grpc_port
    )
