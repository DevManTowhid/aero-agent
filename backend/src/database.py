from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.config import settings

# 1. create_async_engine: This sets up the 'Engine'. 
# Think of the Engine as the actual pipe connected to PostgreSQL.
engine = create_async_engine(
    settings.database_url, # Gets the URL from our config file
    echo=True,             # This logs every SQL query to your terminal (great for debugging)
    future=True            # Ensures we are using SQLAlchemy 2.0 standards
)

# 2. async_sessionmaker: This is a factory that creates 'Sessions'.
# A Session is a single 'transaction' or conversation with the database.
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False # Prevents SQLAlchemy from breaking objects after you save them
)

# 3. get_db: This is a FastAPI 'Dependency'.
# When a user hits an API endpoint, FastAPI will call this function.
async def get_db():
    # 4. 'async with' ensures the session is automatically CLOSED 
    # even if the code crashes, preventing memory leaks.
    async with AsyncSessionLocal() as session:
        yield session # This hands the database connection to your API route