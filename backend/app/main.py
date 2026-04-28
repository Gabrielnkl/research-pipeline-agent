import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.api.routers import research_router
from app.db.postgres import engine, init_db
from app.graph.pipeline import build_graph  # ✅ we'll build the graph here, not at import time

load_dotenv(override=True)

CHECKPOINT_DATABASE_URL = os.getenv("CHECKPOINT_DATABASE_URL")
if not CHECKPOINT_DATABASE_URL:
    raise ValueError("CHECKPOINT_DATABASE_URL is not set")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ Setup app DB tables
    await init_db()
    print("✅ Database tables ready")

    # ✅ Open the async checkpointer for the entire app lifetime
    async with AsyncPostgresSaver.from_conn_string(CHECKPOINT_DATABASE_URL) as checkpointer:
        await checkpointer.setup()  # creates langgraph tables if they don't exist
        print("✅ Checkpointer tables ready")

        # ✅ Build the graph now that we have a live checkpointer
        app.state.graph = build_graph(checkpointer)
        print("✅ Graph compiled")

        yield  # app runs here

    # checkpointer connection is closed automatically when the async with block exits
    await engine.dispose()
    print("🛑 Database connection closed")


app = FastAPI(
    title="Research API",
    description="API for managing research jobs",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(
    research_router,
    prefix="/api/research",
    tags=["research"]
)

origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Research API. Use /docs for API documentation."}

@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)