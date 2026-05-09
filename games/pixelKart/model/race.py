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
        """
        Execute one step of the race for the current kart.

        Args:
            action: Action to perform (for human karts). If None, the kart is AI-controlled.
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

        if kart.laps_done >= self.total_laps:
            kart.finish()
            kart.speed = 0  
            self.check_end_game()
            return 

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
        Apply movement to the kart based on its speed and direction.

        Args:
            kart: Kart to move.

        Returns:
            List of positions traversed by the kart during this movement.
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
                if self.circuit.is_finish(kart.position) and col_step == 1: 
                    kart.position = next_position
                    traversed_positions.append(next_position)
                    remaining_steps -= 1
                    continue
                else:
                    kart.eliminate()
                    return traversed_positions

            if self.is_position_occupied(next_position):
                kart.reset_speed()
                return traversed_positions

            kart.position = next_position
            traversed_positions.append(next_position)
            remaining_steps -= 1

            if self.circuit.is_grass(kart.position):
                remaining_steps //= 2

        return traversed_positions

   
    def update_lap_if_needed(self, kart, old_position, traversed_positions):
        """
        Update the kart's lap count if it crosses the finish line.

        Args:
            kart: Kart to check for lap completion.
            old_position: Previous position of the kart.
            traversed_positions: List of positions traversed by the kart during this movement.
        """
        
        if not traversed_positions or not kart.is_alive:
            return

        finish_positions = self.circuit.get_start_positions()
        if not finish_positions:
            return
        finish_col = finish_positions[0][1]

        old_on_finish = self.circuit.is_finish(old_position)
        for pos in traversed_positions:
            if self.circuit.is_finish(pos) and not old_on_finish:
                current_dir = kart.direction if kart.speed >= 0 else kart.OPPOSITE[kart.direction]
                if old_position[1] < finish_col and pos[1] > old_position[1] and current_dir == "EAST":
                    kart.complete_lap()
                    old_on_finish = True
            else:
                old_on_finish = self.circuit.is_finish(pos)
                
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
        """ if all(not kart.is_alive or kart.has_finished for kart in self.karts):
            self.finished = True
        """
        if all(kart.has_finished for kart in self.karts):
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