from fastapi import FastAPI

app = FastAPI(
    title="Aviation Multi-Agent RAG System",
    description="Backend orchestrator for engineering schematic retrieval",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    """
    Basic health pulse to ensure the orchestrator is alive.
    """
    return {"status": "operational", "systems": "nominal"}