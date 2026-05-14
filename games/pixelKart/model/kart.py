from __future__ import annotations

import random

from games.pixelKart.model.dto import KartDTO
from games.pixelKart.model.circuit import Circuit

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
    
    ACTIONS = ["accelerate", "brake", "turn_left", "turn_right", "pass"]

    is_ai = False

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

    def simulate_movement(self, action: str, circuit: Circuit) -> list[tuple[int, int]]:
        """
        Simulate for a given action and return the traversed positions.
        Doesn't affect the state of the Kart.
        """
        speed, direction = self.simulate_action(action)
        position = self.position

        if speed == 0:
            return []
        
        return self.get_traversed_positions(speed,direction,circuit,position)
        

    def get_traversed_positions(self,speed:int,direction,circuit:Circuit,position):
        """
        Return the traversed positions  without consider the rules of the game.

        Args : speed, direction, circuit, position

        Return : the traversed positions of the kart

        Notes: 
            Explaination of the conditions for the traversed positions return
                1. if the next position is not out of the circuit : the function return the traversed positions before the cell out of the bounds
                2. if the next position is a wall : the function return the traversed positions before the wall

            If the position or the next position of the kart is on the grass : the number of remaining_cells_to_traverse are divided by 2.
        """
        row_step, col_step = self.get_effective_movement_vector()
        row, col = position
        remaining_cells_to_traverse = abs(speed)

        if circuit.is_grass(position):
            remaining_cells_to_traverse  //= 2

        traversed_positions = []

        while remaining_cells_to_traverse  > 0:
            next_position = (row + row_step, col + col_step)
            traversed_positions.append(next_position)

            if not circuit.is_inside(next_position):
                return traversed_positions
            if circuit.is_wall(next_position):
                return traversed_positions

            row, col = next_position
            remaining_cells_to_traverse  -= 1

            if circuit.is_grass((row, col)):
                remaining_cells_to_traverse  //= 2

        return traversed_positions


    def get_effective_movement_vector(self) -> tuple[int, int]:
        """Retourne (row_step, col_step) en tenant compte de la vitesse (négative = recul)."""
        direction = self.direction if self.speed >= 0 else self.opposite_direction()
        return self.direction_to_vector(direction)


    def simulate_action(self, action: str) -> tuple[int, str]:
        """
        Return the new (speed, direction) after applying action, without modifying state.
        """
        speed, direction = self.speed, self.direction
        if action == "accelerate":
            speed = min(speed + 1, self.MAX_SPEED)
        elif action == "brake":
            speed = max(speed - 1, self.MIN_SPEED)
        elif action == "turn_left":
            direction = self.LEFT_TURN[direction]
        elif action == "turn_right":
            direction = self.RIGHT_TURN[direction]
        return speed, direction

    def apply_action(self, action: str) -> None:
        """
        Apply an action to the kart state.

        Args:
            action: Action chosen for this turn.
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
    pass

class RandomAIKart(Kart):
    """Represents a kart controlled by a random AI."""

    is_ai = True

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

        super().__init__(
                name=name,
                color=color,
                position=position,
                direction=direction,
                speed=speed,
                laps_done=laps_done,
                is_alive=is_alive,
                has_finished = has_finished,
            )


    def choose_action(self) -> str:
        """
        Choose a random action among all available actions.

        Returns:
            A randomly selected action.
        """
        return random.choice(self.ACTIONS)
    
class QLearningKart(Kart):
    """Represents a kart controlled by a Q-learning agent."""

    
    is_ai = True

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

    def choose_action(self, state: tuple, circuit) -> str:
        """
        Choose an action using an epsilon-greedy policy.
        """
        self.ensure_state_exists(state)

        safe_actions = self.get_safe_actions(circuit)

        if random.random() < self.epsilon:
            return random.choice(safe_actions)

        return self.exploit(state, safe_actions)
    
    def get_safe_actions(self, circuit) -> list[str]:
        """
        Return simulated actions that do not immediately crash into a wall.
        """
        safe_actions = [
            action
            for action in self.ACTIONS
            if not self.would_crash(action, circuit)
        ]

        return safe_actions if safe_actions else ["brake"]
    
    def would_crash(self, action: str, circuit) -> bool:
        """
        Predict whether an action would immediately crash into a wall.

        This must mirror the real movement rules.
        """
        traversed = self.simulate_movement(action, circuit)
        return any(circuit.is_wall(pos) for pos in traversed)

    def learn(
        self,
        state: tuple,
        action: str,
        reward: float,
        next_state: tuple | None,
    ) -> None:
        """
        Update the Q-table using the Q-learning formula.

        Args : state, action, reward, next_state

        Notes: 
            - The agent learn within updating his Q-table using the Q-value formula.
            - The target is the immediate reward + gamma * the maximum Q-value of the next state.

            Hyperparameters explained :
                * The alpha controls is the learning rate.
                * The gamma manage how the agent enhances the future reward
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
    ) -> float:
        """
        Compute the reward after one action.

        The kart starts on the finish line, so we must not reward proximity
        to the finish line. Instead, the agent is rewarded for safely exploring
        the circuit and finishing the lap.

        Args: crash, finished, old_position, new_position, circuit

        Return : The computed reward based on a reward strategy explained in the "Notes" below.

        Notes: The reward strategy works the following way:

            1. If the agent crashed : return reward -1000 
            2. If the agent finish the race : return reward +5000 
            3. The reward automaticly decrease in the time to oblige the agent to finish faster
            4. If the new position of the agent is equal the old position the reward decrease of -2
            5. Else it means the agent moved and the reward increase of +2
            6. And if the new position of the agent is in the grass the reward decrease of -5. It allows the agent to dodge the grass
        """ 
        if crash:
            return -1000.0

        if finished:
            return 5000.0

        reward = -1.0

        if new_position == old_position:
            reward -= 2.0
        else:
            reward += 2.0


        if circuit.is_grass(new_position):
            reward -= 5.0

        return reward

    def get_state(self, circuit) -> tuple:
        """
        Build the discrete state used by the Q-learning agent.

        The position is included because the same obstacle distances can appear
        in different places of the circuit.

        Args: circuit

        Return : Return a state composed of :
            * The row and the column to get current the position of the kart.
            * The discretized distance from front,left and right of the kart to the nearest wall or border.
            * The indexes of the differents direction : (NORTH=0, EAST=1, SOUTH=2, WEST=3).
            * The current speed of the kart
            * A integer the terrain type for the current position : (R = 0, G = 1, F = 2)
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
            self.get_terrain_one_hot(circuit),
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

    def get_terrain_one_hot(self, circuit) -> int:
        """Return terrain code: 0=road, 1=grass, 2=finish."""
        cell = circuit.get_cell_type(self.position)
        return {"R": 0, "G": 1, "F": 2}[cell]

    def next_epsilon(
        self,
        coef: float = 0.9995,
        min_epsilon: float = 0.02,
    ) -> None:
        """Reduce exploration progressively after each race."""
        self.epsilon = max(min_epsilon, self.epsilon * coef)