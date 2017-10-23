#!/usr/bin/env python3

import nono
import nonogen
import perlin

if __name__ == "__main__":
    grid = nono.NonoGrid(15)
    nonogen.gen_random(grid)

    grid.gen_hints()

    print("random generation: ")
    print(grid)

    nonogen.gen_perlin(grid)

    grid.gen_hints()

    print("perlin noise generation: ")
    print(grid)
