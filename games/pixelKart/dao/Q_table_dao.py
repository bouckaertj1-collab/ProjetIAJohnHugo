import ast
from sqlalchemy import String, Float, create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column, sessionmaker
from pathlib import Path

_DB_PATH = Path(__file__).parent / "q_tables.db"

engine = create_engine(f"sqlite:///{_DB_PATH}")
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class Agent(Base):
    """Represents one trained Q-learning agent for one circuit."""

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
    __tablename__ = "q_values"
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), primary_key=True)
    state: Mapped[str] = mapped_column(String, primary_key=True)
    action: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[float] = mapped_column(Float)
    agent = relationship("Agent", back_populates="q_values")

def serialize_state(state) -> str:
    """Convert a state tuple into a stable string representation."""
    return repr(state).replace(" ", "")


def deserialize_state(state_str: str) -> tuple:
    """Rebuild a state tuple from its string representation."""
    return ast.literal_eval(state_str)


def set_q_value(session, agent_id, state, action, value):
    """
    Update or create one Q-table entry.

    merge() is used to avoid primary-key conflicts.
    """
    q = QValue(
        agent_id=agent_id,
        state=state,
        action=action,
        value=value,
    )
    session.merge(q)
        

def get_q_values(session, agent_id, state):
    state_str = serialize_state(state)
    results = session.query(QValue).filter_by(agent_id=agent_id, state=state_str).all()
    return {q.action: q.value for q in results}

def init_db():
    Base.metadata.create_all(engine)