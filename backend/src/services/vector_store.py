# backend/src/services/vector_store.py
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from fastembed import TextEmbedding

# Import the parser we built in Step 7
from src.services.ingestion import DocumentProcessor

class QdrantStore:
    """
    Handles the connection to the Qdrant microservice, 
    generates local vector embeddings, and indexes them.
    """
    def __init__(self, collection_name: str = "engineering_manuals"):
        self.collection_name = collection_name
        
        # Connect to the Qdrant Docker container via REST API port
        self.client = QdrantClient(url="http://localhost:6333")
        
        # Initialize the lightweight local embedding model. 
        # BAAI/bge-small-en-v1.5 is the industry standard for open-source local RAG.
        # It converts text into an array of 384 dimensions.
        self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        
        # Ensure the table/collection exists in the database
        self._setup_collection()

    def _setup_collection(self):
        """Creates the collection in Qdrant if it doesn't already exist."""
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384, # Must match the output dimensions of our BAAI model
                    distance=Distance.COSINE # Calculates similarity based on vector angles
                )
            )
            print(f"Collection '{self.collection_name}' created successfully.")

    def ingest_pdf(self, file_path: str):
        """
        The Master Pipeline: Parses a PDF, chunks it, embeds it, and saves it.
        """
        print(f"Processing '{file_path}'...")
        processor = DocumentProcessor()
        
        # 1. Extract and Chunk
        pages = processor.extract_text_from_pdf(file_path)
        chunks = processor.chunk_document(pages)
        print(f"Generated {len(chunks)} chunks. Embedding now...")

        # 2. Extract just the text strings for the embedding model
        texts = [chunk["text"] for chunk in chunks]
        
        # 3. Generate the mathematical vectors (this runs locally on your CPU)
        embeddings_generator = self.embedding_model.embed(texts)
        embeddings_list = list(embeddings_generator)

        # 4. Prepare the data points for Qdrant
        points = []
        for i, chunk in enumerate(chunks):
            point = PointStruct(
                id=str(uuid.uuid4()), # Generate a unique ID for each chunk
                vector=embeddings_list[i].tolist(), # The mathematical representation
                payload={
                    "text": chunk["text"], 
                    "page_number": chunk["metadata"]["page_number"],
                    "source": file_path
                } # The metadata we filter by later
            )
            points.append(point)

        # 5. Push to the Vector Database
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"Successfully uploaded {len(points)} vectors to Qdrant!")

# --- Quick Test Block ---
if __name__ == "__main__":
    # We will test this by pushing your test.pdf (like that Lab Report) into the database
    store = QdrantStore()
    
    try:
        store.ingest_pdf("test.pdf")
    except Exception as e:
        print(f"Vector Database Error: {e}")