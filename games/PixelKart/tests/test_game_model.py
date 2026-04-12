import pytest

from games.PixelKart.game_model.game_model import Direction, GameModel, Pixel
from games.PixelKart.game_controller import GameController


TRACK = [
    "..S..",
    "..S..",
    ".....",
]


def test_reset_places_kart_on_start_line_facing_east():
    game = GameModel(TRACK, total_laps=2, seed=0)

    assert game.current_kart.position in {(0, 2), (1, 2)}
    assert game.current_kart.direction == Direction.EAST
    assert game.current_kart.speed == 0
    assert game.turns_elapsed == 0
    assert game.laps_completed == 0


def test_accelerate_updates_speed_and_moves_forward():
    game = GameModel(TRACK, seed=0)
    game.current_kart.position = (2, 0)

    success = game.step("accelerate")

    assert success is True
    assert game.current_kart.position == (2, 1)
    assert game.current_kart.speed == 1
    assert game.turns_elapsed == 1
    assert game.last_turn_report is not None
    assert game.last_turn_report.effective_speed == 1


def test_brake_can_move_backwards():
    game = GameModel(TRACK, seed=0)
    game.current_kart.position = (2, 1)

    game.step("brake")

    assert game.current_kart.speed == -1
    assert game.current_kart.position == (2, 0)


def test_turn_changes_direction_before_automatic_move():
    game = GameModel(TRACK, seed=0)
    game.current_kart.position = (1, 1)
    game.current_kart.direction = Direction.EAST
    game.current_kart.pixels_per_turn = 1

    game.step("turn_left")

    assert game.current_kart.direction == Direction.NORTH
    assert game.current_kart.position == (0, 1)


def test_grass_halves_speed_with_floor_rounding():
    game = GameModel(
        [
            "Sg...",
            ".....",
        ],
        seed=0,
    )
    game.current_kart.position = (0, 1)
    game.current_kart.direction = Direction.EAST
    game.current_kart.pixels_per_turn = 2

    game.step("wait")

    assert game.get_pixel((0, 1)) == Pixel.GRASS
    assert game.current_kart.position == (0, 2)
    assert game.last_turn_report is not None
    assert game.last_turn_report.effective_speed == 1


def test_leaving_track_resets_speed_and_keeps_kart_in_bounds():
    game = GameModel(TRACK, seed=0)
    game.current_kart.position = (2, 3)
    game.current_kart.direction = Direction.EAST
    game.current_kart.pixels_per_turn = 2

    game.step("wait")

    assert game.current_kart.position == (2, 4)
    assert game.current_kart.speed == 0
    assert game.has_lost is False


def test_wall_ends_the_game_without_score():
    game = GameModel(
        [
            "S.#",
            "...",
        ],
        seed=0,
    )
    game.current_kart.position = (0, 1)
    game.current_kart.direction = Direction.EAST
    game.current_kart.pixels_per_turn = 1

    game.step("wait")

    assert game.current_kart.position == (0, 2)
    assert game.has_lost is True
    assert game.is_game_over is True
    assert game.score is None


def test_only_east_crossings_count_laps_and_finish_the_race():
    game = GameModel(TRACK, total_laps=2, seed=0)

    game.current_kart.position = (0, 3)
    game.current_kart.direction = Direction.WEST
    game.current_kart.pixels_per_turn = 1
    game.step("wait")

    assert game.laps_completed == 0
    assert game.has_won is False

    game.current_kart.position = (0, 1)
    game.current_kart.direction = Direction.EAST
    game.current_kart.pixels_per_turn = 1
    game.step("wait")

    assert game.laps_completed == 1
    assert game.has_won is False

    game.current_kart.position = (1, 1)
    game.current_kart.direction = Direction.EAST
    game.current_kart.pixels_per_turn = 1
    game.step("wait")

    assert game.laps_completed == 2
    assert game.has_won is True
    assert game.is_game_over is True
    assert game.score == 3


def test_track_must_be_rectangular_and_have_a_start_line():
    with pytest.raises(ValueError):
        GameModel([["S", "."], ["."]])

    with pytest.raises(ValueError):
        GameModel([[".", "."], [".", "."]])


def test_multiplayer_turns_rotate_between_active_karts():
    game = GameModel(TRACK, seed=0, player_names=("P1", "P2"))
    game.karts[0].position = (2, 0)
    game.karts[1].position = (2, 1)

    assert game.current_kart_index == 0

    game.step("accelerate")

    assert game.last_turn_report is not None
    assert game.last_turn_report.player_name == "P1"
    assert game.karts[0].turns_elapsed == 1
    assert game.current_kart_index == 1

    game.step("accelerate")

    assert game.last_turn_report is not None
    assert game.last_turn_report.player_name == "P2"
    assert game.karts[1].turns_elapsed == 1
    assert game.current_kart_index == 0


def test_controller_applies_one_turn_per_action():
    game = GameModel(TRACK, seed=0, player_names=("P1", "P2"))
    controller = GameController(game)

    success = controller.handle_action("wait")

    assert success is True
    assert game.global_turns_elapsed == 1
    assert game.current_kart_index == 1
