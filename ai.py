"""
ai.py

Two AI strategies are implemented:
1) Random AI (baseline, required by the assignment)
2) Smart AI using Alpha-Beta pruning with a heuristic evaluation function
"""

import time
import random
from typing import List, Optional


# Random AI

def random_move(moves: List[int]) -> Optional[int]:
    """
    Pick a random move from the list of available moves.
    Parameters:
        moves: list of available cell indices

    Returns:
        A randomly chosen move, or None if no moves are available
    """
    if not moves:
        return None
    return random.choice(moves)


# Alpha-Beta AI (Smart AI)

def alphabeta_best_move(
    *,
    board: List[Optional[str]],
    n: int,
    k: int,
    moves: List[int],
    me: str,
    opponent: str,
    max_time_sec: float = 0.25,
    max_depth: Optional[int] = None,
) -> Optional[int]:
    """
    Compute the best move using Alpha-Beta pruning.
    - time-bounded (never freezes the UI)
    - heuristic-based (can evaluate non-terminal positions)

    Parameters:
        board: current board as a flat list
        n: board size (N)
        k: win condition (align K)
        moves: list of currently available moves
        max_time_sec: time budget for the search
        max_depth: optional depth limit (None = adaptive)

    Returns:
        Index of the chosen move, or None if no move is found
    """
    start_time = time.time()

    # Default depth heuristic:
    # - small boards can be searched deeper
    # - larger boards require shallower searches
    if max_depth is None:
        if n <= 3:
            max_depth = 9
        elif n == 4:
            max_depth = 6
        elif n == 5:
            max_depth = 4
        else:
            max_depth = 3

    best_score = float("-inf")
    best_move = None

    # Move ordering improves alpha-beta pruning efficiency.
    # Center moves are generally stronger in Tic-Tac-Toe-like games.
    ordered_moves = sorted(moves, key=lambda m: distance_to_center(m, n))

    for move in ordered_moves:
        if time.time() - start_time > max_time_sec:
            break

        new_board = board.copy()
        new_board[move] = me

        score = alphabeta(
            board=new_board,
            n=n,
            k=k,
            depth=max_depth - 1,
            alpha=float("-inf"),
            beta=float("inf"),
            maximizing=False,
            me=me,
            opponent=opponent,
            start_time=start_time,
            max_time_sec=max_time_sec,
        )

        if score > best_score:
            best_score = score
            best_move = move

    return best_move


# Alpha-Beta recursion

def alphabeta(
    *,
    board: List[Optional[str]],
    n: int,
    k: int,
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
    me: str,
    opponent: str,
    start_time: float,
    max_time_sec: float,
) -> float:
    """
    Recursive Alpha-Beta search.

    Stops when:
    - a terminal state is reached (win/draw)
    - depth reaches 0
    - time budget is exceeded

    Returns:
        A numeric evaluation of the position
    """
    # Time cutoff: guarantees responsiveness
    if time.time() - start_time > max_time_sec:
        return heuristic(board, n, k, me, opponent)

    winner = check_winner(board, n, k)
    if winner == me:
        return 1_000_000
    if winner == opponent:
        return -1_000_000
    if is_draw(board):
        return 0

    if depth == 0:
        return heuristic(board, n, k, me, opponent)

    moves = available_moves(board)

    if maximizing:
        value = float("-inf")
        for move in moves:
            new_board = board.copy()
            new_board[move] = me

            value = max(
                value,
                alphabeta(
                    board=new_board,
                    n=n,
                    k=k,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    maximizing=False,
                    me=me,
                    opponent=opponent,
                    start_time=start_time,
                    max_time_sec=max_time_sec,
                ),
            )
            alpha = max(alpha, value)
            if beta <= alpha:
                break  # Beta cut-off
        return value

    else:
        value = float("inf")
        for move in moves:
            new_board = board.copy()
            new_board[move] = opponent

            value = min(
                value,
                alphabeta(
                    board=new_board,
                    n=n,
                    k=k,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    maximizing=True,
                    me=me,
                    opponent=opponent,
                    start_time=start_time,
                    max_time_sec=max_time_sec,
                ),
            )
            beta = min(beta, value)
            if beta <= alpha:
                break  # Alpha cut-off
        return value


# Heuristic evaluation

def heuristic(board: List[Optional[str]], n: int, k: int, me: str, opponent: str) -> float:
    """
    Heuristic evaluation function.

    Strategy:
    - Look at every possible K-length line
    - Ignore blocked lines (containing both players)
    - Score lines exponentially based on how close they are to completion

    Returns:
        Positive score if position favors AI,
        Negative score if it favors the opponent
    """
    score = 0

    for line in generate_lines(board, n, k):
        me_count = line.count(me)
        opp_count = line.count(opponent)

        # Blocked line → no value
        if me_count > 0 and opp_count > 0:
            continue

        if me_count > 0:
            score += 10 ** (me_count - 1)
        elif opp_count > 0:
            score -= 10 ** (opp_count - 1)

    return score


# Utility functions (pure, no side effects)

def available_moves(board: List[Optional[str]]) -> List[int]:
    """Return indices of all empty cells."""
    return [i for i, v in enumerate(board) if v is None]


def is_draw(board: List[Optional[str]]) -> bool:
    """Return True if the board is full."""
    return all(v is not None for v in board)


def distance_to_center(idx: int, n: int) -> float:
    """Used for move ordering: center-first improves pruning."""
    r, c = divmod(idx, n)
    center = (n - 1) / 2
    return abs(r - center) + abs(c - center)


def generate_lines(board: List[Optional[str]], n: int, k: int):
    """
    Yield all possible K-length segments (rows, columns, diagonals).
    """
    # Rows
    for r in range(n):
        for c in range(n - k + 1):
            yield [board[r * n + c + i] for i in range(k)]

    # Columns
    for c in range(n):
        for r in range(n - k + 1):
            yield [board[(r + i) * n + c] for i in range(k)]

    # Diagonal ↘
    for r in range(n - k + 1):
        for c in range(n - k + 1):
            yield [board[(r + i) * n + (c + i)] for i in range(k)]

    # Diagonal ↙
    for r in range(n - k + 1):
        for c in range(k - 1, n):
            yield [board[(r + i) * n + (c - i)] for i in range(k)]


def check_winner(board: List[Optional[str]], n: int, k: int) -> Optional[str]:
    """
    Return the winning symbol if a player has won, else None.
    """
    for line in generate_lines(board, n, k):
        if line[0] is not None and all(v == line[0] for v in line):
            return line[0]
    return None