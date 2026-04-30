from sqlalchemy import String,Float,create_engine,ForeignKey
from sqlalchemy.orm import DeclarativeBase,relationship,Mapped,mapped_column,sessionmaker

engine = create_engine("sqlite:///q_tables.db")

SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True)
    alpha: Mapped[float]
    gamma: Mapped[float]
    epsilon: Mapped[float]

    q_values = relationship("QValue", back_populates="agent", cascade="all, delete-orphan",lazy="selectin")

class QValue(Base):
    __tablename__ = "q_values"
    
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id"), primary_key=True)
    state: Mapped[str] = mapped_column(String, primary_key=True)
    action: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[float] = mapped_column(Float)

    agent = relationship("Agent", back_populates="q_values")

def set_q_value(session, agent_id, state, action, value):
    state_str = ",".join(map(str, state))

    q = session.query(QValue).filter_by(
        agent_id=agent_id,
        state=state_str,
        action=action
        ).first()

    if q:
        q.value = value
    else:
        q = QValue(
            agent_id=agent_id,
            state=state_str,
            action=action,
            value=value
        )
        session.add(q)


def get_q_values(session, agent_id, state):
    state_str = ",".join(map(str, state))

    results = session.query(QValue).filter_by(
        agent_id=agent_id,
        state=state_str
    ).all()

    return {q.action: q.value for q in results}


Base.metadata.create_all(engine)