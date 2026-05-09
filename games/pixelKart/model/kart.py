from __future__ import annotations

import random

from games.pixelKart.model.dto import KartDTO


class Kart:
    """Represents a kart participating in a race."""

    MIN_SPEED = -1
    MAX_SPEED = 2

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
    ) -> None:
        """
        Initialize a kart.

        Args:
            name: Kart name.
            color: Display color used by the view.
            position: Current kart position as (row, col).
            direction: Current facing direction.
            speed: Current speed.
            laps_done: Number of completed laps.
            is_alive: Whether the kart is still in the race.
            has_finished: Whether the kart has finished the race.
        """
        self.name = name
        self.color = color
        self.position = position
        self.direction = direction
        self.speed = max(self.MIN_SPEED, min(self.MAX_SPEED, speed))
        self.laps_done = laps_done
        self.is_alive = is_alive
        self.has_finished = has_finished

    @property
    def is_ai(self) -> bool:
        """Return whether the kart is controlled by an AI."""
        return False

    def finish(self) -> None:
        """Mark the kart as finished."""
        self.has_finished = True
        self.speed = 0

    def turn_left(self) -> None:
        """Turn the kart 90 degrees to the left."""
        self.direction = self.LEFT_TURN[self.direction]

    def turn_right(self) -> None:
        """Turn the kart 90 degrees to the right."""
        self.direction = self.RIGHT_TURN[self.direction]

    def opposite_direction(self) -> str:
        """Return the opposite of the current direction."""
        return self.OPPOSITE[self.direction]

    def direction_to_vector(self, direction: str | None = None) -> tuple[int, int]:
        """
        Convert a direction to a movement vector.

        Args:
            direction: Direction to convert. If None, use the current kart direction.

        Returns:
            A movement vector as (row_step, col_step).
        """
        target_direction = self.direction if direction is None else direction
        return self.VECTORS[target_direction]

    def apply_action(self, action: str) -> None:
        """
        Apply an action to the kart state.

        Args:
            action: Action chosen for this turn.
        """
        if action == "accelerate":
            self.speed = min(self.speed + 1, self.MAX_SPEED)
        elif action == "brake":
            self.speed = max(self.speed - 1, self.MIN_SPEED)
        elif action == "turn_left":
            self.turn_left()
        elif action == "turn_right":
            self.turn_right()

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
        Convert the kart to a data transfer object.

        Returns:
            A KartDTO representing the current kart state.
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

    @property
    def is_ai(self) -> bool:
        """Return True because this kart is AI-controlled."""
        return True

    def choose_action(self) -> str:
        """
        Choose a random action among all available actions.

        Returns:
            A randomly selected action.
        """
        return random.choice(
            ["accelerate", "brake", "turn_left", "turn_right", "pass"]
        )
    
