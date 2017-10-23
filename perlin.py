#!/usr/bin/env python3

import random

def gen_rand(top: int):
    """Random numbers up to top."""
    for i in range(top):
        yield random.uniform(-1, 1)

def gen_rand_pair(top: int):
    for i in range(top):
        yield (random.uniform(-1, 1), random.uniform(-1, 1))


class NonoGrid:
    def __init__(self, height, width):
        self.height = height
        self.width = width

        self.squares = [[NonoGrid.Square() for square in range(width)] for row in range(height)]

    def __str__(self):
        out = ""

        max_top_hint_size = 0
        max_left_hint_size = 0
        for item in self.top_hints:
            if len(item) > max_left_hint_size:
                max_left_hint_size = len(item)

        modified_top_hints = []
        for item in self.top_hints:
            if len(item) > max_top_hint_size:
                max_top_hint_size = len(item)

        for item in self.top_hints:
            modified_top_hints.append(([" "] * (max_top_hint_size - len(item))) + item)

        modified_left_hints = []
        for item in self.left_hints:
            modified_left_hints.append(([" "] * (max_top_hint_size - len(item))) + item)

        # Print top hints.
        for i in range(max_top_hint_size):

            # Space out left hints.
            out += "  " * max_left_hint_size

            for col in modified_top_hints:
                out += f"{col[i]} "
            out += "\n"

        for r, row in enumerate(self.squares):

            # Don't forget to put in left hints.
            for lh in modified_left_hints[r]:
                out += f"{lh} "

            for c, square in enumerate(row):
                if c != len(row) - 1:
                    out += f"{square} "
                else:
                    out += f"{square}"

            if r != len(self.squares) - 1:
                out += "\n"

        return out

    def gen_hints(self):
        self.left_hints = [[] for r in range(len(self.squares))]
        self.top_hints = [[] for c in range(len(self.squares[0]))]

        # Generate from squares.
        col_counts = [0] * len(self.squares[0])
        for r, row in enumerate(self.squares):
            row_count = 0
            for c, square in enumerate(row):
                if square.has_value:
                    # Update counters
                    row_count += 1
                    col_counts[c] += 1

                else:
                    # Update tophints.
                    if col_counts[c] > 0:
                        self.top_hints[c].append(col_counts[c])
                        col_counts[c] = 0

                    if row_count > 0:
                        # Update lefthints.
                        self.left_hints[r].append(row_count)
                        row_count = 0

            # Finish row
            if row_count > 0:
                self.left_hints[r].append(row_count)

        # Update tophints.
        for c in range(len(self.squares[0])):
            if col_counts[c] > 0:
                self.top_hints[c].append(col_counts[c])

    class Square:
        def __init__(self):
            self.marked = False
            self.filled = False
            self.has_value = False

        def __str__(self):
            # TODO TMP
            if self.filled or self.has_value:
                return "#"
            elif self.marked:
                return "?"

            return "_"


if __name__ == "__main__":
    grid = NonoGrid(5, 5)
    grid.squares[0][2].has_value = True
    grid.squares[1][2].has_value = True
    grid.squares[2][2].has_value = True
    grid.squares[3][2].has_value = True
    grid.squares[4][2].has_value = True

    grid.squares[2][0].has_value = True
    grid.squares[2][1].has_value = True
    grid.squares[2][2].has_value = True
    grid.squares[2][3].has_value = True
    grid.squares[2][4].has_value = True
    grid.gen_hints()

    print(grid)
