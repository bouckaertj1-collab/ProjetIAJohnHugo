"""
Script pour entraîner un kart QLearning sur 10 courses.
- Utilise le circuit depuis circuits.txt ou un circuit par défaut.
- Conserve le même kart entre les courses pour que ε diminue.
- Affiche les métriques d'apprentissage.
"""

from pathlib import Path
from games.PixelKart.dao.Q_table_dao import init_db, SessionLocal
from games.PixelKart.dao.q_table_service import save_q_table, load_q_table,create_agent
from games.PixelKart.model.circuit import Circuit
from games.PixelKart.model.kart_factory import KartFactory
from games.PixelKart.model.race import Race
#import matplotlib.pyplot as plt


def run_automated_races(num_races=10, total_laps=3):
    init_db()

    circuits_file = Path(__file__).parent / "circuits.txt"
    circuit_dto = None

    if circuits_file.exists():
        with open(circuits_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and ':' in line:
                    name, grid_str = line.split(':', 1)
                    circuit_dto = {"name": name, "grid": grid_str}
                    break
    
    circuit = Circuit.from_dto(circuit_dto)

    print(f"[INFO] Circuit utilisé: {circuit.name}\n")

    session = SessionLocal()
    db_agent = create_agent(session)
    agent_id = db_agent.id
    session.commit()
    session.close()

    kart = KartFactory.create(
        kart_type="ql",
        config={"name": "QL Kart", "color": "red", "position": (0, 0)}
    )

    session = SessionLocal()
    load_q_table(kart, agent_id, session)
    session.close()

    kart.alpha = 0.3
    kart.gamma = 0.99
    kart.epsilon = 0.9
    reward_list = []

    for race_num in range(1, num_races + 1):

        start_positions = [(1, 3)]
        kart.position = start_positions[0]

        kart.speed = 0
        kart.laps_done = 0
        kart.is_alive = True
        kart.has_finished = False
        kart.direction = "EAST"
        kart.previous_action = None

        race = Race(circuit=circuit, karts=[kart], total_laps=total_laps)
        total_reward = 0.0
        
        max_steps = 30_000
        
        steps = 0
        while not race.finished and kart.is_alive and steps < max_steps:
            current_kart = race.get_current_kart()

            state = current_kart.get_state(race.circuit)
            action = current_kart.choose_action(state,race.circuit)
            old_position = current_kart.position
            race.step(action)

            crash = not current_kart.is_alive

            finished = current_kart.has_finished
            
            reward = current_kart.compute_reward(crash, finished, old_position, current_kart.position, circuit,action)

            total_reward += reward

            next_state = None if crash or finished else current_kart.get_state(race.circuit)
            current_kart.learn(state, action, reward, next_state)

            steps += 1

        reward_list += [total_reward]

        kart.next_epsilon(coef=0.97, min_epsilon=0.1)

        print("===========================")
        print(f"| Course: {race_num}/{num_races}|")
        print(f"| ε= {kart.epsilon:.2f}|")
        print(f"| Récompense: {total_reward:.1f}|")
        print(f"| États: {len(kart.q_table)}|")
        print(f"| Finished: {kart.has_finished}|")
        print(f"| Laps: {kart.laps_done}/{total_laps}|")
        print(f"| Position: {kart.position}|")
        print(f"| crash: {crash}|")
        print(f"| Time: {race.time}|")
        print("===========================")

    print("\n[SAUVEGARDE FINALE]...")
    session = SessionLocal()
    save_q_table(kart, session, agent_id)
    session.commit()
    session.close()
    print("[SAUVEGARDE FINALE] Terminée !")

    session = SessionLocal()
    try:
        save_q_table(kart, session, agent_id)
        session.commit()
    finally:
        session.close()

    

def reward_evolution(rewards,nb_courses):
    plt.plot(range(len(rewards)), rewards)
    plt.xlabel("Episode")
    plt.ylabel("Récompense totale")
    plt.title(f"Évolution des récompenses sur {nb_courses} courses")
    plt.show()


if __name__ == "__main__":
    run_automated_races(num_races=50, total_laps=3)