#!/usr/bin/env python3

import nono
import nonogen
import random

if __name__ == "__main__":
    grid = nono.NonoGrid(random.choice(range(5, 20)), random.choice(range(5,20)))
    # nonogen.gen_random(grid)
    #
    # grid.gen_hints()
    #
    # print("random generation: ")
    # print(grid)

    nonogen.gen_perlin(grid)

    grid.gen_hints()

    print(f"{grid.type} \n{grid}")

    grid.to_picture("nonogrid.jpg")
    grid.to_picture("nonogrid_solved.jpg", has_value_color="orange")
