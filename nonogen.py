import PIL.Image
import random

from perlin import PerlinNoiseFactory

def gen_random(nonogrid):
    """Generate nonogrid completely at random."""
    nonogrid.clear()

    for row in nonogrid.squares:
        for square in row:
            if random.randint(0,1) == 0:
                square.has_value = True

def gen_perlin(nonogrid):
    """Generate nonogrid using perlin noise."""
    nonogrid.clear()

    # experiment with this, probably.
    arbitrary = 11
    size = arbitrary * len(nonogrid.squares)
    res = 40
    space_range = size//res

    pnf = PerlinNoiseFactory(2, octaves=8, tile=(space_range, space_range))

    step = size // len(nonogrid.squares)
    for x in range(0, size, step):
        for y in range(0, size, step):
            n = pnf(x/res, y/res)

            # Split nice perlin noise into blunt black/white.
            nonogrid.squares[y//step][x//step].has_value = n < 0
