from dataclasses import dataclass
from typing import Optional, Literal

from game import Game
from ai import random_move, alphabeta_best_move

# Supported game modes:
# - human_vs_computer: one player clicks, computer responds automatically
# - human_vs_human: two players use the same computer and alternate clicks
GameMode = Literal["human_vs_computer", "human_vs_human"]

# Supported agent types for the computer player
AIType = Literal["random", "alphabeta"]


@dataclass(frozen=True)
class TurnResult:
    """
    Returned after any action that may change the game (start, click).

    status:    text to display in the UI (turn, win, draw, etc.)
    game_over: True if the game is finished (win or draw)
    """
    status: str
    game_over: bool


class GameController:
    def __init__(self):
        # Default game configuration
        self.n = 3
        self.k = 3  # winning condition: align K
        self.game = Game(n=self.n, k=self.k)

        # Default mode / AI
        self.mode: GameMode = "human_vs_computer"
        self.ai_type: AIType = "random"

        # Human vs Computer roles:
        self.human_symbol = "X"
        self.computer_symbol = "O"

        # Human vs Human roles:
        self.player1_symbol = "X"
        self.player2_symbol = "O"

        # Tracks whose turn it is (either "X" or "O")
        self.current_turn_symbol = "X"

    def start(
        self,
        *,
        mode: GameMode,
        n: int = 3,
        k: Optional[int] = None,
        starter: str = "X",
        # HVC
        human_symbol: str = "X",
        ai_type: AIType = "random",
        # HVH
        player1_symbol: str = "X",
        player2_symbol: str = "O",
    ) -> TurnResult:
        """
        Start (or restart) a game with the provided settings.

        This method:
        - creates a fresh Game instance
        - stores the selected mode and symbols
        - sets who starts
        - if the computer starts, it immediately plays a move
        """
        # If K is not provided, we default to "align N"
        if k is None:
            k = n

        # Create a new game instance for the selected size/rules
        self.n = n
        self.k = k
        self.game = Game(n=self.n, k=self.k)

        # Store configuration
        self.mode = mode
        self.ai_type = ai_type

        # Validate starter symbol
        if starter not in ("X", "O"):
            starter = "X"
        self.current_turn_symbol = starter

        # Human vs Computer
        if self.mode == "human_vs_computer":
            # Validate human symbol
            if human_symbol not in ("X", "O"):
                human_symbol = "X"

            # Assign roles
            self.human_symbol = human_symbol
            self.computer_symbol = "O" if human_symbol == "X" else "X"

            # If computer starts, it plays immediately
            if self.current_turn_symbol == self.computer_symbol:
                self.computer_play()
                # After computer move, it's human's turn
                self.current_turn_symbol = self.human_symbol
                return self.evaluate_state(after="Computer starts.")

            return TurnResult(status="Your turn.", game_over=False)

        # Human vs Human
        # Validate player symbols
        if player1_symbol not in ("X", "O"):
            player1_symbol = "X"
        if player2_symbol not in ("X", "O"):
            player2_symbol = "O"

        self.player1_symbol = player1_symbol
        self.player2_symbol = player2_symbol

        # UI validation ensures symbols differ; controller assumes they are valid here.
        return TurnResult(status=self.turn_status_hvh(), game_over=False)

    def click(self, idx: int) -> TurnResult:
        """
        Handle a click on a cell index (0..N*N-1).

        Depending on the mode:
        - HVC: apply human move -> maybe end -> computer move -> maybe end -> return status
        - HVH: apply current player's move -> switch turn -> return status
        """
        # If the game is already done, ignore further moves
        if self.is_over():
            return self.evaluate_state(after="Game is over.")

        # Human vs Computer
        if self.mode == "human_vs_computer":
            # Prevent clicking when it's not the human's turn
            if self.current_turn_symbol != self.human_symbol:
                return TurnResult(status="Wait for your turn.", game_over=False)

            # Try to apply the human move
            if not self.game.make_move(idx, self.human_symbol):
                return TurnResult(status="Invalid move.", game_over=False)

            # If that move ended the game, return final state
            if self.is_over():
                return self.evaluate_state(after="")

            # Computer plays
            self.current_turn_symbol = self.computer_symbol
            self.computer_play()

            # If the computer ended the game, return final state
            if self.is_over():
                return self.evaluate_state(after="")

            # Otherwise back to human
            self.current_turn_symbol = self.human_symbol
            return TurnResult(status="Your turn.", game_over=False)

        # Human vs Human
        # Place the symbol of the current player
        if not self.game.make_move(idx, self.current_turn_symbol):
            return TurnResult(status="Invalid move.", game_over=False)

        if self.is_over():
            return self.evaluate_state(after="")

        # Toggle turn (X <-> O)
        self.current_turn_symbol = "O" if self.current_turn_symbol == "X" else "X"
        return TurnResult(status=self.turn_status_hvh(), game_over=False)

    def is_over(self) -> bool:
        """
        Returns True if the game has ended (win or draw).
        """
        return self.game.winner() is not None or self.game.is_draw()

    def computer_play(self) -> None:
        """
        Perform one computer move (if available).
        AI selection:
        - random: pick any available cell
        - alphabeta: choose best move under time/depth constraints
        """
        moves = self.game.available_moves()
        if not moves:
            return

        if self.ai_type == "random":
            idx = random_move(moves)
        else:
            # Alpha-beta uses a heuristic + time budget to stay responsive on larger boards.
            idx = alphabeta_best_move(
                board=self.game.board,
                n=self.game.n,
                k=self.game.k,
                moves=moves,
                me=self.computer_symbol,
                opponent=self.human_symbol,
                max_time_sec=0.25,
                max_depth=None,
            )

        if idx is not None:
            self.game.make_move(idx, self.computer_symbol)

    def evaluate_state(self, after: str) -> TurnResult:
        """
        Convert the current game state into a UI-friendly TurnResult.

        Priority:
        1) Winner
        2) Draw
        3) Otherwise use 'after' message if provided
        4) Otherwise compute a default "whose turn" message
        """
        winner = self.game.winner()
        if winner:
            return TurnResult(status=f"{winner} wins!", game_over=True)

        if self.game.is_draw():
            return TurnResult(status="Draw!", game_over=True)

        if after:
            return TurnResult(status=after, game_over=False)

        if self.mode == "human_vs_computer":
            return TurnResult(status="Your turn.", game_over=False)

        return TurnResult(status=self.turn_status_hvh(), game_over=False)

    def turn_status_hvh(self) -> str:
        """
        Return a readable status message for Human vs Human mode.
        """
        if self.current_turn_symbol == self.player1_symbol:
            return f"Player 1 ({self.player1_symbol})'s turn."
        if self.current_turn_symbol == self.player2_symbol:
            return f"Player 2 ({self.player2_symbol})'s turn."
        return f"{self.current_turn_symbol}'s turn."