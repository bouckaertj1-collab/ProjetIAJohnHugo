"""
Script pour entraîner un kart QLearning sur 10 courses.
- Utilise le circuit depuis circuits.txt ou un circuit par défaut.
- Conserve le même kart entre les courses pour que ε diminue.
- Affiche les métriques d'apprentissage.
"""

from pathlib import Path
from dao.q_table_dao import init_db, SessionLocal
from dao.q_table_service import save_q_table, load_q_table,create_agent
from model.circuit import Circuit
from model.kart_factory import KartFactory
from model.race import Race
from model.kart import QLearningKart


def create_default_circuit():
    """Crée un circuit 5x5 par défaut au format attendu par Circuit.from_dto()."""
    grid_str = ",".join([
        "road,road,road,road,road",
        "road,wall,wall,wall,road",
        "road,wall,finish,wall,road",
        "road,wall,wall,wall,road",
        "road,road,road,road,road"
    ])
    return {"name": "default_test_circuit", "grid": grid_str}

def run_automated_races(num_races=10, total_laps=3):
    # Initialisation
    init_db()

    # Lire circuits.txt
    circuits_file = Path(__file__).parent / "circuits.txt"
    circuit_dto = None

    """ if circuits_file.exists():
        with open(circuits_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and ':' in line:
                    name, grid_str = line.split(':', 1)
                    circuit_dto = {"name": name, "grid": grid_str}
                    break
    """
    if circuit_dto is None:
        print("[INFO] Aucun circuit valide trouvé. Utilisation du circuit par défaut.")
        circuit_dto = create_default_circuit()

    circuit = Circuit.from_dto(circuit_dto)

    print(f"[INFO] Circuit utilisé: {circuit.name}\n")
    # Créer/Charger l'agent et la Q-table UNE SEULE FOIS
    session = SessionLocal()
    db_agent = create_agent(session)
    agent_id = db_agent.id
    session.commit()
    session.close()

    # Créer le kart
    kart = KartFactory.create(
        kart_type="ql",
        config={"name": "QL Kart", "color": "red", "position": (0, 0)}
    )

    # Charger la Q-table depuis la DB (une seule fois)
    session = SessionLocal()
    load_q_table(kart, agent_id, session)
    session.close()



    for race_num in range(1, num_races + 1):

        start_positions = circuit.get_random_start_positions(1)
        kart.position = start_positions[0]
        kart.speed = 0
        kart.laps_done = 0
        kart.is_alive = True
        kart.has_finished = False
        kart.direction = "EAST"

        race = Race(circuit=circuit, karts=[kart], total_laps=total_laps)
        total_reward = 0
        crash_count = 0

        while not race.finished and kart.is_alive:
            current_kart = race.get_current_kart()
            if not isinstance(current_kart, QLearningKart):
                race.step(current_kart.choose_action())
                continue

            state = current_kart.get_state(race.circuit)
            action = current_kart.choose_action(state)
            old_position = current_kart.position
            race.step(action)

            crash = not current_kart.is_alive
            finished = current_kart.has_finished
            reward = current_kart.compute_reward(crash, finished, old_position, current_kart.position, circuit)
            total_reward += reward
            if crash:
                crash_count += 1

            next_state = None if crash or finished else current_kart.get_state(race.circuit)
            current_kart.learn(state, action, reward, next_state)

        kart.next_epsilon()  # ← Déplacé ici (après la boucle)
        print(f"Course {race_num}/{num_races} | ε={kart.epsilon:.2f} | Récompense: {total_reward:.1f} | États: {len(kart.q_table)}| Nb crash : {crash_count}")
  

    # ⭐ SAUVEGARDE FINALE UNIQUE (après toutes les courses)
    print("\n[SAUVEGARDE FINALE]...")
    session = SessionLocal()
    save_q_table(kart, agent_id, session)
    session.commit()
    session.close()
    print("[SAUVEGARDE FINALE] Terminée !")

if __name__ == "__main__":
    run_automated_races(num_races=50, total_laps=5)