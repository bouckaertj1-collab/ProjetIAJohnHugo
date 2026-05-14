from __future__ import annotations

from games.pixelKart.model.circuit import Circuit
from games.pixelKart.model.dto import RaceDTO
from games.pixelKart.model.kart import Kart, QLearningKart


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
        """Check whether a position is occupied by a kart still in the race."""
        for kart in self.karts:
            if not kart.is_alive or kart.has_finished:
                continue
            if kart.position == position:
                return True
        return False

    def play_current_turn(self, action: str) -> None:
        """Play the current kart turn with the given action."""
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
        Play the turn of the current AI kart.

        Raises:
            ValueError: If the current kart is not an AI kart.
        """
        kart = self.get_current_kart()

        if not kart.is_ai:
            raise ValueError("The current kart is not AI-controlled.")

        if isinstance(kart, QLearningKart):
            state = kart.get_state(self.circuit)
            allowed_actions = self.get_allowed_actions(kart)
            action = kart.choose_action(state, allowed_actions)
        else:
            action = kart.choose_action()

        self.play_current_turn(action)

    def get_allowed_actions(self, kart: Kart) -> list[str]:
        """
        Return the actions that the Q-learning agent is allowed to choose.

        This method belongs to Race, not QLearningKart, because deciding whether an
        action is allowed depends on race rules: circuit borders, walls, occupied cells
        and training-specific restrictions.

        The method filters:
            - actions that would immediately crash into a wall or leave the circuit;
            - maximum-speed turns, because after removing the old implicit slowdown
            from turn_left and turn_right, the agent tended to learn circular
            behaviours during training.

        This does not change the physical meaning of actions:
            - turn_left and turn_right only change direction;
            - brake is still the only action that reduces speed.
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
        Return whether the action is a turn attempted at maximum speed.

        A maximum-speed turn is technically possible in the race model. It is filtered
        only for the Q-learning agent because removing the old implicit slowdown from
        turn_left and turn_right made training unstable on larger circuits.

        Without this filter, the agent often learns circular behaviours: it keeps speed
        2 and repeatedly turns without building a useful trajectory. Filtering this
        case forces the agent to use brake before turning at maximum speed, while still
        keeping the action model clean.
        """
        return (
            action in {"turn_left", "turn_right"}
            and abs(kart.speed) >= kart.MAX_SPEED
        )

    def would_crash(self, kart: Kart, action: str) -> bool:
        """
        Predict whether an action would immediately make the kart crash.

        The action is simulated without modifying the real kart. The method checks the
        path that would be followed after applying the action speed and direction.

        It returns True when the simulated movement would:
            - leave the circuit;
            - hit a wall.

        It does not handle training restrictions such as maximum-speed turns. Those are
        handled separately by get_allowed_actions.
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
        """Update the kart lap count if the finish line was crossed eastward."""
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
        End the race only when there is a real winner or when all karts crashed.

        A kart does not win just because all the others crashed.
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
        """Convert the race to a RaceDTO."""
        return {
            "time": self.time,
            "total_laps": self.total_laps,
            "current_player_index": self.current_player_index,
            "finished": self.finished,
            "winner_name": self.winner_name,
        }