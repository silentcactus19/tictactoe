from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Game:
    n: int = 3
    k: int = 3
    board: List[Optional[str]] = None

    def __post_init__(self):
        if self.board is None:
            self.board = [None] * (self.n * self.n)

    def reset(self):
        self.board = [None] * (self.n * self.n)

    def available_moves(self):
        return [i for i, v in enumerate(self.board) if v is None]

    def make_move(self, idx: int, symbol: str) -> bool:
        if idx < 0 or idx >= len(self.board):
            return False
        if self.board[idx] is not None:
            return False
        self.board[idx] = symbol
        return True

    def winner(self) -> Optional[str]:
        n, k = self.n, self.k

        def at(r, c):
            return self.board[r * n + c]

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for r in range(n):
            for c in range(n):
                start = at(r, c)
                if start is None:
                    continue
                for dr, dc in directions:
                    er, ec = r + (k - 1) * dr, c + (k - 1) * dc
                    if not (0 <= er < n and 0 <= ec < n):
                        continue
                    if all(at(r + i * dr, c + i * dc) == start for i in range(1, k)):
                        return start
        return None

    def is_draw(self) -> bool:
        return self.winner() is None and all(v is not None for v in self.board)