"""
Define the SQLAlchemy persistence layer for PixelKart Q-learning data.

This module configures the SQLite database used to store trained Q-learning
agents and their Q-values. It defines the ORM models and class, the database session
factory, and small helper functions used to serialize states and insert or
update Q-values.

Database structure:
- Agent represents one trained Q-learning agent linked to one circuit.
- QValue represents one learned value for one state-action pair.
"""

import ast
from pathlib import Path

from sqlalchemy import String, Float, create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column, sessionmaker


_DB_PATH = Path(__file__).parent / "q_tables.db"

engine = create_engine(f"sqlite:///{_DB_PATH}")
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Base class used by SQLAlchemy models."""
    pass


class Agent(Base):
    """Database row representing one trained agent for one circuit."""

    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True)
    circuit_name: Mapped[str] = mapped_column(String, unique=True)
    alpha: Mapped[float]
    gamma: Mapped[float]
    epsilon: Mapped[float]

    q_values = relationship(
        "QValue",
        back_populates="agent",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class QValue(Base):
    """Database row representing one Q-value for one state-action pair."""

    __tablename__ = "q_values"

    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), primary_key=True)
    state: Mapped[str] = mapped_column(String, primary_key=True)
    action: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[float] = mapped_column(Float)

    agent = relationship("Agent", back_populates="q_values")


def serialize_state(state) -> str:
    """
    Convert a Q-learning state to a database string.

    Args:
        state: Q-learning state tuple.

    Returns:
        Serialized state string.
    """
    return repr(state).replace(" ", "")


def deserialize_state(state_str: str) -> tuple:
    """
    Convert a database state string back to a tuple.

    Args:
        state_str: Serialized state string.

    Returns:
        Q-learning state tuple.
    """
    return ast.literal_eval(state_str)


def set_q_value(session, agent_id, state, action, value):
    """
    Insert or update one Q-value.

    Args:
        session: Active SQLAlchemy session.
        agent_id: Database identifier of the agent.
        state: Serialized Q-learning state.
        action: Action linked to the Q-value.
        value: Q-value to save.
    """
    q = QValue(
        agent_id=agent_id,
        state=state,
        action=action,
        value=value,
    )
    session.merge(q)


def init_db():
    """Create the Q-table database tables if they do not exist."""
    Base.metadata.create_all(engine)