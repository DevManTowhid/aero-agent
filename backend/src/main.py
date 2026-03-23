# backend/src/main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database import get_db
from src.models import User
from src.schemas import UserCreate, UserResponse

app = FastAPI(
    title="Aviation Multi-Agent RAG System",
    description="Backend orchestrator for engineering schematic retrieval",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    return {"status": "operational", "systems": "nominal"}

@app.post("/users/", response_model=UserResponse)
async def create_test_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Creates a new engineer in the database."""
    # 1. Check for existing user
    query = select(User).where(User.email == user.email)
    result = await db.execute(query)
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Engineer already registered.")

    # 2. Create and save the new user
    new_user = User(
        email=user.email, 
        hashed_password=f"dummy_hash_{user.password}"
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user