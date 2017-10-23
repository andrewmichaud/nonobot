import PIL.Image
import random

from perlin import PerlinNoiseFactory

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

def gen_perlin(nonogrid):
    """Generate nonogrid using perlin noise."""
    # experiment with this, probably.
    arbitrary = 11
    size = arbitrary * len(nonogrid.squares)
    res = 40
    frames = 20
    frameres = 5
    space_range = size//res
    frame_range = frames//frameres

    pnf = PerlinNoiseFactory(2, octaves=4, tile=(space_range, space_range, frame_range))

    step = size // len(nonogrid.squares)
    for x in range(0, size, step):
        for y in range(0, size, step):
            n = pnf(x/res, y/res)
            if n < 0:
                o = 0
            else:
                o = 1

            nonogrid.squares[y//step][x//step].has_value = o
