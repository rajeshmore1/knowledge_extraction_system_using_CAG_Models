from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

print("Loaded cache_manager.py (Version: No persist)")  # Debug print

def setup_cache(persist_dir: str = "cache_db") -> Chroma:
    """
    Set up a vector store for caching query-response pairs.
    
    Args:
        persist_dir (str): Directory to persist cache
    
    Returns:
        Chroma: Configured cache vector store
    """
    try:
        print("Creating Chroma vector store for cache")  # Debug print
        cache_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L12-v2")
        return Chroma(embedding_function=cache_embeddings, persist_directory=persist_dir)
    except Exception as e:
        print(f"Error setting up cache: {e}")
        return None

def get_cached_response(query: str, cache_db: Chroma, top_k: int = 5, distance_threshold: float = 0.5) -> tuple:
    """
    Retrieve a cached response if available.
    
    Args:
        query (str): User query
        cache_db (Chroma): Cache vector store
        top_k (int): Number of top results to retrieve
        distance_threshold (float): Similarity threshold for cache hit
    
    Returns:
        tuple: (cached_response, best_doc) or (None, None)
    """
    try:
        docs_and_scores = cache_db.similarity_search_with_score(query, k=top_k)
        if docs_and_scores:
            docs_and_scores.sort(key=lambda x: x[1])
            best_doc, best_score = docs_and_scores[0]
            if best_score < distance_threshold:
                return best_doc.metadata.get("response"), best_doc
        return None, None
    except Exception as e:
        print(f"Error retrieving cached response: {e}")
        return None, None

def add_to_cache(query: str, response: str, cache_db: Chroma) -> None:
    """
    Add a query-response pair to the cache.
    
    Args:
        query (str): User query
        response (str): Generated response
        cache_db (Chroma): Cache vector store
    """
    try:
        cache_db.add_texts([query], metadatas=[{"response": response}])
    except Exception as e:
        print(f"Error adding to cache: {e}")