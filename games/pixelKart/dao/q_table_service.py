from __future__ import annotations

from sqlalchemy.orm import Session

from games.pixelKart.dao.Q_table_dao import (
    Agent,
    QValue,
    deserialize_state,
    serialize_state,
    set_q_value,
)


def load_q_table(agent, agent_id: int, session: Session) -> dict:
    """
    Load a Q-table from the database into a Q-learning kart.

    Args:
        agent: QLearningKart instance receiving the Q-table.
        agent_id: Database identifier of the trained agent.
        session: Active SQLAlchemy session.

    Returns:
        The loaded Q-table dictionary.
    """
    results = session.query(QValue).filter_by(agent_id=agent_id).all()

    for q_value in results:
        state = deserialize_state(q_value.state)

        if state not in agent.q_table:
            agent.q_table[state] = {}

        agent.q_table[state][q_value.action] = q_value.value

    return agent.q_table


def save_q_table(agent, session: Session, agent_id: int) -> None:
    """
    Save a Q-learning kart Q-table into the database.

    Existing state/action pairs are updated. New state/action pairs are inserted.

    Args:
        agent: QLearningKart instance containing the Q-table to save.
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
    Retrieve the trained agent linked to one circuit.

    Args:
        session: Active SQLAlchemy session.
        circuit_name: Name of the circuit linked to the Q-table.

    Returns:
        The matching Agent if it exists, otherwise None.
    """
    return session.query(Agent).filter_by(circuit_name=circuit_name).first()


def create_agent(
    session: Session,
    circuit_name: str,
    alpha: float = 0.2,
    gamma: float = 0.95,
    epsilon: float = 1.0,
) -> Agent:
    """
    Retrieve or create a Q-learning agent for one circuit.

    Each circuit gets one Agent entry and therefore one Q-table through
    the q_values table.

    Args:
        session: Active SQLAlchemy session.
        circuit_name: Name of the circuit to train or load.
        alpha: Learning rate stored as metadata.
        gamma: Discount factor stored as metadata.
        epsilon: Exploration rate stored as metadata.

    Returns:
        The existing or newly created Agent.

    Raises:
        ValueError: If circuit_name is empty.
    """
    if not circuit_name.strip():
        raise ValueError("Circuit name cannot be empty.")

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