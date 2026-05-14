"""
Automated training script for PixelKart QLearningKart.

This script trains one Q-learning agent per circuit without opening the
Tkinter interface. Each circuit has its own Agent entry in the database and
therefore its own Q-table.

Training flow:
    1. load every circuit from circuits.txt;
    2. create or retrieve the database agent linked to the circuit;
    3. load the existing Q-table if one already exists;
    4. simulate many races with epsilon-greedy exploration;
    5. update the Q-table after each action;
    6. save the Q-table periodically and once again at the end;
    7. evaluate the final Q-table with epsilon set to 0.0.

The Q-table is saved in q_tables.db through the DAO/service layer.
The number of laps is used only for simulated races, not as part of the
database identity: one circuit corresponds to one saved Q-table.
"""

from __future__ import annotations

from pathlib import Path
import random

from games.pixelKart.dao.Q_table_dao import SessionLocal, init_db
from games.pixelKart.dao.q_table_service import create_agent, load_q_table, save_q_table
from games.pixelKart.model.circuit import Circuit
from games.pixelKart.model.kart_factory import KartFactory
from games.pixelKart.model.race import Race


TRAINING_TOTAL_LAPS = 2
TRAINING_RACES_PER_CONFIG = 20_000
EVALUATION_RACES_PER_CONFIG = 1_000
MAX_STEPS_PER_RACE = 1_500
LOG_EVERY = 100
SAVE_EVERY = 10000


def load_all_circuits() -> list[Circuit]:
    """
    Load all circuits from the PixelKart circuits file.

    Returns:
        A list of Circuit instances loaded from circuits.txt.

    Raises:
        FileNotFoundError: If circuits.txt cannot be found.
        ValueError: If no valid circuit is found in circuits.txt.
    """
    circuits_file = Path(__file__).parent / "circuits.txt"

    if not circuits_file.exists():
        raise FileNotFoundError(f"Fichier introuvable: {circuits_file}")

    circuits: list[Circuit] = []

    with circuits_file.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or ":" not in line:
                continue

            name, grid_str = line.split(":", 1)
            circuit = Circuit.from_dto(
                {
                    "name": name,
                    "grid": grid_str,
                }
            )
            circuits.append(circuit)

    if not circuits:
        raise ValueError("Aucun circuit valide trouvé dans circuits.txt.")

    return circuits


def create_training_kart():
    """
    Create a Q-learning kart used during automated training.

    Returns:
        A QLearningKart instance created by the kart factory.
    """
    return KartFactory.create(
        kart_type="ql",
        config={
            "name": "QL Kart",
            "color": "red",
            "position": (0, 0),
        },
    )


def reset_kart(kart, circuit: Circuit) -> None:
    """
    Reset a Q-learning kart before starting a new training race.

    The kart starts on a finish/start cell because, in PixelKart,
    the start line and the finish line are the same cells.

    Args:
        kart: QLearningKart instance to reset.
        circuit: Circuit used for the race.

    Raises:
        ValueError: If the circuit has no start/finish cell.
    """
    start_positions = circuit.get_start_positions()

    if not start_positions:
        raise ValueError(f"Le circuit {circuit.name} n'a aucune case F.")

    kart.position = random.choice(start_positions)
    kart.speed = 0
    kart.laps_done = 0
    kart.is_alive = True
    kart.has_finished = False
    kart.direction = "EAST"


def get_or_create_agent_id(circuit_name: str) -> int:
    """
    Retrieve or create the database agent linked to one circuit.

    Args:
        circuit_name: Name of the circuit.

    Returns:
        Database identifier of the matching agent.
    """
    session = SessionLocal()

    try:
        db_agent = create_agent(
            session=session,
            circuit_name=circuit_name,
            alpha=0.2,
            gamma=0.95,
            epsilon=1.0,
        )
        agent_id = db_agent.id
        session.commit()
        return agent_id

    finally:
        session.close()


def load_agent_q_table(kart, agent_id: int) -> None:
    """
    Load a saved Q-table into a Q-learning kart.

    Args:
        kart: QLearningKart instance receiving the Q-table.
        agent_id: Database identifier of the agent to load.
    """
    session = SessionLocal()

    try:
        load_q_table(kart, agent_id=agent_id, session=session)

    finally:
        session.close()


def save_agent_q_table(kart, agent_id: int) -> None:
    """
    Save a Q-learning kart Q-table into the database.

    Args:
        kart: QLearningKart instance containing the Q-table.
        agent_id: Database identifier of the agent to save.
    """
    session = SessionLocal()

    try:
        save_q_table(kart, session=session, agent_id=agent_id)

    finally:
        session.close()


def evaluate_agent(
    kart,
    circuit: Circuit,
    total_laps: int,
    num_races: int = EVALUATION_RACES_PER_CONFIG,
    max_steps: int = MAX_STEPS_PER_RACE,
) -> dict[str, int]:
    """
    Evaluate a trained Q-learning kart without exploration.

    Evaluation temporarily sets epsilon to 0.0. This means the kart no longer tries
    random actions and only exploits the best action stored in its Q-table.

    The evaluation result is therefore more representative of the final trained AI
    than the cumulative finish rate printed during training.
    """
    old_epsilon = kart.epsilon
    kart.epsilon = 0.0

    finished_count = 0
    crash_count = 0
    timeout_count = 0

    for _ in range(num_races):
        reset_kart(kart, circuit)

        race = Race(circuit=circuit, karts=[kart], total_laps=total_laps)
        steps = 0

        while (
            not race.finished
            and kart.is_alive
            and not kart.has_finished
            and steps < max_steps
        ):
            state = kart.get_state(race.circuit)
            allowed_actions = race.get_allowed_actions(kart)
            action = kart.choose_action(state, allowed_actions)

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
    print(f"Circuit: {circuit.name}")
    print(f"Tours: {total_laps}")
    print(
        f"Finish: {finished_count}/{num_races} "
        f"({finished_count / num_races * 100:.1f}%)"
    )
    print(f"Crash: {crash_count}")
    print(f"Timeout: {timeout_count}")

    return {
        "finished": finished_count,
        "crash": crash_count,
        "timeout": timeout_count,
    }


