from dataclasses import dataclass
from typing import Optional, Literal

from game import Game
from ai import random_move, alphabeta_best_move


GameMode = Literal["human_vs_computer", "human_vs_human"]
AIType = Literal["random", "alphabeta"]


@dataclass(frozen=True)
class TurnResult:
    status: str
    game_over: bool


class GameController:
    def __init__(self):
        self.n = 3
        self.k = 3
        self.game = Game(n=self.n, k=self.k)

        self.mode: GameMode = "human_vs_computer"
        self.ai_type: AIType = "random"

        # HVC roles
        self.human_symbol = "X"
        self.computer_symbol = "O"

        # HVH roles
        self.player1_symbol = "X"
        self.player2_symbol = "O"

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
        if k is None:
            k = n

        self.n = n
        self.k = k
        self.game = Game(n=self.n, k=self.k)

        self.mode = mode
        self.ai_type = ai_type

        if starter not in ("X", "O"):
            starter = "X"
        self.current_turn_symbol = starter

        if self.mode == "human_vs_computer":
            if human_symbol not in ("X", "O"):
                human_symbol = "X"

            self.human_symbol = human_symbol
            self.computer_symbol = "O" if human_symbol == "X" else "X"

            if self.current_turn_symbol == self.computer_symbol:
                self._computer_play()
                self.current_turn_symbol = self.human_symbol
                return self._evaluate_state(after="Computer starts.")

            return TurnResult(status="Your turn.", game_over=False)

        # human_vs_human
        if player1_symbol not in ("X", "O"):
            player1_symbol = "X"
        if player2_symbol not in ("X", "O"):
            player2_symbol = "O"

        self.player1_symbol = player1_symbol
        self.player2_symbol = player2_symbol

        return TurnResult(status=self._turn_status_hvh(), game_over=False)

    def click(self, idx: int) -> TurnResult:
        if self.is_over():
            return self._evaluate_state(after="Game is over.")

        if self.mode == "human_vs_computer":
            if self.current_turn_symbol != self.human_symbol:
                return TurnResult(status="Wait for your turn.", game_over=False)

            if not self.game.make_move(idx, self.human_symbol):
                return TurnResult(status="Invalid move.", game_over=False)

            if self.is_over():
                return self._evaluate_state(after="")

            self.current_turn_symbol = self.computer_symbol
            self._computer_play()

            if self.is_over():
                return self._evaluate_state(after="")

            self.current_turn_symbol = self.human_symbol
            return TurnResult(status="Your turn.", game_over=False)

        # human_vs_human
        if not self.game.make_move(idx, self.current_turn_symbol):
            return TurnResult(status="Invalid move.", game_over=False)

        if self.is_over():
            return self._evaluate_state(after="")

        self.current_turn_symbol = "O" if self.current_turn_symbol == "X" else "X"
        return TurnResult(status=self._turn_status_hvh(), game_over=False)

    def is_over(self) -> bool:
        return self.game.winner() is not None or self.game.is_draw()

    def _computer_play(self) -> None:
        moves = self.game.available_moves()
        if not moves:
            return

        if self.ai_type == "random":
            idx = random_move(moves)
        else:
            # Alpha-beta with time budget (responsive for any size)
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

    def _evaluate_state(self, after: str) -> TurnResult:
        winner = self.game.winner()
        if winner:
            return TurnResult(status=f"{winner} wins!", game_over=True)

        if self.game.is_draw():
            return TurnResult(status="Draw!", game_over=True)

        if after:
            return TurnResult(status=after, game_over=False)

        if self.mode == "human_vs_computer":
            return TurnResult(status="Your turn.", game_over=False)

        return TurnResult(status=self._turn_status_hvh(), game_over=False)

    def _turn_status_hvh(self) -> str:
        if self.current_turn_symbol == self.player1_symbol:
            return f"Player 1 ({self.player1_symbol})'s turn."
        if self.current_turn_symbol == self.player2_symbol:
            return f"Player 2 ({self.player2_symbol})'s turn."
        return f"{self.current_turn_symbol}'s turn."