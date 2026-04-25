import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from app.api.routers import research_router
from app.db.postgres import engine
from app.db.models import Base

# Load environment variables
load_dotenv(override=True)

# Lifespan (startup + shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔥 Startup logic
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables ready")

    yield

    # 🧹 Shutdown logic (optional)
    await engine.dispose()
    print("🛑 Database connection closed")


app = FastAPI(
    title="Research API",
    description="API for managing research jobs",
    version="1.0.0",
    lifespan=lifespan
)

# Routers
app.include_router(
    research_router,
    prefix="/api/research",
    tags=["research"]
)

# CORS
origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root
@app.get("/")
async def root():
    return {"message": "Welcome to the Research API. Use /docs for API documentation."}

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)