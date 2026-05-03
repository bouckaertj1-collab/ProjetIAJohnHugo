from __future__ import annotations

import random

from games.PixelKart.model.dto import KartDTO


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
        elif action == "turn_left" or "turn_right":
            self.speed = max(self.speed - 1, 0) 
            if action == "turn_left":
                self.turn_left()
            else:
                self.turn_right()
        elif action == "pass":
            pass 

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

    def choose_action(self,state=None) -> str:
        """
        Choose a random action among all available actions.

        Returns:
            A randomly selected action.
        """
        return random.choice(
            ["accelerate", "brake", "turn_left", "turn_right", "pass"]
        )
    
class QLearningKart(Kart):
    def __init__(self, name, color, position, direction = "EAST", speed = 0, laps_done = 0, is_alive = True, has_finished = False):
        super().__init__(name, color, position, direction, speed, laps_done, is_alive, has_finished)

        self.epsilon: float = 0.9
        self.alpha: float = 0.2
        self.gamma: float = 0.95
        self.q_table = {}

    ACTIONS = ["accelerate", "brake", "turn_left", "turn_right", "pass"]
    
    @property
    def is_ai(self) -> bool:
        """Return True because this kart is AI-controlled."""
        return True

    def ensure_state_exists(self, state: tuple) -> None:
        """
        Ensure that a state and its legal actions exist in the Q-table.

        Args:
            state: Serialized state key.
        """
        if state not in self.q_table:
            self.q_table[state] = {}

        for action in self.ACTIONS:
            self.q_table[state].setdefault(action, 0.0)

    def exploit(self, state: tuple) -> str:
        """
        Choose the best known action for a given state.

        If several actions share the same best value, one of them is
        selected randomly.

        Args:
            state: Serialized state key.
            legal_moves: Legal actions available in this state.

        Returns:
            One of the best actions for this state.
        """
        self.ensure_state_exists(state)

        best_value = max(self.q_table[state][action] for action in self.ACTIONS)
        best_actions = [action for action in self.ACTIONS if self.q_table[state][action] == best_value]
        return random.choice(best_actions)

    def choose_action(self, state: tuple,circuit) -> str:
        front = self.distance_to_obstacle_front(circuit)
        behind = self.distance_to_obstacle_behind(circuit)  
        left = self.distance_to_obstacle_left(circuit)
        right = self.distance_to_obstacle_right(circuit)

        if front <= 1 and self.speed > 0:
            return "brake"

        if behind <= 1 and self.speed < 0:
            return "brake"

        if front == 0 and self.speed == 0:
            if left > 0 and right > 0:
                return random.choice(["turn_left", "turn_right"])
            elif left > 0:
                return "turn_left"
            elif right > 0:
                return "turn_right"
            else:
                return random.choice(["turn_left", "turn_right"])

        if random.random() < self.epsilon:
            return random.choice(self.ACTIONS)
        return self.exploit(state)

    def learn(self, state: tuple, action: str, reward: float, next_state: tuple | None) -> None:
        """
        Apply the Q-learning update.

        Args:
            state: Previous state.
            action: Action played from that state.
            reward: Reward obtained for the transition.
            next_state: Next state, or None if the game is over.
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
    
    def compute_reward(self, crash, finished, old_position, new_position,circuit,action):

        if crash:
            return -100
        if finished:
            return +100
        
        finish_positions = circuit.get_start_positions()
        
        old_dist = min(abs(old_position[0]- row ) + abs(old_position[1] - col ) for row,col in finish_positions )
        new_dist = min(abs(new_position[0]- row ) + abs(new_position[1] - col ) for row,col in finish_positions )

        reward = (old_dist - new_dist) * 10.0
        
        reward = 0.0
        
        if circuit.is_grass(new_position):
            reward -= 0.5
        if self.speed <= 0:
            reward -= 0.5
        
        if action == "pass":
            reward -= 2.0

        reward += 2.0

        return reward
    

    def get_state(self,circuit):
        """"""
        return (
                self.terrain_behind(circuit),
                self.distance_to_obstacle_front(circuit),
                self.distance_to_obstacle_behind(circuit),
                self.distance_to_obstacle_right(circuit),
                self.distance_to_obstacle_left(circuit),
                self.center_bucket(circuit),
                self.speed_level(),
                self.terrain_type(circuit),
                ["NORTH", "EAST", "SOUTH", "WEST"].index(self.direction),
            )
    
    def center_bucket(self,circuit):
        center_col = len(circuit.grid[0]) // 2
        dist_to_center = abs(self.position[1] - center_col)
        return  min(dist_to_center // 2, 3)
    
    def terrain_behind(self, circuit) -> int:
        """Retourne 0 si route/finish, 1 si herbe, 2 si mur (derrière)."""
        behind_pos = (
            self.position[0] + self.direction_to_vector(self.OPPOSITE[self.direction])[0],
            self.position[1] + self.direction_to_vector(self.OPPOSITE[self.direction])[1]
        )
        if not circuit.is_inside(behind_pos):
            return 2
        if circuit.is_wall(behind_pos):
            return 2
        if circuit.is_grass(behind_pos):
            return 1
        return 0 

    def distance_to_obstacle(self, circuit, direction: str) -> int:
        """
        Calcule la distance à l'obstacle dans une direction donnée.
        Args:
            circuit: Circuit actuel.
            direction: Direction à vérifier ("NORTH", "EAST", "SOUTH", "WEST").
        Returns:
            0 = obstacle immédiat (≤1 case),
            1 = proche (2 cases),
            2 = moyen (3-4 cases),
            3 = loin (≥5 cases).
        """
        delta_row, delta_col = self.direction_to_vector(direction)
        row, col = self.position

        for i in range(1, 6):
            next_pos = (row + delta_row * i, col + delta_col * i)
            if not circuit.is_inside(next_pos) or circuit.is_wall(next_pos):

                current_dir = self.direction if self.speed >= 0 else self.OPPOSITE[self.direction]
                if direction == current_dir and abs(self.speed) >= i:
                    return 0 
                if i <= 1: return 0
                if i == 2: return 1
                if i <= 4: return 2
                return 3
        return 3
    
    def distance_to_obstacle_front(self, circuit) -> int:
        """Distance à l'obstacle DEVANT le kart."""
        return self.distance_to_obstacle(circuit, self.direction)

    def distance_to_obstacle_behind(self, circuit) -> int:
        """Distance à l'obstacle DERRIÈRE le kart."""
        return self.distance_to_obstacle(circuit, self.OPPOSITE[self.direction])

    def distance_to_obstacle_left(self, circuit) -> int:
        """Distance à l'obstacle À GAUCHE du kart."""
        return self.distance_to_obstacle(circuit, self.LEFT_TURN[self.direction])

    def distance_to_obstacle_right(self, circuit) -> int:
        """Distance à l'obstacle À DROITE du kart."""
        return self.distance_to_obstacle(circuit, self.RIGHT_TURN[self.direction])


    def dist_to_finish_line(self,circuit):
        """État généralisable avec distance à l'objectif."""
        
        finish_positions = circuit.get_start_positions()

        if finish_positions:
            dist = min(abs(self.position[0]-row) + abs(self.position[1]-col)
                    for row, col in finish_positions)
            dist_to_finish = min(dist // 3, 3)
        else:
            dist_to_finish = 3

        return dist_to_finish

    def terrain_type(self, circuit) -> int:
        """0 = road/finish, 1 = grass"""
        return 1 if circuit.is_grass(self.position) else 0

    def speed_level(self):
        """
        This function return a level of the speed depending the real speed of the kart
            return : int
        """
        if self.speed <= 0:
            return 0
        elif self.speed < 2:
            return 1
        else:
            return 2       
        
    def next_epsilon(self, coef: float = 0.95, min_epsilon: float = 0.5) -> None:
        """
        Reduce exploration progressively after each game.

        Args:
            coef: Multiplicative decay coefficient.
            min_epsilon: Minimum exploration rate allowed.
        """
        self.epsilon = max(min_epsilon, self.epsilon * coef)
