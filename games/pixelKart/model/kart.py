from __future__ import annotations

import random

from games.pixelKart.model.dto import KartDTO


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
        """Convert a direction to a movement vector."""
        target_direction = self.direction if direction is None else direction
        return self.VECTORS[target_direction]

    def simulate_action(self, action: str) -> tuple[int, str]:
        """Return the speed and direction that would result from an action."""
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
        """Apply an action to the kart state."""
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
        """Convert the kart to a data transfer object."""
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

    The agent learns a Q-table where:
        - each key is a discrete state describing the kart situation;
        - each value is a dictionary mapping actions to Q-values.

    Example:
        {
            state_1: {
                "accelerate": 2.4,
                "brake": -0.5,
                "turn_left": 1.1,
                "turn_right": 0.0,
                "pass": 3.2,
            }
        }

    A Q-value represents the expected long-term reward of choosing one action
    in one state. During training, the agent sometimes explores random allowed
    actions using epsilon. During evaluation or real play, epsilon is set to
    0.0 so the agent only uses the best known action.
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

    def exploit(self, state: tuple, legal_actions: list[str] | None = None) -> str:
        """Choose the best known action for the given state."""
        self.ensure_state_exists(state)
        actions = legal_actions if legal_actions is not None else self.ACTIONS

        best_value = max(self.q_table[state][action] for action in actions)
        best_actions = [
            action
            for action in actions
            if self.q_table[state][action] == best_value
        ]

        return random.choice(best_actions)

    def choose_action(
        self,
        state: tuple,
        legal_actions: list[str] | None = None,
    ) -> str:
        """
        Choose an action using an epsilon-greedy policy.

        The agent receives a list of allowed actions from Race. This keeps the kart
        independent from race rules such as walls, borders or training restrictions.

        Decision process:
            - with probability epsilon, choose a random allowed action;
            - otherwise, choose the allowed action with the highest Q-value.

        During training, epsilon is high at the beginning to encourage exploration.
        During evaluation or in the graphical game, epsilon is set to 0.0 so the agent
        always exploits the learned Q-table.
        """
        self.ensure_state_exists(state)
        actions = legal_actions if legal_actions is not None else self.ACTIONS

        if not actions:
            actions = ["brake"]

        if random.random() < self.epsilon:
            return random.choice(actions)

        return self.exploit(state, actions)

    def learn(
        self,
        state: tuple,
        action: str,
        reward: float,
        next_state: tuple | None,
    ) -> None:
        """
        Update the Q-table using the Q-learning formula.

        Formula:
            Q(state, action) = Q(state, action)
                + alpha * (target - Q(state, action))

        Where:
            target = reward + gamma * max(Q(next_state, next_action))

        Meaning:
            - alpha controls how strongly new information updates old values;
            - gamma controls how much future rewards matter;
            - reward is the immediate result of the action;
            - next_state is None when the race ended after the action.

        This method is called after every action during automated training.
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
        crash: bool,
        finished: bool,
        old_position: tuple[int, int],
        new_position: tuple[int, int],
        circuit,
        action: str | None = None,
        completed_lap: bool = False,
    ) -> float:
        """
        Compute the reward received after one action.

        Reward design:
            - crash: very large negative reward because the kart is eliminated;
            - finished race: very large positive reward because the objective is reached;
            - time cost: small negative reward at each step to avoid endless races;
            - movement: neutralizes the time cost when the kart actually moves;
            - useless action: extra penalty when the kart does not move, except for pass;
            - grass: strong penalty because grass slows the kart and is usually bad;
            - completed lap: intermediate positive reward before the full race is won.

        Important:
            The action "pass" does not mean that the kart does not move. It only means
            that speed and direction are unchanged. If the kart already has speed, it
            still moves afterwards. This is why pass is not punished as a bad action.
        """
        if crash:
            return -1000.0

        if finished:
            return 5000.0

        reward = -0.5

        if new_position != old_position:
            reward += 0.5
        elif action != "pass":
            reward -= 1.0

        if circuit.is_grass(new_position):
            reward -= 5.0

        if completed_lap:
            reward += 1000.0

        return reward
        
    def get_state(self, circuit) -> tuple:
        """
        Build the discrete state used by the Q-learning agent.

        State format:
            (
                row,
                col,
                front_distance,
                front_terrain,
                left_distance,
                left_terrain,
                right_distance,
                right_terrain,
                direction_index,
                speed,
                current_terrain,
            )

        Meaning:
            - row and col keep the kart position on the current circuit;
            - front/left/right distances describe how close the next relevant terrain is;
            - front/left/right terrain codes tell whether the agent sees road, grass,
            finish, wall or out of bounds;
            - direction_index encodes NORTH/EAST/SOUTH/WEST as an integer;
            - speed keeps the current kart speed;
            - current_terrain describes the terrain under the kart.

        The position is intentionally kept because the Q-table is trained per circuit.
        This helps the agent learn circuit-specific behaviours. The state also includes
        local terrain information so the agent does not only know obstacle distances,
        but also the type of terrain around it.
        """
        current_direction = (
            self.direction
            if self.speed >= 0
            else self.OPPOSITE[self.direction]
        )

        front_distance, front_terrain = self.scan_direction(circuit, current_direction)
        left_distance, left_terrain = self.scan_direction(
            circuit,
            self.LEFT_TURN[current_direction],
        )
        right_distance, right_terrain = self.scan_direction(
            circuit,
            self.RIGHT_TURN[current_direction],
        )

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
            self.get_current_terrain_code(circuit),
        )

    def scan_direction(self, circuit, direction: str) -> tuple[int, int]:
        """
        Scan one direction from the kart position.

        The method looks up to five cells away and returns:
            - a discretized distance;
            - the terrain code of the first non-road cell found.

        Distance codes:
            0 = immediate cell;
            1 = close cell;
            2 = medium distance;
            3 = far away or only road found nearby.

        Terrain codes:
            ROAD_CODE = road;
            GRASS_CODE = grass;
            FINISH_CODE = finish/start line;
            WALL_CODE = wall;
            OUT_OF_BOUNDS_CODE = outside the circuit.

        This gives the Q-learning state more information than a simple wall distance:
        the agent can distinguish a wall, grass, finish line and out-of-bounds.
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
        """Return a compact distance code used in the Q-learning state."""
        if distance == 1:
            return 0
        if distance == 2:
            return 1
        if distance <= 4:
            return 2
        return 3

    def distance_to_obstacle(self, circuit, direction: str) -> int:
        """Return the discretized distance to a wall or circuit border."""
        distance, terrain_code = self.scan_direction(circuit, direction)

        if terrain_code in {self.WALL_CODE, self.OUT_OF_BOUNDS_CODE}:
            return distance

        return 3

    def get_terrain_code(
        self,
        circuit,
        position: tuple[int, int] | None = None,
    ) -> int:
        """
        Return the terrain code at a given circuit position.

        If no position is provided, the current kart position is used.

        Terrain codes are represented by named constants:
            - ROAD_CODE;
            - GRASS_CODE;
            - FINISH_CODE;
            - WALL_CODE;
            - OUT_OF_BOUNDS_CODE.

        These constants make the Q-learning state easier to understand than vague
        magic values such as 1 for grass and 0 for every other terrain.
        """
        target_position = self.position if position is None else position
        cell = circuit.get_cell_type(target_position)
        return self.TERRAIN_CODES[cell]

    def get_current_terrain_code(self, circuit) -> int:
        """Return the terrain code of the current kart position."""
        return self.get_terrain_code(circuit, self.position)

    def next_epsilon(
        self,
        coef: float = 0.9995,
        min_epsilon: float = 0.02,
    ) -> None:
        """Reduce exploration progressively after each race."""
        self.epsilon = max(min_epsilon, self.epsilon * coef)