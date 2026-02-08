import random
import time
from typing import List, Optional, Tuple


def random_move(moves: List[int]) -> Optional[int]:
    """Pick a random move from available move indices."""
    return random.choice(moves) if moves else None


def alphabeta_best_move(
    board: List[Optional[str]],
    n: int,
    k: int,
    moves: List[int],
    me: str,
    opponent: str,
    *,
    max_time_sec: float = 0.25,
    max_depth: Optional[int] = None,
) -> Optional[int]:
    """
    Alpha-beta with a heuristic + time cutoff.
    Works for any board size; returns the best move found within time/depth.
    """

    if not moves:
        return None

    # Depth defaults tuned for responsiveness (you can adjust later)
    if max_depth is None:
        # A simple rule of thumb; bigger board => smaller depth
        # Still works for any N; it just searches less on large N.
        if n <= 3:
            max_depth = 9  # effectively full search
        elif n == 4:
            max_depth = 5
        elif n == 5:
            max_depth = 4
        else:
            max_depth = 3

    deadline = time.perf_counter() + max_time_sec

    # Move ordering helps alpha-beta a LOT:
    # center-ish moves first (usually best in grid games).
    ordered_moves = sorted(moves, key=lambda idx: _distance_to_center(idx, n))

    best_move = ordered_moves[0]
    best_score = float("-inf")

    # Root search (maximizing)
    alpha = float("-inf")
    beta = float("inf")

    for mv in ordered_moves:
        if time.perf_counter() > deadline:
            break

        board[mv] = me
        score = _alphabeta(
            board, n, k,
            depth=max_depth - 1,
            alpha=alpha,
            beta=beta,
            maximizing=False,
            me=me,
            opponent=opponent,
            deadline=deadline,
        )
        board[mv] = None

        if score > best_score:
            best_score = score
            best_move = mv

        alpha = max(alpha, best_score)

    return best_move


def _alphabeta(
    board: List[Optional[str]],
    n: int,
    k: int,
    *,
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
    me: str,
    opponent: str,
    deadline: float,
) -> float:
    # Time cutoff
    if time.perf_counter() > deadline:
        return _evaluate(board, n, k, me, opponent)

    w = _winner(board, n, k)
    if w == me:
        return 1_000_000
    if w == opponent:
        return -1_000_000
    if all(v is not None for v in board):
        return 0  # draw

    if depth <= 0:
        return _evaluate(board, n, k, me, opponent)

    moves = [i for i, v in enumerate(board) if v is None]
    moves.sort(key=lambda idx: _distance_to_center(idx, n))

    if maximizing:
        value = float("-inf")
        for mv in moves:
            board[mv] = me
            value = max(
                value,
                _alphabeta(
                    board, n, k,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    maximizing=False,
                    me=me,
                    opponent=opponent,
                    deadline=deadline,
                ),
            )
            board[mv] = None
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = float("inf")
        for mv in moves:
            board[mv] = opponent
            value = min(
                value,
                _alphabeta(
                    board, n, k,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    maximizing=True,
                    me=me,
                    opponent=opponent,
                    deadline=deadline,
                ),
            )
            board[mv] = None
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value


def _evaluate(board: List[Optional[str]], n: int, k: int, me: str, opponent: str) -> float:
    """
    Heuristic: score all length-k segments in rows/cols/diagonals.
    A segment contributes if it's still "open" (contains only me + empty OR opponent + empty).
    Weighted by how close it is to completion.
    """
    my_score = 0.0
    opp_score = 0.0

    for segment in _all_segments(board, n, k):
        m = segment.count(me)
        o = segment.count(opponent)

        if m > 0 and o > 0:
            continue  # blocked segment -> no one benefits

        empties = k - (m + o)
        if empties == k:
            continue  # all empty -> neutral

        # Exponential-ish weights: 1, 10, 100, 1000 ...
        if m > 0 and o == 0:
            my_score += 10 ** (m - 1)
        elif o > 0 and m == 0:
            opp_score += 10 ** (o - 1)

    return my_score - opp_score


def _all_segments(board: List[Optional[str]], n: int, k: int) -> List[List[Optional[str]]]:
    """Return every contiguous length-k segment in all directions."""
    segments: List[List[Optional[str]]] = []

    def at(r: int, c: int) -> Optional[str]:
        return board[r * n + c]

    directions: List[Tuple[int, int]] = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for r in range(n):
        for c in range(n):
            for dr, dc in directions:
                end_r = r + (k - 1) * dr
                end_c = c + (k - 1) * dc
                if not (0 <= end_r < n and 0 <= end_c < n):
                    continue
                seg = [at(r + i * dr, c + i * dc) for i in range(k)]
                segments.append(seg)

    return segments


def _winner(board: List[Optional[str]], n: int, k: int) -> Optional[str]:
    def at(r: int, c: int) -> Optional[str]:
        return board[r * n + c]

    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for r in range(n):
        for c in range(n):
            start = at(r, c)
            if start is None:
                continue
            for dr, dc in directions:
                end_r = r + (k - 1) * dr
                end_c = c + (k - 1) * dc
                if not (0 <= end_r < n and 0 <= end_c < n):
                    continue
                ok = True
                for step in range(1, k):
                    if at(r + step * dr, c + step * dc) != start:
                        ok = False
                        break
                if ok:
                    return start
    return None


def _distance_to_center(idx: int, n: int) -> float:
    r, c = divmod(idx, n)
    center = (n - 1) / 2.0
    return (r - center) ** 2 + (c - center) ** 2

