"""
Define the karts used in PixelKart.

This module contains the base Kart class and the different kart types used in
the game: human karts, random AI karts, and Q-learning karts.

The base Kart class manages common data and actions such as speed, direction,
movement actions, lap state, and DTO conversion.

QLearningKart adds the Q-table, epsilon-greedy action selection, state creation,
reward calculation, and Q-value update used during training.
"""

from __future__ import annotations

import random

from games.pixelKart.model.dto import KartDTO
from games.pixelKart.model.circuit import Circuit


class Kart:
    """Represents a kart participating in a race."""

    MIN_SPEED = -1
    MAX_SPEED = 2

    ACTIONS = ["accelerate", "brake", "turn_left", "turn_right", "pass"]
    DIRECTIONS = ["NORTH", "EAST", "SOUTH", "WEST"]

    ROAD_CODE = 0
    GRASS_CODE = 1
    FINISH_CODE = 2
    WALL_CODE = 3
    OUT_OF_BOUNDS_CODE = 4

    TERRAIN_CODES = {
        "R": ROAD_CODE,
        "G": GRASS_CODE,
        "F": FINISH_CODE,
        "W": WALL_CODE,
    }

    LEFT_TURN = {
        "NORTH": "WEST",
        "WEST": "SOUTH",
        "SOUTH": "EAST",
        "EAST": "NORTH",
    }

    RIGHT_TURN = {
        "NORTH": "EAST",
        "EAST": "SOUTH",
        "SOUTH": "WEST",
        "WEST": "NORTH",
    }

    OPPOSITE = {
        "NORTH": "SOUTH",
        "SOUTH": "NORTH",
        "EAST": "WEST",
        "WEST": "EAST",
    }

    VECTORS = {
        "NORTH": (-1, 0),
        "EAST": (0, 1),
        "SOUTH": (1, 0),
        "WEST": (0, -1),
    }

    def __init__(
        self,
        name: str,
        color: str,
        position: tuple[int, int],
        direction: str = "EAST",
        speed: int = 0,
        laps_done: int = 0,
        is_alive: bool = True,
        has_finished: bool = False,
        is_ai: bool = False,
    ) -> None:
        """Initialize a kart."""
        self.name = name
        self.color = color
        self.position = position
        self.direction = direction
        self.speed = max(self.MIN_SPEED, min(self.MAX_SPEED, speed))
        self.laps_done = laps_done
        self.is_alive = is_alive
        self.has_finished = has_finished
        self.is_ai = is_ai

    def finish(self) -> None:
        """Mark the kart as finished."""
        self.has_finished = True
        self.speed = 0

    def opposite_direction(self) -> str:
        """Return the opposite of the current direction."""
        return self.OPPOSITE[self.direction]

    def direction_to_vector(self, direction: str | None = None) -> tuple[int, int]:
        """
        Convert a direction into a row and column movement.

        Args:
            direction: Direction to convert. Uses the current direction if omitted.

        Returns:
            Movement vector as (row_step, col_step).
        """
        target_direction = self.direction if direction is None else direction
        return self.VECTORS[target_direction]

    def simulate_action(self, action: str) -> tuple[int, str]:
        """
        Compute the speed and direction resulting from an action.

        Args:
            action: Action to simulate.

        Returns:
            New speed and direction without modifying the kart.

        Raises:
            ValueError: If the action is unknown.
        """
        speed = self.speed
        direction = self.direction

        if action == "accelerate":
            speed = min(speed + 1, self.MAX_SPEED)
        elif action == "brake":
            speed = max(speed - 1, self.MIN_SPEED)
        elif action == "turn_left":
            direction = self.LEFT_TURN[direction]
        elif action == "turn_right":
            direction = self.RIGHT_TURN[direction]
        elif action == "pass":
            pass
        else:
            raise ValueError(f"Unknown action: {action}")

        return speed, direction

    def apply_action(self, action: str) -> None:
        """
        Apply an action to the kart.

        Args:
            action: Action to apply.
        """
        self.speed, self.direction = self.simulate_action(action)

    def reset_speed(self) -> None:
        """Reset the kart speed to zero."""
        self.speed = 0

    def complete_lap(self) -> None:
        """Increase the number of completed laps by one."""
        self.laps_done += 1

    def eliminate(self) -> None:
        """Mark the kart as eliminated."""
        self.is_alive = False

    def to_dto(self) -> KartDTO:
        """
        Convert the kart to a DTO used by the view.

        Returns:
            Dictionary containing the kart display and race state.
        """
        return {
            "name": self.name,
            "color": self.color,
            "position": self.position,
            "direction": self.direction,
            "speed": self.speed,
            "laps_done": self.laps_done,
            "is_ai": self.is_ai,
            "is_alive": self.is_alive,
            "has_finished": self.has_finished,
        }


