from games.PixelKart.dao.q_table_dao import *

def load_q_table(agent,agent_id, session):
    results = session.query(QValue).filter_by(agent_id=agent_id).all()

    for q in results:

        state = deserialize_state(q.state)
        agent.q_table[(state, q.action)] = q.value

def save_q_table(agent, agent_id, session):
    for (state, action), value in agent.q_table.items():
        set_q_value(session, agent_id, state, action, value)

    session.commit()


def deserialize_state(state_str):
    parts = state_str.split(",")
    return (
        int(parts[0]),
        int(parts[1]),
        int(parts[2]),
        int(parts[3]),
        parts[4]
    )

def create_agent(session):
    agent = session.query(Agent).first()

    if agent is None:
        agent = Agent(alpha=0.1, gamma=0.9, epsilon=1.0)
        session.add(agent)
        session.commit()

    return agent