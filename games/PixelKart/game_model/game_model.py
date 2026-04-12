"""
Core model for the PixelKart game.

The model implements a turn-based race on a pixel grid. A kart has a position,
direction and speed. At each turn the player chooses a single action, then the
kart moves automatically according to its updated state.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Sequence
from games.PixelKart.game_model.direction import Direction
from games.PixelKart.game_model.kart import Kart
from games.PixelKart.game_model.normalization import normalize_action, normalize_track,parse_track,normalize_player_names
from games.PixelKart.game_model.types import Action, Pixel, Position, RawPixel
from games.PixelKart.game_model.physics import compute_effective_speed

@dataclass(slots=True)
class TurnReport:
    """Outcome of the last turn played."""

    player_index: int
    player_name: str
    action: Action
    position: Position
    direction: Direction
    speed: int
    effective_speed: int
    crossed_start_line: bool
    turns_elapsed: int
    laps_completed: int
    is_game_over: bool
    has_won: bool
    has_lost: bool


class GameModel:
    """Store the race state and apply the PixelKart rules."""

    MIN_SPEED = -1
    MAX_SPEED = 2
    
    DEFAULT_TRACK: str = (
      "Basic:GGGGGGGGWGGGGGGGGGGG,"
      "GGGRRRRRFRRRRRRRRGGG,"
      "GGRRRRRRFRRRRRRRRRGG,"
      "GRRRRRRRFRRRRRRRRRRG,"
      "GRRRRRGGWGGGGGGRRRRG,"
      "GRRRRGWWWWWWWWWGRRRG,"
      "GRRRRRGGGGGGGGGRRRRG,"
      "GRRRRRRRRRRRRRRRRRRG,"
      "GRRRRRRRRRRRRRRRRRRG,"
      "GGRRRRRRRRRRRRRRRRGG,"
      "GGGRRRRRRRRRRRRRRGGG,"
      "GGGGGGGGGGGGGGGGGGGG"
    )

    PLAYER_COLORS: tuple[str, ...] = (
        "#f97316",
        "#38bdf8",
        "#f43f5e",
        "#a3e635",
    )

    def __init__(
        self,
        track: str | Sequence[Sequence[RawPixel]] | None = None,
        total_laps: int = 1,
        seed: int | None = None,
        displayable: bool = True,
        player_names: Sequence[str] | None = None,
    ) -> None:
        """
        Initialize the game model.

        Args:
            track: Rectangular grid describing the circuit.
            total_laps: Number of valid start-line crossings required to win.
            seed: Optional random seed used to choose the starting cell.
            displayable: Kept for consistency with the other games.
            player_names: Names of the players. At least one player is required.
        """

        if total_laps < 1:
            raise ValueError("Minimum 1 total lap")

        track_name = ""
        if isinstance(track, str) or track is None:
            track_name, parsed_track = parse_track(track or self.DEFAULT_TRACK)
        else:
            parsed_track = track

        normalized_track,start_cells = normalize_track(parsed_track)

        self.track = normalized_track
        self.start_cells:tuple[Position,...] = start_cells
        self.track_name = track_name    
        players_name = normalize_player_names(player_names)
        self.displayable = displayable
        self.height = len(self.track)
        self.width = len(self.track[0])
        self.total_laps = total_laps
        self._rng = random.Random(seed)

        self.karts: list[Kart] = [
            Kart(
                position=self.start_cells[0],
                direction=Direction.EAST,
                name=name,
                color=self.PLAYER_COLORS[index % len(self.PLAYER_COLORS)],
            )
            for index, name in enumerate(players_name)
        ]

        self.current_kart_index = 0
        self.global_turns_elapsed = 0
        self.last_turn_report: TurnReport | None = None

        self.reset()

    
    @property
    def current_kart(self) -> Kart:
        """Return the kart whose turn it is."""
        return self.karts[self.current_kart_index]

    @property
    def is_game_over(self) -> bool:
        """"""
        if len(self.karts) < 1:
            return any(kart.has_won for kart in self.karts)
        else:
            return not self.karts[0].is_active

    @property
    def score(self) -> int | None:
        """Return the current kart score in turns, or None until it wins."""
        return self.current_kart.finish_time

    @property
    def turns_elapsed(self) -> int:
        """Return the number of turns played by the current kart."""
        return self.current_kart.turns_elapsed

    @property
    def laps_completed(self) -> int:
        """Return the current kart completed laps."""
        return self.current_kart.laps_completed

    @property
    def has_won(self) -> bool:
        """Return whether the current kart has finished the race."""
        return self.current_kart.has_won

    @property
    def has_lost(self) -> bool:
        """Return whether the current kart has crashed."""
        return self.current_kart.has_lost

    @property
    def finish_time(self) -> int | None:
        """Return the current kart final time if it has finished."""
        return self.current_kart.finish_time

    @property
    def winner(self) -> Kart | None:
        """Return the winning kart once the race is over."""
        winners = [kart for kart in self.karts if kart.has_won]
        if not winners:
            return None
        return min(winners, key=lambda kart: kart.finish_time or 0)

    def reset(self) -> None:
        """Reset the race and choose start-line positions for every kart."""
        start_positions = list(self.start_cells)
        self._rng.shuffle(start_positions)

        for index, kart in enumerate(self.karts):
            kart.reset(start_positions[index % len(start_positions)])

        self.current_kart_index = 0
        self.global_turns_elapsed = 0
        self.last_turn_report = None

    def available_actions(self) -> list[Action]:
        """Return the list of actions accepted by the model."""
        return list(Action)

    def is_in_bounds(self, position: Position) -> bool:
        """Check whether a position is inside the track."""
        row, col = position
        return 0 <= row < self.height and 0 <= col < self.width

    def get_pixel(self, position: Position) -> Pixel:
        """Return the tile at a given position."""
        row, col = position
        return self.track[row][col]

    def step(self, action: str | Action) -> bool:
        """
        Play one turn.

        The chosen action is applied first, then the kart moves automatically.

        Args:
            action: One of the supported PixelKart actions.

        Returns:
            False if the race is already over, True otherwise.
        """
        if self.is_game_over:
            return False

        normalized_action = normalize_action(action)
        acting_index = self.current_kart_index
        acting_kart = self.current_kart

        self.global_turns_elapsed += 1
        acting_kart.turns_elapsed += 1

        self._apply_action(normalized_action, acting_kart)
        effective_speed, crossed_start_line = self._move_kart(acting_kart)

        self.last_turn_report = TurnReport(
            player_index=acting_index,
            player_name=acting_kart.name,
            action=normalized_action,
            position=acting_kart.position,
            direction=acting_kart.direction,
            speed=acting_kart.speed,
            effective_speed=effective_speed,
            crossed_start_line=crossed_start_line,
            turns_elapsed=acting_kart.turns_elapsed,
            laps_completed=acting_kart.laps_completed,
            is_game_over=self.is_game_over,
            has_won=acting_kart.has_won,
            has_lost=acting_kart.has_lost,
        )

        if not self.is_game_over:
            self._advance_to_next_active_kart()

        return True

    def get_state_dto(self) -> dict:
        """Return a serializable snapshot of the current race state."""
        current_kart = self.current_kart
        return {
            "size": (self.height, self.width),
            "track": [[tile.value for tile in row] for row in self.track],
            "kart_position": current_kart.position,
            "kart_direction": current_kart.direction.value,
            "kart_speed": current_kart.speed,
            "kart_pixels_per_turn": current_kart.pixels_per_turn,
            "laps_completed": current_kart.laps_completed,
            "total_laps": self.total_laps,
            "turns_elapsed": current_kart.turns_elapsed,
            "global_turns_elapsed": self.global_turns_elapsed,
            "score": self.score,
            "has_won": current_kart.has_won,
            "has_lost": current_kart.has_lost,
            "is_game_over": self.is_game_over,
            "current_player_index": self.current_kart_index,
            "current_player_name": current_kart.name,
            "winner": self.winner.name if self.winner else None,
            "karts": [self._kart_to_dto(index, kart) for index, kart in enumerate(self.karts)],
        }

    def _apply_action(self, action: Action, kart: Kart) -> None:
        """Apply the chosen action before the automatic movement."""
        if action == Action.ACCELERATE:
            kart.pixels_per_turn = min(self.MAX_SPEED, kart.pixels_per_turn + 1)
        elif action == Action.BRAKE:
            kart.pixels_per_turn = max(self.MIN_SPEED, kart.pixels_per_turn - 1)
        elif action == Action.TURN_LEFT:
            kart.direction = kart.direction.turn_left()
        elif action == Action.TURN_RIGHT:
            kart.direction = kart.direction.turn_right()

    def _move_kart(self, kart: Kart) -> tuple[int, bool]:
        """
        Move the kart according to its current speed and terrain.

        Returns:
            A tuple containing the effective speed used during the turn and
            whether the start line was crossed in the valid direction.
        """
        pixel = self.get_pixel(kart.position)
        effective_speed = compute_effective_speed(pixel,kart)

        if effective_speed == 0:
            return 0, False

        step_direction = kart.direction if effective_speed > 0 else kart.direction.opposite()
        delta_row, delta_col = step_direction.delta
        crossed_start_line = False
        previous_position = kart.position

        for _ in range(abs(effective_speed)):
            next_position = (previous_position[0] + delta_row, previous_position[1] + delta_col)

            if not self.is_in_bounds(next_position):
                kart.pixels_per_turn = 0
                return effective_speed, crossed_start_line
            
            kart.position = next_position
            tile = self.get_pixel(next_position)

            if tile == Pixel.WALL:
                kart.has_lost = True
                kart.finish_time = None
                return effective_speed, crossed_start_line

            if self._crosses_start_line(previous_position, next_position):
                crossed_start_line = True
                kart.laps_completed += 1

                if kart.laps_completed >= self.total_laps:
                    kart.has_won = True
                    kart.finish_time = kart.turns_elapsed
                    return effective_speed, crossed_start_line

            previous_position = next_position

        return effective_speed, crossed_start_line

    

    def _crosses_start_line(self, previous: Position, current: Position) -> bool:
        """
        Check whether the start line was crossed in the valid direction.

        A valid lap is counted only when the kart enters a start tile while
        moving east (left to right).
        """
        if self.get_pixel(current) != Pixel.START:
            return False

        same_row = previous[0] == current[0]
        moved_east = current[1] - previous[1] == 1
        return same_row and moved_east

    def _advance_to_next_active_kart(self) -> None:
        """Move the turn to the next kart that is still racing."""
        if self.is_game_over:
            return

        for offset in range(1, len(self.karts) + 1):
            next_index = (self.current_kart_index + offset) % len(self.karts)
            if self.karts[next_index].is_active:
                self.current_kart_index = next_index
                return

    def _kart_to_dto(self, index: int, kart: Kart) -> dict:
        """Return a serializable snapshot of one kart."""
        return {
            "index": index,
            "name": kart.name,
            "color": kart.color,
            "position": kart.position,
            "direction": kart.direction.value,
            "speed": kart.speed,
            "pixels_per_turn": kart.pixels_per_turn,
            "laps_completed": kart.laps_completed,
            "turns_elapsed": kart.turns_elapsed,
            "score": kart.finish_time,
            "has_won": kart.has_won,
            "has_lost": kart.has_lost,
            "is_game_over": kart.is_active,
            "is_current": index == self.current_kart_index and not self.is_game_over,
        }

   
