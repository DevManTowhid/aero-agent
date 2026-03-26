# backend/src/services/retriever.py
from qdrant_client import QdrantClient
from fastembed import TextEmbedding

class VectorRetriever:
    """
    Handles converting user questions into mathematical embeddings
    and performing high-speed similarity searches against the Qdrant database.
    """
    def __init__(self, collection_name: str = "engineering_manuals"):
        self.collection_name = collection_name
        self.client = QdrantClient(url="http://localhost:6333")
        
        # Load the exact same local AI model we used for ingestion
        self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def search(self, query: str, limit: int = 3) -> list[dict]:
        """
        Takes a human question, embeds it, and returns the most relevant technical chunks.
        """
        print(f"Embedding query: '{query}'...")
        
        # 1. Convert the plain English question into a 384-dimensional vector
        query_generator = self.embedding_model.embed([query])
        query_vector = list(query_generator)[0].tolist()

        # 2. Perform the Cosine Similarity search (Updated for Qdrant v1.17+)
        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        )

        # 3. Format the raw database results into a clean Python list
        # We safely extract the points whether Qdrant returns a list or a response object
        points = getattr(search_results, 'points', search_results)
        
        formatted_results = []
        for result in points:
            formatted_results.append({
                "score": result.score, 
                "text": result.payload["text"],
                "page_number": result.payload["page_number"],
                "source": result.payload["source"]
            })
            
        return formatted_results

# --- Quick Test Block ---
if __name__ == "__main__":
    retriever = VectorRetriever()
    
    # Let's ask a hyper-specific question about the PDF you just uploaded
    test_query = "What is the course code and title for this lab report?"
    
    try:
        results = retriever.search(query=test_query, limit=2)
        
        print("\n--- SEARCH RESULTS ---")
        for i, res in enumerate(results):
            print(f"\nResult {i+1} (Confidence Score: {res['score']:.4f})")
            print(f"Source: {res['source']} - Page {res['page_number']}")
            print(f"Text: {res['text']}")
            
    except Exception as e:
        print(f"Retrieval Error: {e}")