import random
import csv
from abc import ABC, abstractmethod
import unittest
import os

class Board:
    def __init__(self):
        self._board = [" " for _ in range(9)]

    def display(self):
        for i in range(3):
            print(" | ".join(self._board[i*3:(i+1)*3]))
            if i < 2:
                print("---------")

    def update(self, position, symbol):
        if self._board[position] == " ":
            self._board[position] = symbol
            return True
        return False

    def is_full(self):
        return " " not in self._board

    def check_winner(self, symbol):
        win_positions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        return any(all(self._board[pos] == symbol for pos in line) for line in win_positions)

    def get_available_moves(self):
        return [i for i, spot in enumerate(self._board) if spot == " "]

class Player(ABC):
    def __init__(self, symbol):
        self.symbol = symbol

    @abstractmethod
    def get_move(self, board):
        pass

class HumanPlayer(Player):
    def __init__(self, symbol, moves=None):
        super().__init__(symbol)
        self._moves = moves or []
        self._move_index = 0

    def get_move(self, board):
        while True:
            if self._move_index < len(self._moves):
                move = self._moves[self._move_index]
                self._move_index += 1
                if move in board.get_available_moves():
                    return move
                else:
                    print(f"Neteisingas ėjimas iš failo: {move}. Įveskite naują ėjimą (0-8):")
            try:
                move = int(input("Tavo ėjimas (0-8): "))
                if move in board.get_available_moves():
                    return move
                else:
                    print("Negalimas ėjimas. Bandyk dar kartą.")
            except ValueError:
                print("Neteisingas įvedimas. Bandyk dar kartą.")

class AIPlayer(Player):
    def get_move(self, board):
        return random.choice(board.get_available_moves())

class PlayerFactory:
    @staticmethod
    def create_player(player_type, symbol, moves=None):
        if player_type == "human":
            return HumanPlayer(symbol, moves)
        elif player_type == "ai":
            return AIPlayer(symbol)
        else:
            raise ValueError("Unknown player type")

class Game:
    def __init__(self, human_moves=None):
        self.board = Board()
        self.players = []
        self.results_file = "game_results.csv"
        self.human_moves = human_moves

    def setup_players(self):
        self.players.append(PlayerFactory.create_player("human", "X", self.human_moves))
        self.players.append(PlayerFactory.create_player("ai", "O"))

    def play(self):
        self.setup_players()
        current_player_idx = 0

        while True:
            self.board.display()
            player = self.players[current_player_idx]
            try:
                move = player.get_move(self.board)
                self.board.update(move, player.symbol)
            except Exception as e:
                print(f"Klaida atliekant ėjimą: {e}")
                self.save_game_result("Error")
                break

            if self.board.check_winner(player.symbol):
                self.board.display()
                print(f"Player '{player.symbol}' wins!")
                self.save_game_result(player.symbol)
                break

            if self.board.is_full():
                self.board.display()
                print("It's a draw!")
                self.save_game_result("Draw")
                break

            current_player_idx = 1 - current_player_idx

    def save_game_result(self, result):
        try:
            with open(self.results_file, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([result])
            print(f"Game result saved: {result}")
        except Exception as e:
            print(f"Could not save game result to file: {e}\nDisplaying result instead: {result}")

    def read_game_results(self):
        if not os.path.exists(self.results_file):
            print("No game results found.")
            return

        print("Previous Game Results:")
        try:
            with open(self.results_file, mode="r", newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:
                        print(f"- {row[0]}")
        except Exception as e:
            print(f"Could not read game results: {e}")

class TestTicTacToe(unittest.TestCase):
    def test_board_update(self):
        b = Board()
        self.assertTrue(b.update(0, "X"))
        self.assertFalse(b.update(0, "O"))

    def test_check_winner(self):
        b = Board()
        for move in [0, 1, 2]:
            b.update(move, "X")
        self.assertTrue(b.check_winner("X"))

    def test_draw(self):
        b = Board()
        draw_moves = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
        for i in range(9):
            b.update(i, draw_moves[i])
        self.assertTrue(b.is_full())
        self.assertFalse(b.check_winner("X"))
        self.assertFalse(b.check_winner("O"))

    def test_available_moves(self):
        b = Board()
        b.update(0, "X")
        b.update(4, "O")
        available = b.get_available_moves()
        self.assertNotIn(0, available)
        self.assertNotIn(4, available)
        self.assertEqual(len(available), 7)

# Entry point simulation
if __name__ == "__main__":
    # Skaityti ėjimus iš failo
    move_file_path = "moves.txt"
    if os.path.exists(move_file_path):
        with open(move_file_path, "r") as f:
            simulated_moves = [int(line.strip()) for line in f.readlines() if line.strip().isdigit()]
    else:
        simulated_moves = [0, 4, 1, 3, 2]  # Atsarginiai ėjimai jei nėra failo

    print("Simulating Tic-Tac-Toe Game from file-based moves")
    game = Game(human_moves=simulated_moves)
    game.play()

    print("\nRunning Tests")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestTicTacToe)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

    print("\nViewing Game History")
    game.read_game_results()
