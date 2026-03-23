# backend/src/models.py
from datetime import datetime, timezone
from sqlalchemy import String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List, Optional

# 1. The Centralized Registry (The 'Base')
class Base(DeclarativeBase):
    """
    Acts as the master template for all models. 
    Inheriting from DeclarativeBase ensures all tables are registered 
    to a single MetaData object for foreign key consistency.
    """
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    
    # Relationship: One user can have multiple diagnostic sessions
    sessions: Mapped[List["ChatSession"]] = relationship(back_populates="user") 

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255), default="Aviation Diagnostic Session")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship(back_populates="sessions")
    messages: Mapped[List["ChatMessage"]] = relationship(
        back_populates="session", # Links back to ChatSession
        cascade="all, delete-orphan" # Ensures messages are deleted if the session is deleted, avoiding orphaned records
    )

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"))
    
    # 'role' can be: user, assistant, or system
    role: Mapped[str] = mapped_column(String(50)) 
    content: Mapped[str] = mapped_column(Text)
    
    # agent_metadata: Critical for Multi-Agent RAG.
    # Stores which agent (Safety, Retrieval, etc.) generated the response.
    agent_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )

    session: Mapped["ChatSession"] = relationship(back_populates="messages") # Links back to ChatSession

#