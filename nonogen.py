import random

def clear(nonogrid):
    """Clear a nonogrid."""
    for row in nonogrid.squares:
        for square in row:
            square.has_value = False

def gen_random(nonogrid):
    """Generate nonogrid completely at random."""
    for row in nonogrid.squares:
        for square in row:
            if random.randint(0,1) == 0:
                square.has_value = True
