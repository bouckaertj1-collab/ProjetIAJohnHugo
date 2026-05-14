import ast
from sqlalchemy import String, Float, create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column, sessionmaker
from pathlib import Path

_DB_PATH = Path(__file__).parent / "q_tables.db"

engine = create_engine(f"sqlite:///{_DB_PATH}")
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy database models.

    Every table class inherits from this class so SQLAlchemy can register it
    in Base.metadata and create the database schema with create_all().
    """
    pass

class Agent(Base):
    """
    Represents one trained Q-learning agent linked to one circuit.

    Each Agent row identifies a saved Q-table in the database. In this project,
    the Q-learning agent is trained separately for each circuit, so the circuit
    name is used to retrieve the correct Q-table before playing or continuing
    training.

    The related QValue rows store the actual Q-table values:
        - one state;
        - one action;
        - one learned Q-value.

    This class does not contain the learning logic itself. It only represents
    the database identity of a trained agent.
    """
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
    """
    Represents one value of the Q-table.

    The primary key is composed of:
        - agent_id: the trained agent/circuit;
        - state: the serialized Q-learning state;
        - action: the action evaluated in that state.

    The value column stores Q(state, action), meaning the learned expected
    long-term reward for choosing this action in this state.
    """
    __tablename__ = "q_values"
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), primary_key=True)
    state: Mapped[str] = mapped_column(String, primary_key=True)
    action: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[float] = mapped_column(Float)
    agent = relationship("Agent", back_populates="q_values")

def serialize_state(state) -> str:
    """
    Convert a Q-learning state tuple into a stable database string.

    States are tuples containing integers such as position, obstacle distances,
    terrain codes, direction and speed. SQLite cannot directly use Python tuples
    as primary-key values, so the tuple is converted to a compact string.
    """
    return repr(state).replace(" ", "")

def deserialize_state(state_str: str) -> tuple:
    """
    Convert a serialized database state back into a Python tuple.

    ast.literal_eval is used instead of eval so only Python literals are parsed.
    This rebuilds the exact state format expected by QLearningKart.
    """
    return ast.literal_eval(state_str)

def set_q_value(session, agent_id, state, action, value):
    """
    Insert or update one Q-table value in the database.

    SQLAlchemy merge() is used because the same state/action pair is saved many
    times during training. If the row already exists, it is updated. Otherwise,
    it is inserted.
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