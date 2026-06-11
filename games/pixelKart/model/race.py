"""
Manage a PixelKart race.

This module contains the Race class. It keeps the current state of the race and
updates it after each turn.

It manages the current kart, the played actions, the kart movements, crashes,
laps, finish detection, and AI turns.

It also contains helper methods used by Q-learning karts to know which actions
are allowed by the race rules.
"""

from __future__ import annotations

from games.pixelKart.model.circuit import Circuit
from games.pixelKart.model.dto import RaceDTO
from games.pixelKart.model.kart import Kart, QLearningKart


class Race:
    """Manage a PixelKart race and its rules."""

    def __init__(self, circuit: Circuit, karts: list[Kart], total_laps: int) -> None:
        """
        Initialize a race.

        Args:
            circuit: Circuit used for the race.
            karts: Karts participating in the race.
            total_laps: Number of laps required to win.

        Raises:
            ValueError: If there are no karts or if total_laps is invalid.
        """
        self.circuit = circuit
        self.karts = karts
        self.total_laps = total_laps
        self.time = 0
        self.current_player_index = 0
        self.finished = False
        self.winner_name: str | None = None

    def get_current_kart(self) -> Kart:
        """
        Return the kart whose turn is currently active.

        Returns:
            Current kart.
        """
        return self.karts[self.current_player_index]

    def is_position_occupied(self, position: tuple[int, int]) -> bool:
        """
        Check whether an active kart occupies a position.

        Args:
            position: Position to check.

        Returns:
            True if a living and unfinished kart is on the position.
        """
        for kart in self.karts:
            if not kart.is_alive or kart.has_finished:
                continue
            if kart.position == position:
                return True
        return False

    def play_current_turn(self, action: str) -> None:
        """
        Play one turn for the current kart.

        The method applies the chosen action, moves the kart, updates laps,
        checks if the race is finished, and selects the next player.

        Args:
            action: Action chosen by the current kart.
        """
        if self.finished:
            return

        kart = self.get_current_kart()

        if not kart.is_alive or kart.has_finished:
            self.next_player()
            self.check_end_game()
            return

        old_position = kart.position
        kart.apply_action(action)

        traversed_positions = self.apply_movement(kart)

        if kart.is_alive:
            self.update_lap_if_needed(kart, old_position, traversed_positions)

        if kart.is_alive and kart.laps_done >= self.total_laps:
            kart.finish()
            self.winner_name = kart.name
            self.finished = True
            return

        self.check_end_game()

        if not self.finished:
            self.next_player()

    def play_current_ai_turn(self) -> None:
        """
        Play one turn for the current AI kart.

        Raises:
            ValueError: If the current kart is not controlled by an AI.
        """
        kart = self.get_current_kart()

        if isinstance(kart, QLearningKart):
            state = kart.get_state(self.circuit)
            allowed_actions = self.get_allowed_actions(kart)
            action = kart.choose_action(state, allowed_actions)
        else:
            action = kart.choose_action()

        self.play_current_turn(action)

    def get_allowed_actions(self, kart: Kart) -> list[str]:
        """
        Return the actions allowed for a Q-learning kart.

        Args:
            kart: Kart for which actions are checked.

        Returns:
            Actions that do not immediately crash and do not turn at maximum speed.
        """
        allowed_actions = []

        for action in kart.ACTIONS:
            if self.would_crash(kart, action):
                continue

            if self.is_high_speed_turn(kart, action):
                continue

            allowed_actions.append(action)

        return allowed_actions if allowed_actions else ["brake"]

    def is_high_speed_turn(self, kart: Kart, action: str) -> bool:
        """
        Check whether an action is a turn at maximum speed.

        Args:
            kart: Kart trying to play the action.
            action: Action to check.

        Returns:
            True if the action is a left or right turn at maximum speed.
        """
        return (
            action in {"turn_left", "turn_right"}
            and abs(kart.speed) >= kart.MAX_SPEED
        )

    def would_crash(self, kart: Kart, action: str) -> bool:
        """
        Predict whether an action would hit a wall or leave the circuit.

        Args:
            kart: Kart for which the action is simulated.
            action: Action to simulate.

        Returns:
            True if the simulated movement would leave the circuit or hit a wall.
        """
        speed, direction = kart.simulate_action(action)

        if speed == 0:
            return False

        move_direction = direction if speed > 0 else kart.OPPOSITE[direction]
        row_step, col_step = kart.direction_to_vector(move_direction)

        row, col = kart.position
        remaining_steps = abs(speed)

        if self.circuit.is_grass(kart.position):
            remaining_steps //= 2

        while remaining_steps > 0:
            next_position = (row + row_step, col + col_step)

            if not self.circuit.is_inside(next_position):
                return True

            if self.circuit.is_wall(next_position):
                return True

            row, col = next_position
            remaining_steps -= 1

            if self.circuit.is_grass((row, col)):
                remaining_steps //= 2

        return False

    def apply_movement(self, kart: Kart) -> list[tuple[int, int]]:
        """
        Move a kart according to its current speed and direction.

        The movement stops if the kart leaves the circuit, hits another kart,
        hits a wall, or tries to cross the finish line westward.

        Args:
            kart: Kart to move.

        Returns:
            Positions crossed during the movement.
        """
        traversed_positions: list[tuple[int, int]] = []

        if kart.speed == 0:
            return traversed_positions

        if kart.speed > 0:
            row_step, col_step = kart.direction_to_vector()
        else:
            row_step, col_step = kart.direction_to_vector(kart.opposite_direction())

        remaining_steps = abs(kart.speed)

        if self.circuit.is_grass(kart.position):
            remaining_steps //= 2

        while remaining_steps > 0:
            row, col = kart.position
            next_position = (row + row_step, col + col_step)

            if not self.circuit.is_inside(next_position):
                kart.reset_speed()
                return traversed_positions

            if self.circuit.is_wall(next_position):
                kart.eliminate()
                return traversed_positions

            if self.is_position_occupied(next_position):
                kart.reset_speed()
                return traversed_positions
            
            # Prevent crossing the finish line in the wrong direction.
            if col_step == -1 and (
                self.circuit.is_finish(kart.position)
                or self.circuit.is_finish(next_position)
            ):
                kart.reset_speed()
                return traversed_positions

            kart.position = next_position
            traversed_positions.append(next_position)
            remaining_steps -= 1

            if self.circuit.is_grass(kart.position):
                remaining_steps //= 2

        return traversed_positions

    def update_lap_if_needed(
        self,
        kart: Kart,
        old_position: tuple[int, int],
        traversed_positions: list[tuple[int, int]],
    ) -> None:
        """
        Complete a lap if the kart crossed the finish line eastward.

        Args:
            kart: Kart to update.
            old_position: Position before the movement.
            traversed_positions: Positions crossed during the movement.
        """
        if not traversed_positions or not kart.is_alive:
            return

        previous_position = old_position

        for position in traversed_positions:
            if (
                position[0] != previous_position[0]
                or position[1] != previous_position[1] + 1
            ):
                return
            previous_position = position

        if any(self.circuit.is_finish(position) for position in traversed_positions):
            kart.complete_lap()

    def next_player(self) -> None:
        """
        Select the next active kart.

        The race time increases when the turn order loops back to an earlier index.
        """
        if self.finished:
            return

        previous_index = self.current_player_index

        for step in range(1, len(self.karts) + 1):
            next_index = (previous_index + step) % len(self.karts)

            if (
                not self.karts[next_index].is_alive
                or self.karts[next_index].has_finished
            ):
                continue

            self.current_player_index = next_index
            if next_index <= previous_index:
                self.time += 1
            return

    def check_end_game(self) -> None:
        """
        Update the race end state if the race is over.

        The race ends when a kart has finished or when all karts are eliminated.
        """
        if self.finished:
            return

        finished_karts = [kart for kart in self.karts if kart.has_finished]

        if finished_karts:
            self.winner_name = finished_karts[0].name
            self.finished = True
            return

        if all(not kart.is_alive for kart in self.karts):
            self.winner_name = None
            self.finished = True

    def to_dto(self) -> RaceDTO:
        """
        Convert the race to a DTO.

        Returns:
            Dictionary containing the race state for the view.
        """
        return {
            "time": self.time,
            "total_laps": self.total_laps,
            "current_player_index": self.current_player_index,
            "finished": self.finished,
            "winner_name": self.winner_name,
        }