class HumanKart(Kart):
    """Represents a human-controlled kart."""


class RandomAIKart(Kart):
    """Represents a kart controlled by a random AI."""

    def __init__(
        self,
        name: str,
        color: str,
        position: tuple[int, int],
        direction: str = "EAST",
        speed: int = 0,
        laps_done: int = 0,
        is_alive: bool = True,
        has_finished: bool = False,
    ) -> None:
        """Initialize a random AI kart."""
        super().__init__(
            name=name,
            color=color,
            position=position,
            direction=direction,
            speed=speed,
            laps_done=laps_done,
            is_alive=is_alive,
            has_finished=has_finished,
            is_ai=True,
        )

    def choose_action(self) -> str:
        """Choose a random action among all available actions."""
        return random.choice(self.ACTIONS)


class QLearningKart(Kart):
    """
    Kart controlled by a Q-learning agent.

    The Q-table maps each state to one Q-value per action:
        q_table[state][action] = value
    """

    def __init__(
        self,
        name: str,
        color: str,
        position: tuple[int, int],
        direction: str = "EAST",
        speed: int = 0,
        laps_done: int = 0,
        is_alive: bool = True,
        has_finished: bool = False,
        q_table: dict[tuple, dict[str, float]] | None = None,
        epsilon: float = 0.9,
        alpha: float = 0.2,
        gamma: float = 0.95,
    ) -> None:
        """Initialize a Q-learning kart."""
        super().__init__(
            name=name,
            color=color,
            position=position,
            direction=direction,
            speed=speed,
            laps_done=laps_done,
            is_alive=is_alive,
            has_finished=has_finished,
            is_ai=True,
        )

        self.q_table = q_table if q_table is not None else {}
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma

    def ensure_state_exists(self, state: tuple) -> None:
        """Create the state in the Q-table if it does not exist yet."""
        if state not in self.q_table:
            self.q_table[state] = {}

        for action in self.ACTIONS:
            self.q_table[state].setdefault(action, 0.0)

    def exploit(self, state: tuple, allowed_actions: list[str]) -> str:
        """
        Choose the best known action for a state. use in choose_action.

        Args:
            state: Current Q-learning state.
            allowed_actions: Actions allowed by the race rules.

        Returns:
            One of the allowed actions with the highest Q-value.
        """
        best_value = max(self.q_table[state][action] for action in allowed_actions)

        best_actions = [
            action
            for action in allowed_actions
            if self.q_table[state][action] == best_value
        ]

        return random.choice(best_actions)

    def choose_action(
        self,
        state: tuple,
        allowed_actions: list[str],
    ) -> str:
        """
        Choose an action with an epsilon-greedy policy. used in Race.play_current_ai_turn() and training.

        Args:
            state: Current Q-learning state.
            allowed_actions: Actions allowed by the race rules.

        Returns:
            Random allowed action when exploring, otherwise the best known action.
        """
        self.ensure_state_exists(state)

        if random.random() < self.epsilon:
            return random.choice(allowed_actions)

        return self.exploit(state, allowed_actions)

    def learn(
        self,
        state: tuple,
        action: str,
        reward: float,
        next_state: tuple | None,
    ) -> None:
        """
        Update one Q-value after a training action. Use in training.

        Args:
            state: State before the action.
            action: Action chosen in that state.
            reward: Reward received after the action.
            next_state: State after the action, or None if the race ended.

        The update uses the Q-learning formula:
            new_q = current_q + alpha * (reward + gamma * max_next_q - current_q)
        """
        self.ensure_state_exists(state)

        current_q = self.q_table[state][action]

        if next_state is None:
            max_next_q = 0.0
        else:
            self.ensure_state_exists(next_state)
            max_next_q = max(self.q_table[next_state].values())

        target = reward + self.gamma * max_next_q
        self.q_table[state][action] = current_q + self.alpha * (target - current_q)

    def compute_reward(
        self,
        has_crashed: bool,
        has_finished: bool,
        old_position: tuple[int, int],
        new_position: tuple[int, int],
        circuit: Circuit,
        completed_lap: bool = False,
    ) -> float:
        """
        Compute the reward received by the Q-learning agent after one action. Use in training

        Args:
            has_crashed: True if the kart was eliminated during this turn.
            has_finished: True if the kart finished the race during this turn.
            old_position: Kart position before the action was played.
            new_position: Kart position after the action and movement were applied.
            circuit: Circuit used to check the terrain at the new position.
            action: Action chosen by the agent during this turn.
            completed_lap: True if the kart completed a lap during this turn.

        Returns:
            Reward value used to update the Q-table.

        Reward policy:
            - A crash gives a large negative reward because the kart is eliminated.
            - Finishing the race gives a large positive reward because the goal is reached.
            - Each action has a small time cost to discourage endless races.
            - Moving neutralizes the time cost so normal movement is not punished.
            - A useless non-pass action receives an extra penalty when the kart does not move.
            - Ending on grass gives a penalty because grass slows the kart.
            - Completing a lap gives an intermediate positive reward before the race is fully won.
        """
        if has_crashed:
            return -1000.0

        if has_finished:
            return 5000.0

        reward = -0.5

        if new_position != old_position:
            reward += 0.5
        else:
            reward -= 20.0

        if circuit.is_grass(new_position):
            reward -= 5.0

        if completed_lap:
            reward += 1000.0

        return reward
        
    def get_state(self, circuit: Circuit) -> tuple:
        """
        Build the state used by the Q-learning agent.

        Args:
            circuit: Circuit used to inspect the kart surroundings.

        Returns:
            Tuple describing position, nearby terrain, direction, speed and current terrain.
        """
        current_direction = (
            self.direction
            if self.speed >= 0
            else self.OPPOSITE[self.direction]
        )

        front_distance, front_terrain = self.scan_direction(circuit, current_direction)
        left_distance, left_terrain = self.scan_direction(circuit, self.LEFT_TURN[current_direction])
        right_distance, right_terrain = self.scan_direction(circuit,self.RIGHT_TURN[current_direction])

        return (
            self.position[0],
            self.position[1],
            front_distance,
            front_terrain,
            left_distance,
            left_terrain,
            right_distance,
            right_terrain,
            self.DIRECTIONS.index(self.direction),
            self.speed,
            self.get_terrain_code(circuit, self.position),
        )

    def scan_direction(self, circuit: Circuit, direction: str) -> tuple[int, int]:
        """
        Scan the terrain in one direction from the kart position.

        Args:
            circuit: Circuit to inspect.
            direction: Direction to scan.

        Returns:
            Discretized distance and terrain code of the first non-road cell found.
            Returns road at maximum distance if only road is found nearby.
        """
        delta_row, delta_col = self.direction_to_vector(direction)
        row, col = self.position

        for distance in range(1, 6):
            next_position = (
                row + delta_row * distance,
                col + delta_col * distance,
            )

            if not circuit.is_inside(next_position):
                return self.discretize_distance(distance), self.OUT_OF_BOUNDS_CODE

            terrain_code = self.get_terrain_code(circuit, next_position)

            if terrain_code != self.ROAD_CODE:
                return self.discretize_distance(distance), terrain_code

        return 3, self.ROAD_CODE

    @staticmethod
    def discretize_distance(distance: int) -> int:
        """
        Convert a raw distance into a compact distance code.

        Args:
            distance: Raw distance from the kart.

        Returns:
            Discretized distance code.
        """
        if distance == 1:
            return 0
        if distance == 2:
            return 1
        if distance <= 4:
            return 2
        return 3

    def get_terrain_code(self, circuit: Circuit, position: tuple[int, int]) -> int:
        """
        Return the terrain code at a circuit position.

        Args:
            circuit: Circuit to inspect.
            position: Position to inspect.

        Returns:
            Terrain code used in the Q-learning state.
        """
        cell = circuit.get_cell_type(position)
        return self.TERRAIN_CODES[cell]

    def next_epsilon(
        self,
        coef: float = 0.9995,
        min_epsilon: float = 0.02,
    ) -> None:
        """
        Reduce the exploration rate after a training race.

        Args:
            coef: Multiplicative decay factor.
            min_epsilon: Minimum exploration rate.
        """
        self.epsilon = max(min_epsilon, self.epsilon * coef)