# backend/src/services/ingestion.py
import fitz  # PyMuPDF: Chosen over PyPDF2 because its C++ backend is much faster and handles complex engineering layouts (like two-column text) accurately.
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor:
    """
    Handles the ingestion, cleaning, and chunking of complex technical PDFs.
    Prepares documents for vector embedding and Multi-Agent retrieval.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        # We use a Recursive split. Instead of blindly chopping text every 1000 characters,
        # it tries to split at paragraphs first (\n\n), then lines (\n), then sentences (. ), 
        # to keep the semantic meaning and technical context intact.
        # The 200-character overlap ensures context isn't lost if a concept spans across a chunk boundary.
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def extract_text_from_pdf(self, file_path: str) -> list[dict]:
        """
        Reads a PDF and extracts text page by page, preserving the page number 
        as critical metadata so the AI can cite its sources later.
        """
        doc = fitz.open(file_path) # Loads the PDF into RAM
        extracted_pages = []

        # Iterate page by page to lock in the page number metadata
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            
            # PDFs often contain hidden/broken line breaks. 
            # This normalizes the text into a clean, continuous string.
            clean_text = " ".join(text.split())
            
            if clean_text:
                extracted_pages.append({
                    "page_number": page_num + 1,
                    "content": clean_text
                })
                
        return extracted_pages

    def chunk_document(self, extracted_pages: list[dict]) -> list[dict]:
        """
        Takes the extracted pages and breaks them into LLM-digestible chunks,
        carrying the specific page number metadata into every individual chunk.
        """
        final_chunks = []
        
        for page in extracted_pages:
            # Pass the clean text of a single page into the LangChain algorithm
            chunks = self.text_splitter.split_text(page["content"])
            
            # This is the most important part of RAG data preparation. 
            # We attach the metadata to the chunk so the database can filter it later.
            for chunk in chunks:
                final_chunks.append({
                    "text": chunk,
                    "metadata": {
                        "page_number": page["page_number"]
                    }
                })
                
        return final_chunks

# --- Quick Test Block ---
# This block only runs if you execute this file directly from the terminal.
# It will NOT run when we import this class into our FastAPI routes later.
if __name__ == "__main__":
    processor = DocumentProcessor()
    
    try:
        print("Extracting text...")
        pages = processor.extract_text_from_pdf("test.pdf")
        
        print(f"Chunking {len(pages)} pages...")
        chunks = processor.chunk_document(pages)
        
        print(f"\nSuccessfully created {len(chunks)} chunks!")
        print(f"Sample Chunk 1: {chunks[0]}")
    except Exception as e:
        print(f"Error: Make sure you have a 'test.pdf' file in the directory. {e}")