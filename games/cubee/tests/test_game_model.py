import pytest
from games.cubee.game_model import GameModel


def test_step_valid_move_updates_position_and_board():
    game = GameModel("P1", "P2", size=3)

    game.player_turn = 1
    game.current_player = game.player1

    success = game.step("right")

    assert success is True
    assert game.player1.position == (0, 1)
    assert game.board[0][1] == 1


def test_step_invalid_move_out_of_bounds():
    game = GameModel("P1", "P2", size=3)

    game.player_turn = 1
    game.current_player = game.player1

    success = game.step("up")

    assert success is False
    assert game.player1.position == (0, 0)
    assert game.board[0][0] == 1


def test_step_invalid_move_on_opponent_cell():
    game = GameModel("P1", "P2", size=3)

    game.board = [
        [1, 2, 0],
        [0, 0, 0],
        [0, 0, 2]
    ]

    game.player1.position = (0, 0)
    game.player2.position = (2, 2)
    game.player_turn = 1
    game.current_player = game.player1

    success = game.step("right")

    assert success is False
    assert game.player1.position == (0, 0)


def test_available_moves_from_start_corner():
    game = GameModel("P1", "P2", size=3)

    game.player_turn = 1
    game.current_player = game.player1

    moves = game.available_moves()

    assert set(moves) == {"right", "down"}


def test_next_player_switches_turn():
    game = GameModel("P1", "P2", size=3)

    game.player_turn = 1
    game.current_player = game.player1

    game.next_player()

    assert game.player_turn == 2
    assert game.current_player == game.player2


def test_check_game_over_when_board_is_full():
    game = GameModel("P1", "P2", size=3)

    game.board = [
        [1, 1, 2],
        [1, 2, 2],
        [1, 2, 2]
    ]

    game.update_score()
    result = game.check_game_over()

    assert result is True
    assert game.is_game_over is True
    assert game.winner == game.player2


def test_board_to_string():
    game = GameModel("P1", "P2", size=3)

    game.board = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 2]
    ]

    assert game.board_to_string() == "100010002"


def test_get_state_dto_contains_expected_keys():
    game = GameModel("P1", "P2", size=3)

    dto = game.get_state_DTO()

    expected_keys = {
        "size",
        "board",
        "turn",
        "pos_p1",
        "pos_p2",
        "is_game_over",
        "score",
        "winner",
        "loser",
    }

    assert set(dto.keys()) == expected_keys


@pytest.mark.parametrize(
    "move, expected",
    [
        ("right", True),
        ("down", True),
        ("up", False),
        ("left", False),
    ]
)
def test_is_legal_move_from_start(move, expected):
    game = GameModel("P1", "P2", size=3)

    game.player_turn = 1
    game.current_player = game.player1

    assert game.is_legal_move(move) is expected