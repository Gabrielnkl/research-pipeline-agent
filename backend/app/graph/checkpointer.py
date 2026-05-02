from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("CHECKPOINT_DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("CHECKPOINT_DATABASE_URL is not set")

# ✅ Just create the instance — do NOT call .setup() here
# .setup() is async and must be called once during FastAPI lifespan startup
checkpointer = AsyncPostgresSaver.from_conn_string(DATABASE_URL)