import os
from contextlib import contextmanager
from langgraph.checkpoint.postgres import PostgresSaver


@contextmanager
def get_checkpointer():
    db_url = os.getenv("CHECKPOINTER_DB_URL")

    if not db_url:
        raise ValueError("CHECKPOINTER_DB_URL not set")

    with PostgresSaver.from_conn_string(db_url) as saver:
        yield saver

