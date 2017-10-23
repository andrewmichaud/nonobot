#!/usr/bin/env python3

import nono
import nonogen
import random

def gen_rand(top: int):
    """Random numbers up to top."""
    for i in range(top):
        yield random.uniform(-1, 1)

def gen_rand_pair(top: int):
    for i in range(top):
        yield (random.uniform(-1, 1), random.uniform(-1, 1))

if __name__ == "__main__":
    grid = nono.NonoGrid(15)
    nonogen.gen_random(grid)

    grid.gen_hints()

    print(grid)
