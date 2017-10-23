class NonoGrid:
    def __init__(self, height, width=None):
        self.height = height
        if width is None:
            self.width = height
        else:
            self.width = width

        self.squares = [[NonoGrid.Square() for square in range(self.width)] for row in
                        range(self.height)]

    def __str__(self):
        out = ""

        # Calculate the amount of padding we need for each hint row and each hint column
        # Also calculate additional padding for double-digit numbers.

        # Calculate left.
        max_left_hint_size = 0
        max_left_hint_digit = 1
        for item in self.left_hints:
            if len(item) > max_left_hint_size:
                max_left_hint_size = len(item)

            for hint in item:
                if len(str(hint)) > max_left_hint_digit:
                    max_left_hint_digit = len(str(hint))

        modified_left_hints = []
        for item in self.left_hints:
            modified_left_hints.append(([" "] * (max_left_hint_size - len(item))) + item)


        # Calculate top.
        max_top_hint_size = 0
        max_top_hint_digit = 1
        modified_top_hints = []
        for item in self.top_hints:
            if len(item) > max_top_hint_size:
                max_top_hint_size = len(item)

            if len(str(item)) > max_top_hint_digit:
                max_top_hint_digit = len(str(item))

        for item in self.top_hints:
            modified_top_hints.append(([" "] * (max_top_hint_size - len(item))) + item)

        # Print top hints.
        for i in range(max_top_hint_size):

            # Space out left hints.
            out += "  " * max_left_hint_size

            for c, col in enumerate(modified_top_hints):

                # Spacing to make things nicer.
                if c % 5 == 0 and c > 0:
                    out += " "

                out += f"{col[i]} "

            out += "\n"

        for r, row in enumerate(self.squares):

            # Don't forget to put in left hints.
            for lh in modified_left_hints[r]:
                out += f"{lh}" + " "

            for c, square in enumerate(row):

                # Spacing to make things nicer.
                if (c+1) % 5 == 0 and c > 0:
                    out += f"{square}  "
                elif c != len(row) - 1:
                    out += f"{square} "
                else:
                    out += f"{square}"

            if r != len(self.squares) - 1:
                out += "\n"

            if (r+1) % 5 == 0 and r > 0 and r < len(self.squares) - 1:
                out += "\n"

        return out

    def gen_hints(self):
        self.left_hints = [[] for r in range(len(self.squares))]
        self.top_hints = [[] for c in range(len(self.squares[0]))]

        # Generate hints from squares.
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

        # Handle last column.
        for c in range(len(self.squares[0])):
            if col_counts[c] > 0:
                self.top_hints[c].append(col_counts[c])

    class Square:
        def __init__(self):
            self.marked = False
            self.filled = False
            self.has_value = False

        def __str__(self):
            if self.filled:
                return "#"
            elif self.marked:
                return "?"

            return "_"

        def debug_print(self):
            if self.has_value:
                return "#"

