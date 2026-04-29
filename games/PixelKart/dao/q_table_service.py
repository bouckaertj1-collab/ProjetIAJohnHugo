from games.PixelKart.dao.q_table_dao import *

def load_q_table(q_learning_agent,agent_id_db, session):
    results = session.query(QValue).filter_by(agent_id=agent_id_db).all()

    for q in results:

        state = deserialize_state(q.state)
        q_learning_agent.q_table[(state, q.action)] = q.value

def save_q_table(q_learning_agent, agent_id_db, session):
    for (state, action), value in q_learning_agent.q_table.items():
        set_q_value(session, agent_id_db, state, action, value)

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