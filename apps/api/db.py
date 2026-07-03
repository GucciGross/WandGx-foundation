from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, MetaData, String, Table, Text, create_engine, insert
from sqlalchemy.engine import Engine

from .settings import settings

metadata = MetaData()

agent_runs = Table(
    "agent_runs",
    metadata,
    __import__("sqlalchemy").Column("id", String, primary_key=True),
    __import__("sqlalchemy").Column("agent_id", String, nullable=False),
    __import__("sqlalchemy").Column("status", String, nullable=False, default="started"),
    __import__("sqlalchemy").Column("payload", JSON, nullable=False, default=dict),
    __import__("sqlalchemy").Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)

feedback = Table(
    "feedback",
    metadata,
    __import__("sqlalchemy").Column("id", Integer, primary_key=True, autoincrement=True),
    __import__("sqlalchemy").Column("run_id", String, nullable=True),
    __import__("sqlalchemy").Column("agent_id", String, nullable=False),
    __import__("sqlalchemy").Column("rating", String, nullable=False),
    __import__("sqlalchemy").Column("comment", Text, nullable=False, default=""),
    __import__("sqlalchemy").Column("snapshot", JSON, nullable=False, default=dict),
    __import__("sqlalchemy").Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)

approvals = Table(
    "approvals",
    metadata,
    __import__("sqlalchemy").Column("id", Integer, primary_key=True, autoincrement=True),
    __import__("sqlalchemy").Column("action", String, nullable=False),
    __import__("sqlalchemy").Column("status", String, nullable=False, default="pending"),
    __import__("sqlalchemy").Column("payload", JSON, nullable=False, default=dict),
    __import__("sqlalchemy").Column("created_at", DateTime, nullable=False, default=datetime.utcnow),
)


def engine() -> Engine:
    if settings.database_url.startswith("sqlite"):
        Path(".local").mkdir(exist_ok=True)
    return create_engine(settings.database_url, pool_pre_ping=True)


def init_db() -> None:
    metadata.create_all(engine())


def store_feedback(record: dict[str, Any]) -> None:
    with engine().begin() as conn:
        conn.execute(insert(feedback).values(**record))
