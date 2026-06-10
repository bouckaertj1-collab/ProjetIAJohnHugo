from __future__ import annotations

from sqlalchemy.orm import Session

from games.pixelKart.dao.Q_table_dao import (
    Agent,
    QValue,
    SessionLocal,
    deserialize_state,
    init_db,
    serialize_state,
    set_q_value,
)


def load_q_table(agent_id: int, session: Session) -> dict:
    """
    Load a Q-table from the database.

    Args:
        agent_id: Database identifier of the trained agent.
        session: Active SQLAlchemy session.

    Returns:
        Q-table loaded from saved state-action values.
    """
    q_table = {}
    results = session.query(QValue).filter_by(agent_id=agent_id).all()

    for q_value in results:
        state = deserialize_state(q_value.state)

        if state not in q_table:
            q_table[state] = {}

        q_table[state][q_value.action] = q_value.value

    return q_table


def load_q_table_for_circuit(circuit_name: str) -> dict:
    """
    Load the trained Q-table linked to a circuit.

    Args:
        circuit_name: Circuit name linked to the trained agent.

    Returns:
        Q-table saved for the circuit.

    Raises:
        ValueError: If no trained agent exists for the circuit.
    """
    init_db()

    with SessionLocal() as session:
        agent = get_agent(session=session, circuit_name=circuit_name)

        if agent is None:
            raise ValueError(f"No trained Q-table found for circuit: {circuit_name}")

        return load_q_table(agent_id=agent.id, session=session)


def save_q_table(agent, session: Session, agent_id: int) -> None:
    """
    Save a Q-learning agent Q-table.

    Args:
        agent: QLearningKart containing the Q-table.
        session: Active SQLAlchemy session.
        agent_id: Database identifier of the trained agent.
    """
    for state, actions in agent.q_table.items():
        state_str = serialize_state(state)

        for action, value in actions.items():
            set_q_value(
                session=session,
                agent_id=agent_id,
                state=state_str,
                action=action,
                value=value,
            )

    session.commit()


def get_agent(session: Session, circuit_name: str) -> Agent | None:
    """
    Retrieve the trained agent linked to a circuit.

    Args:
        session: Active SQLAlchemy session.
        circuit_name: Circuit name.

    Returns:
        Trained agent linked to the circuit, or None if it does not exist.
    """
    return session.query(Agent).filter_by(circuit_name=circuit_name).first()


def get_or_create_agent_for_circuit(
    session: Session,
    circuit_name: str,
    alpha: float = 0.2,
    gamma: float = 0.95,
    epsilon: float = 0.95,
) -> Agent:
    """
    Return the saved Q-learning agent linked to a circuit.

    Args:
        session: Active SQLAlchemy session.
        circuit_name: Circuit name linked to the agent.
        alpha: Learning rate stored when a new agent is created.
        gamma: Future reward factor stored when a new agent is created.
        epsilon: Exploration rate stored when a new agent is created.

    Returns:
        Existing agent for the circuit, or a newly created one.
    """
    agent = get_agent(session=session, circuit_name=circuit_name)

    if agent is not None:
        return agent

    agent = Agent(
        circuit_name=circuit_name,
        alpha=alpha,
        gamma=gamma,
        epsilon=epsilon,
    )

    session.add(agent)
    session.commit()
    session.refresh(agent)

    return agent