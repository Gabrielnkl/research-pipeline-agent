from langgraph.checkpoint.postgres import PostgresSaver
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("CHECKPOINT_DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("CHECKPOINT_DATABASE_URL is not set")

checkpointer = PostgresSaver.from_conn_string(DATABASE_URL)