def train_agent_on_circuit(
    circuit: Circuit,
    total_laps: int,
    num_races: int = TRAINING_RACES_PER_CONFIG,
    max_steps: int = MAX_STEPS_PER_RACE,
    log_every: int = LOG_EVERY,
    save_every: int = SAVE_EVERY,
):
    """
    Train one Q-learning agent for one circuit.

    At each training step:
        1. the kart observes its current state with get_state();
        2. Race computes the allowed actions for that situation;
        3. QLearningKart chooses an action using epsilon-greedy selection;
        4. Race applies the action and moves the kart;
        5. the kart receives a reward;
        6. the Q-table is updated with the Q-learning formula.

    The Q-table is saved every save_every races and once at the end. In this
    project, save_every is set to 10 000 to avoid losing long training sessions
    while keeping database writes reasonable.

    The training finish rate printed during training is cumulative from the first
    race. It can be lower than the final evaluation result because the agent
    explores random actions during training.
    """
    print()
    print("=" * 80)
    print(f"[TRAINING] Circuit: {circuit.name} | Laps: {total_laps}")
    print("=" * 80)

    agent_id = get_or_create_agent_id(circuit_name=circuit.name)

    kart = create_training_kart()
    load_agent_q_table(kart, agent_id)

    kart.alpha = 0.2
    kart.gamma = 0.95
    kart.epsilon = 0.95

    finished_count = 0
    crash_count = 0
    timeout_count = 0
    recent_rewards: list[float] = []

    for race_num in range(1, num_races + 1):
        reset_kart(kart, circuit)

        race = Race(circuit=circuit, karts=[kart], total_laps=total_laps)
        total_reward = 0.0
        steps = 0

        while (
            not race.finished
            and kart.is_alive
            and not kart.has_finished
            and steps < max_steps
        ):
            state = kart.get_state(race.circuit)
            allowed_actions = race.get_allowed_actions(kart)
            action = kart.choose_action(state, allowed_actions)
            old_position = kart.position
            old_laps = kart.laps_done

            race.play_current_turn(action)

            crash = not kart.is_alive
            finished = kart.has_finished
            completed_lap = kart.laps_done > old_laps

            reward = kart.compute_reward(
                crash=crash,
                finished=finished,
                old_position=old_position,
                new_position=kart.position,
                circuit=circuit,
                action=action,
                completed_lap=completed_lap,
            )

            total_reward += reward

            next_state = None
            if not crash and not finished:
                next_state = kart.get_state(race.circuit)

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

        kart.next_epsilon(coef=0.99985, min_epsilon=0.02)

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

        if save_every > 0 and race_num % save_every == 0:
            save_agent_q_table(kart, agent_id)
            print(f"[SAVE] Q-table sauvegardée à la course {race_num}")

    save_agent_q_table(kart, agent_id)

    print("[INFO] Entraînement terminé.")
    print(f"Circuit: {circuit.name}")
    print(f"Tours: {total_laps}")
    print(f"Courses terminées: {finished_count}/{num_races}")
    print(f"Crashs: {crash_count}")
    print(f"Timeouts: {timeout_count}")
    print(f"États appris: {len(kart.q_table)}")

    return kart


def train_all_circuits(
    training_total_laps: int = TRAINING_TOTAL_LAPS,
    num_races: int = TRAINING_RACES_PER_CONFIG,
    max_steps: int = MAX_STEPS_PER_RACE,
) -> None:
    """
    Train one Q-learning agent for every circuit.

    Args:
        training_total_laps: Number of laps used during training.
        num_races: Number of training races per circuit.
        max_steps: Maximum number of steps per race.
    """
    init_db()

    circuits = load_all_circuits()

    print(f"[INFO] Circuits trouvés: {len(circuits)}")
    print(f"[INFO] Tours utilisés pour l'entraînement: {training_total_laps}")
    print(f"[INFO] Courses par circuit: {num_races}")

    for circuit in circuits:
        kart = train_agent_on_circuit(
            circuit=circuit,
            total_laps=training_total_laps,
            num_races=num_races,
            max_steps=max_steps,
        )

        evaluate_agent(
            kart=kart,
            circuit=circuit,
            total_laps=training_total_laps,
            num_races=EVALUATION_RACES_PER_CONFIG,
            max_steps=max_steps,
        )

    print()
    print("=" * 80)
    print("[DONE] Tous les circuits ont été entraînés.")
    print("=" * 80)


if __name__ == "__main__":
    train_all_circuits(
        training_total_laps=TRAINING_TOTAL_LAPS,
        num_races=TRAINING_RACES_PER_CONFIG,
        max_steps=MAX_STEPS_PER_RACE,
    )