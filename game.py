"""
This file contains the *pure* game rules and state for Tic-Tac-Toe.
- Store the board state
- Validate and apply moves
- Detect wins and draws
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Game:
    """
    Notes:
        - The board is stored as a 1D list for simplicity.
        - Index mapping: index = row * n + col
    """
    n: int = 3
    k: int = 3

    def __post_init__(self):
        if self.n < 3:
            raise ValueError("Board size n must be >= 3")
        if self.k < 3 or self.k > self.n:
            raise ValueError("Win condition k must satisfy 3 <= k <= n")

        # Initialize an empty board (None = empty cell)
        self.board: List[Optional[str]] = [None] * (self.n * self.n)

    # Basic operations
    def reset(self) -> None:
        """Clear the board so a new game can start."""
        for i in range(len(self.board)):
            self.board[i] = None

    def available_moves(self) -> List[int]:
        """
        Return a list of indices that are still empty.
        """
        return [i for i, v in enumerate(self.board) if v is None]

    def make_move(self, idx: int, symbol: str) -> bool:
        """
        Returns:
            True if the move was applied
            False if the move is invalid (out of range, already occupied, invalid symbol)
        """
        if symbol not in ("X", "O"):
            return False
        if idx < 0 or idx >= self.n * self.n:
            return False
        if self.board[idx] is not None:
            return False

        self.board[idx] = symbol
        return True

    # End state detection
    def is_draw(self) -> bool:
        """
        A draw means: the board is full AND there is no winner.
        """
        return all(v is not None for v in self.board) and self.winner() is None

    def winner(self) -> Optional[str]:
        """
        Return:
            "X" if X has a winning alignment
            "O" if O has a winning alignment
            None if there is no winner
        """
        n, k = self.n, self.k

        def at(r: int, c: int) -> Optional[str]:
            return self.board[r * n + c]

        # Directions: right, down, down-right, down-left
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for r in range(n):
            for c in range(n):
                start = at(r, c)
                if start is None:
                    continue

                for dr, dc in directions:
                    end_r = r + (k - 1) * dr
                    end_c = c + (k - 1) * dc

                    # Segment must remain inside board boundaries
                    if not (0 <= end_r < n and 0 <= end_c < n):
                        continue

                    # Check if all K cells in that direction match the start
                    ok = True
                    for step in range(1, k):
                        if at(r + step * dr, c + step * dc) != start:
                            ok = False
                            break

                    if ok:
                        return start

        return None

    # Debug helpers (optional but handy)
    def __str__(self) -> str:
        """
        Text representation of the board for debugging.
        Empty cells are shown as '.'.
        """
        out = []
        for r in range(self.n):
            row = []
            for c in range(self.n):
                v = self.board[r * self.n + c]
                row.append(v if v is not None else ".")
            out.append(" ".join(row))
        return "\n".join(out)