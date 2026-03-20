import pytest

from games.cubee.game_model import GameModel
from games.cubee.game_controller import GameController

def test_is_legal_move_to_opponent_cell():
    game = GameModel("P1", "P2", size=3)
    game.player_turn = 1
    game.player1.position = (0, 0)
    game.board = [
        [1, 2, 0],
        [0, 0, 0],
        [0, 0, 2],
    ]

    assert game.is_legal_move("right") is False

def test_step_updates_position_board_score_and_turn():
    game = GameModel("P1", "P2", size=3)
    game.player_turn = 1
    game.player1.position = (0, 0)
    game.player2.position = (2, 2)
    game.board = [
        [1, 0, 0],
        [0, 0, 0],
        [0, 0, 2],
    ]
    game.update_score()

    success = game.step("right")

    assert success is True
    assert game.player1.position == (0, 1)
    assert game.board[0][1] == 1
    assert game.score == (2, 1)
    assert game.player_turn == 2

def test_check_game_over_sets_winner_and_stats():
    game = GameModel("P1", "P2", size=3)
    game.board = [
        [1, 1, 1],
        [1, 1, 2],
        [2, 2, 2],
    ]
    game.update_score()

    result = game.check_game_over()

    assert result is True
    assert game.is_game_over is True
    assert game.winner == game.player1
    assert game.loser == game.player2
    assert game.player1.nb_win == 1
    assert game.player2.nb_lose == 1
    assert game.player1.nb_game == 1
    assert game.player2.nb_game == 1


def test_reset_restores_initial_state():
    game = GameModel("P1", "P2", size=4)
    game.board = [
        [1, 1, 1, 1],
        [1, 2, 2, 1],
        [1, 2, 2, 1],
        [1, 1, 1, 2],
    ]
    game.player1.position = (2, 2)
    game.player2.position = (1, 1)
    game.is_game_over = True
    game.winner = game.player1
    game.loser = game.player2
    game.score = (10, 6)

    game.reset()

    assert game.player1.position == (0, 0)
    assert game.player2.position == (3, 3)
    assert game.board[0][0] == 1
    assert game.board[3][3] == 2
    assert game.is_game_over is False
    assert game.winner is None
    assert game.loser is None
    assert game.score == (1, 1)
    assert game.player_turn in (1, 2)


def test_handle_cell_click_adjacent_cell_moves_player():
    game = GameModel("P1", "P2", size=3)
    game.player_turn = 1
    game.player1.position = (0, 0)
    game.player2.position = (2, 2)
    game.board = [
        [1, 0, 0],
        [0, 0, 0],
        [0, 0, 2],
    ]

    controller = GameController(game)

    result = controller.handle_cell_click(0, 1)

    assert result is True
    assert game.player1.position == (0, 1)