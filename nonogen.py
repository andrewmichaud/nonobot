import random

from perlin import PerlinNoiseFactory

def gen_random(nonogrid):
    """Generate nonogrid completely at random."""
    nonogrid.clear()

    for row in nonogrid.squares:
        for square in row:
            if random.randint(0, 1) == 0:
                square.has_value = True

    nonogrid.type = "Random"

def gen_perlin(nonogrid):
    """Generate nonogrid using perlin noise."""
    nonogrid.clear()

    # experiment with this, probably.
    arbitrary = 11
    x_size = arbitrary * len(nonogrid.squares[0])
    y_size = arbitrary * len(nonogrid.squares)
    res = 40
    x_space_range = x_size//res
    y_space_range = y_size//res

    pnf = PerlinNoiseFactory(2, octaves=8, tile=(x_space_range, y_space_range))

    x_step = x_size // len(nonogrid.squares[0])
    y_step = y_size // len(nonogrid.squares)
    for x in range(0, x_size, x_step):
        for y in range(0, y_size, y_step):
            n = pnf(x/res, y/res)

            # Split nice perlin noise into blunt black/white.
            nonogrid.squares[y//x_step][x//y_step].has_value = n < 0

    nonogrid.type = "Perlin"
