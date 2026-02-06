from dataclasses import dataclass
from typing import Optional
from game import Game
from ai import random_move

@dataclass(frozen=True)
class TurnResult:
    status: str
    game_over: bool

class GameController:
    def __init__(self, n: int = 3, k: int = 3):
        self.n = n
        self.k = k
        self.game = Game(n=n, k=k)
        self.human = "X"
        self.computer = "O"

    def start(self, human_symbol: str, starter: str = "X") -> TurnResult:
        self.game = Game(n=self.n, k=self.k)  # fresh game
        self.human = human_symbol
        self.computer = "O" if human_symbol == "X" else "X"

        if starter not in ("X", "O"):
            starter = "X"  # fallback to standard

        # If computer is the starter symbol, computer plays first
        if self.computer == starter:
            self._computer_play()
            return self._evaluate_state(after="Computer starts.")
        else:
            return TurnResult(status="Your turn.", game_over=False)

    def human_click(self, idx: int) -> TurnResult:
        # Invalid or game already over -> no change
        if self.is_over():
            return self._evaluate_state(after="Game is over.")
        if not self.game.make_move(idx, self.human):
            return TurnResult(status="Invalid move.", game_over=False)

        # Check end after human
        if self.is_over():
            return self._evaluate_state(after="")

        # Computer plays
        self._computer_play()

        return self._evaluate_state(after="")

    def is_over(self) -> bool:
        return self.game.winner() is not None or self.game.is_draw()

    def _computer_play(self) -> None:
        idx = random_move(self.game.available_moves())
        if idx is not None:
            self.game.make_move(idx, self.computer)

    def _evaluate_state(self, after: str) -> TurnResult:
        w = self.game.winner()
        if w:
            return TurnResult(status=f"{w} wins!", game_over=True)
        if self.game.is_draw():
            return TurnResult(status="Draw!", game_over=True)
        # game continues
        # after is optional; UI can show it briefly, but keep simple:
        return TurnResult(status=("Your turn." if self.human == "X" else "Your turn.") if after == "" else after,
                         game_over=False)