from games.PixelKart.dao.q_table_dao import *

def load_q_table(agent, agent_id, session):
    results = session.query(QValue).filter_by(agent_id=agent_id).all()

    for q in results:
        state = deserialize_state(q.state)

        if state not in agent.q_table:
            agent.q_table[state] = {}

        agent.q_table[state][q.action] = q.value

def save_q_table(agent, agent_id, session):
    for state, actions in agent.q_table.items():
        for action, value in actions.items():
            set_q_value(session, agent_id, state, action, value) 

    session.commit()

def create_agent(session):
    agent = session.query(Agent).first()

    if agent is None:
        agent = Agent(alpha=0.1, gamma=0.9, epsilon=1.0)
        session.add(agent)
        session.commit()

    return agent