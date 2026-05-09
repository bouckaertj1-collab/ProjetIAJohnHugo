"""
Entraînement headless du QLearningKart.
- Pas d'affichage graphique
- Peu de logs
- Beaucoup de courses
- Sauvegarde finale dans q_tables.db
"""

from pathlib import Path
import random

from games.pixelKart.dao.Q_table_dao import init_db, SessionLocal
from games.pixelKart.dao.q_table_service import save_q_table, load_q_table, create_agent
from games.pixelKart.model.circuit import Circuit
from games.pixelKart.model.kart_factory import KartFactory
from games.pixelKart.model.race import Race


def load_first_circuit() -> Circuit:
    circuits_file = Path(__file__).parent / "circuits.txt"

    if not circuits_file.exists():
        raise FileNotFoundError(f"Fichier introuvable: {circuits_file}")

    with circuits_file.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line and ":" in line:
                name, grid_str = line.split(":", 1)
                return Circuit.from_dto({"name": name, "grid": grid_str})

    raise ValueError("Aucun circuit valide trouvé dans circuits.txt")


def reset_kart(kart, circuit: Circuit) -> None:
    start_positions = circuit.get_start_positions()

    if not start_positions:
        raise ValueError("Le circuit n'a pas de ligne d'arrivée F pour démarrer.")

    kart.position = random.choice(start_positions)
    kart.speed = 0
    kart.laps_done = 0
    kart.is_alive = True
    kart.has_finished = False
    kart.direction = "EAST"
    kart.previous_action = None


def run_automated_races(
    num_races: int = 10_000,
    total_laps: int = 3,
    max_steps: int = 3_000,
    log_every: int = 100,
) -> None:
    init_db()

    circuit = load_first_circuit()
    print(f"[INFO] Circuit utilisé: {circuit.name}")

    session = SessionLocal()
    db_agent = create_agent(session)
    agent_id = db_agent.id
    session.commit()
    session.close()

    kart = KartFactory.create(
        kart_type="ql",
        config={
            "name": "QL Kart",
            "color": "red",
            "position": (0, 0),
        },
    )

    session = SessionLocal()
    load_q_table(kart, agent_id, session)
    session.close()

    kart.alpha = 0.2
    kart.gamma = 0.95
    kart.epsilon = 0.95

    finished_count = 0
    crash_count = 0
    timeout_count = 0
    recent_rewards = []

    for race_num in range(1, num_races + 1):
        reset_kart(kart, circuit)

        race = Race(circuit=circuit, karts=[kart], total_laps=total_laps)
        total_reward = 0.0
        steps = 0

        while not race.finished and kart.is_alive and not kart.has_finished and steps < max_steps:
            state = kart.get_state(race.circuit)
            action = kart.choose_action(state, race.circuit)
            old_position = kart.position

            race.play_current_turn(action)

            crash = not kart.is_alive
            finished = kart.has_finished

            reward = kart.compute_reward(
                crash=crash,
                finished=finished,
                old_position=old_position,
                new_position=kart.position,
                circuit=circuit,
                action=action,
            )

            total_reward += reward

            next_state = None if crash or finished else kart.get_state(race.circuit)
            kart.learn(state, action, reward, next_state)

            steps += 1

        if kart.has_finished:
            finished_count += 1
        elif not kart.is_alive:
            crash_count += 1
        else:
            timeout_count += 1

        recent_rewards.append(total_reward)
        if len(recent_rewards) > log_every:
            recent_rewards.pop(0)

        kart.next_epsilon(coef=0.9995, min_epsilon=0.02)

        if race_num % log_every == 0:
            avg_reward = sum(recent_rewards) / len(recent_rewards)
            finish_rate = finished_count / race_num * 100

            print(
                f"[{race_num}/{num_races}] "
                f"epsilon={kart.epsilon:.3f} | "
                f"states={len(kart.q_table)} | "
                f"avg_reward={avg_reward:.1f} | "
                f"finish={finish_rate:.1f}% | "
                f"crash={crash_count} | "
                f"timeout={timeout_count}"
            )

    print("[INFO] Sauvegarde finale...")
    session = SessionLocal()
    save_q_table(kart, session, agent_id)
    session.commit()
    session.close()

    print("[INFO] Entraînement terminé.")
    print(f"Courses terminées: {finished_count}/{num_races}")
    print(f"Crashs: {crash_count}")
    print(f"Timeouts: {timeout_count}")
    print(f"États appris: {len(kart.q_table)}")

    return kart, circuit

def evaluate_agent(kart, circuit, total_laps=1, num_races=1000, max_steps=1000):
    old_epsilon = kart.epsilon
    kart.epsilon = 0.0

    finished_count = 0
    crash_count = 0
    timeout_count = 0

    for _ in range(num_races):
        reset_kart(kart, circuit)

        race = Race(circuit=circuit, karts=[kart], total_laps=total_laps)
        steps = 0

        while not race.finished and kart.is_alive and not kart.has_finished and steps < max_steps:
            state = kart.get_state(race.circuit)
            action = kart.choose_action(state, race.circuit)
            race.play_current_turn(action)
            steps += 1

        if kart.has_finished:
            finished_count += 1
        elif not kart.is_alive:
            crash_count += 1
        else:
            timeout_count += 1

    kart.epsilon = old_epsilon

    print("=== EVALUATION ===")
    print(f"Finish: {finished_count}/{num_races} ({finished_count / num_races * 100:.1f}%)")
    print(f"Crash: {crash_count}")
    print(f"Timeout: {timeout_count}")

if __name__ == "__main__":
    kart, circuit = run_automated_races(
        num_races=10_000,
        total_laps=1,
        max_steps=500,
        log_every=100,
    )

    evaluate_agent(
        kart,
        circuit,
        total_laps=1,
        num_races=1000,
        max_steps=1500,
    )