from __future__ import annotations

from games.PixelKart.model.circuit import Circuit
from games.PixelKart.model.dto import RaceDTO
from games.PixelKart.model.kart import Kart

class Race:
    """Represents a PixelKart race and its game rules."""

    def __init__(self, circuit: Circuit, karts: list[Kart], total_laps: int) -> None:
        """
        Initialize a race.

        Args:
            circuit: Circuit used for the race.
            karts: List of karts participating in the race.
            total_laps: Number of laps required to win.

        Raises:
            ValueError: If the race configuration is invalid.
        """
        if not karts:
            raise ValueError("A race must contain at least one kart.")
        if total_laps <= 0:
            raise ValueError("The number of laps must be strictly positive.")

        self.circuit = circuit
        self.karts = karts
        self.total_laps = total_laps
        self.time = 0
        self.current_player_index = 0
        self.finished = False
        self.winner_name: str | None = None

    def get_current_kart(self) -> Kart:
        """Return the kart whose turn is currently being played."""
        return self.karts[self.current_player_index]

    def is_position_occupied(self, position: tuple[int, int]) -> bool:
        """
        Check whether a position is occupied by a kart still in the race.

        Args:
            position: Position to check.

        Returns:
            True if the position is occupied, False otherwise.
        """
        for kart in self.karts:
            if not kart.is_alive or kart.has_finished:
                continue
            if kart.position == position:
                return True
        return False

    def step(self, action: str | None = None) -> None:

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
        self.update_lap_if_needed(kart, old_position, traversed_positions)

        if kart.laps_done >= self.total_laps:
            if self.winner_name is None:
                self.winner_name = kart.name
            kart.finish()
        self.check_end_game()

        if not self.finished:
            self.next_player()

    def apply_movement(self, kart: Kart) -> list[tuple[int, int]]:
        """
        Apply the kart movement according to its speed and direction.

        The finish line can only be crossed towards the east.
        If the kart tries to cross it towards the west, its speed is reset
        and the movement stops.

        Args:
            kart: Kart to move.

        Returns:
            The list of traversed positions.
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

            if col_step == -1 and (
                self.circuit.is_finish(kart.position) or self.circuit.is_finish(next_position)
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
        Update the kart lap count if the finish line was crossed towards the east.
        """
        if not traversed_positions or not kart.is_alive:
            return

        previous_position = old_position

        for position in traversed_positions:
            if position[0] != previous_position[0] or position[1] != previous_position[1] + 1:
                return
            previous_position = position

        if any(self.circuit.is_finish(position) for position in traversed_positions):
            kart.complete_lap()

    def next_player(self) -> None:
        """
        Move to the next kart still in the race.

        The race time is increased when a full round has been completed.
        """
        if self.finished:
            return

        previous_index = self.current_player_index

        for step in range(1, len(self.karts) + 1):
            next_index = (previous_index + step) % len(self.karts)

            if not self.karts[next_index].is_alive or self.karts[next_index].has_finished:
                continue

            self.current_player_index = next_index
            if next_index <= previous_index:
                self.time += 1
            return

    def check_end_game(self) -> None:
        """
        End the race when all karts are either finished or eliminated.
        """
        if all(not kart.is_alive or kart.has_finished for kart in self.karts):
            self.finished = True

    def to_dto(self) -> RaceDTO:
        """
        Convert the race to a RaceDTO.

        Returns:
            A RaceDTO representing the current race state.
        """
        return {
            "time": self.time,
            "total_laps": self.total_laps,
            "current_player_index": self.current_player_index,
            "finished": self.finished,
            "winner_name": self.winner_name,
        }