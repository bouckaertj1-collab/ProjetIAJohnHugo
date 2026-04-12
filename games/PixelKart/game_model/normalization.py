    
from typing import Sequence
from games.PixelKart.game_model.types import  Pixel, Position, RawPixel, Action

_PIXEL_ALIASES: dict[RawPixel, Pixel] = {
    Pixel.ROAD: Pixel.ROAD,
    Pixel.GRASS: Pixel.GRASS,
    Pixel.WALL: Pixel.WALL,
    Pixel.START: Pixel.START,

    ".": Pixel.ROAD,
    "r": Pixel.ROAD,
    "road": Pixel.ROAD,

    "g": Pixel.GRASS,
    "grass": Pixel.GRASS,

    "#": Pixel.WALL,
    "w": Pixel.WALL,
    "wall": Pixel.WALL,

    "f": Pixel.START,
    "start": Pixel.START,
    "=": Pixel.START,

    0: Pixel.ROAD,
    1: Pixel.GRASS,
    2: Pixel.WALL,
    3: Pixel.START,
}

_ACTION_ALIASES: dict[str | Action, Action] = {
    Action.ACCELERATE: Action.ACCELERATE,
    Action.BRAKE: Action.BRAKE,
    Action.TURN_LEFT: Action.TURN_LEFT,
    Action.TURN_RIGHT: Action.TURN_RIGHT,
    Action.WAIT: Action.WAIT,

    "accelerate": Action.ACCELERATE,
    "accel": Action.ACCELERATE,

    "brake": Action.BRAKE,

    "turn_left": Action.TURN_LEFT,
    "left": Action.TURN_LEFT,

    "turn_right": Action.TURN_RIGHT,
    "right": Action.TURN_RIGHT,

    "wait": Action.WAIT,
    "noop": Action.WAIT,
    "nothing": Action.WAIT,
}

def parse_track(track: str) -> tuple[str, list[list[str]]]:
    try:
        name, raw_track = track.split(":", 1)
    except ValueError:
        raise ValueError(f"Invalid track format: {track!r}")
    
    rows = raw_track.split(",")
    grid = [list(row.strip()) for row in rows if row.strip()]

    return name.strip(), grid


def normalize_player_names(player_names: Sequence[str] | None) -> tuple[str, ...]:
    """Validate player names and provide a default one-player race."""
    if player_names is None:
        return ("Player 1",)
    if isinstance(player_names, str):
        player_names = (player_names,)

    names = tuple(name.strip() for name in player_names if name.strip())
    if not names:
        raise ValueError("PixelKart requires at least one player.")

    return names

def normalize_track(track: Sequence[Sequence[RawPixel]] ) -> tuple[tuple[tuple[Pixel, ...], ...], tuple[Position, ...]]:
    """Validate the circuit and convert every raw cell to a Pixel."""
    if not track:
        raise ValueError("track must contain at least one row.")

    width = len(track[0])
    if width == 0:
        raise ValueError("track rows must not be empty.")

    normalized_rows: list[tuple[Pixel, ...]] = []
    start_cells: list[Position] = []

    for row_index, raw_row in enumerate(track):
        if len(raw_row) != width:
            raise ValueError("track must be rectangular.")

        normalized_row: list[Pixel] = []
        for col_index, raw_tile in enumerate(raw_row):
            tile = normalize_tile(raw_tile)
            normalized_row.append(tile)

            if tile == Pixel.START:
                start_cells.append((row_index, col_index))

        normalized_rows.append(tuple(normalized_row))

    if not start_cells:
        raise ValueError("track must contain at least one start tile.")

    return tuple(normalized_rows), tuple(start_cells)

def normalize_tile(raw_tile: RawPixel) -> Pixel:
    """Convert a raw cell representation to a Tile."""
    key = raw_tile.lower() if isinstance(raw_tile, str) else raw_tile
    try:
        return _PIXEL_ALIASES[key]
    except KeyError as exc:
        raise ValueError(f"Unsupported tile value: {raw_tile!r}") from exc

def normalize_action(action: str | Action) -> Action:
    """Convert a raw action representation to an Action."""
    key = action.lower() if isinstance(action, str) else action
    try:
        return _ACTION_ALIASES[key]
    except KeyError as exc:
        raise ValueError(f"Unsupported action: {action!r}") from exc