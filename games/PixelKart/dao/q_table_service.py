from games.PixelKart.dao.Q_table_dao import *

def load_q_table(agent, agent_id, session):
    """
    Charge la Q-table depuis la base de données.
    Args:
        agent: Un objet QLearningKart (ou un dict avec .q_table)
        agent_id: ID de l'agent dans la DB
        session: Session SQLAlchemy
    """
    results = session.query(QValue).filter_by(agent_id=agent_id).all()
    for q in results:
        state = deserialize_state(q.state)
        if state not in agent.q_table:
            agent.q_table[state] = {}
        agent.q_table[state][q.action] = q.value

    return agent.q_table

def save_q_table(agent, session, agent_id):
    for state, actions in agent.q_table.items():
        state_str = serialize_state(state)
        for action, value in actions.items():
            set_q_value(session, agent_id, state_str, action, value)
    session.commit()

def create_agent(session):
    agent = session.query(Agent).first()

    if agent is None:
        agent = Agent(alpha=0.1, gamma=0.9, epsilon=1.0)
        session.add(agent)
        session.commit()

    return agent