class QLearningKart(Kart):
        """Represents a kart controlled by a Q-learning agent."""

        ACTIONS = ["accelerate", "brake", "turn_left", "turn_right", "pass"]

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
            super().__init__(
                name=name,
                color=color,
                position=position,
                direction=direction,
                speed=speed,
                laps_done=laps_done,
                is_alive=is_alive,
                has_finished=has_finished,
            )

            self.q_table = q_table if q_table is not None else {}
            self.epsilon = epsilon
            self.alpha = alpha
            self.gamma = gamma

        @property
        def is_ai(self) -> bool:
            """Return True because this kart is AI-controlled."""
            return True

        def ensure_state_exists(self, state: tuple) -> None:
            """Create the state in the Q-table if it does not exist yet."""
            if state not in self.q_table:
                self.q_table[state] = {}

            for action in self.ACTIONS:
                self.q_table[state].setdefault(action, 0.0)

        def exploit(self, state: tuple) -> str:
            """Choose the best known action for the given state."""
            self.ensure_state_exists(state)

            best_value = max(self.q_table[state].values())
            best_actions = [
                action
                for action, value in self.q_table[state].items()
                if value == best_value
            ]

            return random.choice(best_actions)

        def choose_action(self, state: tuple, circuit) -> str:
            """
            Choose an action using an epsilon-greedy policy.

            With probability epsilon, the kart explores randomly.
            Otherwise, it chooses the best known action from the Q-table.
            """
            self.ensure_state_exists(state)

            current_direction = (
                self.direction
                if self.speed >= 0
                else self.OPPOSITE[self.direction]
            )

            # Small safety rule: if the kart is moving directly into a wall,
            # braking is usually better than continuing.
            if self.speed != 0 and self.distance_to_obstacle(circuit, current_direction) == 0:
                return "brake"

            if random.random() < self.epsilon:
                return random.choice(self.ACTIONS)

            return self.exploit(state)

        def learn(
            self,
            state: tuple,
            action: str,
            reward: float,
            next_state: tuple | None,
        ) -> None:
            """Update the Q-table using the Q-learning formula."""
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
            crash: bool,
            finished: bool,
            old_position: tuple[int, int],
            new_position: tuple[int, int],
            circuit,
            action: str,
        ) -> float:
            """
            Compute the reward after one action.

            The reward is intentionally moderate to keep learning stable.
            """
            if crash:
                return -1000.0

            if finished:
                return 5000.0

            reward = -1.0

            if new_position == old_position:
                reward -= 2.0
            else:
                reward += 1.0

            if circuit.is_grass(new_position):
                reward -= 10.0

            if action == "pass":
                reward -= 3.0

            finish_positions = circuit.get_start_positions()

            if finish_positions:
                current_direction = (
                    self.direction
                    if self.speed >= 0
                    else self.OPPOSITE[self.direction]
                )

                if new_position in finish_positions and old_position not in finish_positions:
                    if current_direction == "EAST" and new_position[1] > old_position[1]:
                        reward += 500.0
                    else:
                        reward -= 500.0

                old_distance = min(
                    abs(old_position[0] - finish[0]) + abs(old_position[1] - finish[1])
                    for finish in finish_positions
                )
                new_distance = min(
                    abs(new_position[0] - finish[0]) + abs(new_position[1] - finish[1])
                    for finish in finish_positions
                )

                reward += (old_distance - new_distance) * 5.0

            return reward

        def get_state(self, circuit) -> tuple:
            """
            Build the discrete state used by the Q-learning agent.

            The position is included because the same obstacle distances can appear
            in different places of the circuit.
            """
            current_direction = (
                self.direction
                if self.speed >= 0
                else self.OPPOSITE[self.direction]
            )

            front_distance = self.distance_to_obstacle(circuit, current_direction)
            left_distance = self.distance_to_obstacle(
                circuit,
                self.LEFT_TURN[current_direction],
            )
            right_distance = self.distance_to_obstacle(
                circuit,
                self.RIGHT_TURN[current_direction],
            )

            return (
                self.position[0],
                self.position[1],
                front_distance,
                left_distance,
                right_distance,
                ["NORTH", "EAST", "SOUTH", "WEST"].index(self.direction),
                self.speed,
                self.terrain_type(circuit),
                self.laps_done,
            )

        def distance_to_obstacle(self, circuit, direction: str) -> int:
            """
            Return a discretized distance to the nearest wall or border.

            0 means immediate obstacle.
            3 means no obstacle nearby.
            """
            delta_row, delta_col = self.direction_to_vector(direction)
            row, col = self.position

            for distance in range(1, 6):
                next_position = (
                    row + delta_row * distance,
                    col + delta_col * distance,
                )

                if not circuit.is_inside(next_position) or circuit.is_wall(next_position):
                    if distance == 1:
                        return 0
                    if distance == 2:
                        return 1
                    if distance <= 4:
                        return 2
                    return 3

            return 3

        def terrain_type(self, circuit) -> int:
            """Return 1 on grass, 0 otherwise."""
            return 1 if circuit.is_grass(self.position) else 0

        def next_epsilon(
            self,
            coef: float = 0.9995,
            min_epsilon: float = 0.02,
        ) -> None:
            """Reduce exploration progressively after each race."""
            self.epsilon = max(min_epsilon, self.epsilon * coef)