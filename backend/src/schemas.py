# backend/src/schemas.py
from pydantic import BaseModel

class UserCreate(BaseModel): # This is the schema for creating a new user (registration)
    email: str
    password: str

class UserResponse(BaseModel): # This is the schema for returning user data (e.g., after registration or login)
    id: int
    email: str

    class Config:
        from_attributes = True # Allows Pydantic to read from SQLAlchemy models directly