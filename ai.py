import random
from typing import List, Optional

def random_move(moves: List[int]) -> Optional[int]:
    """
    Pick a random move from a list of available move indices.
    Returns None if no moves are available.
    """
    return random.choice(moves) if moves else None

