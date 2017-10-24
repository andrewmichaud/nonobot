class NonoGrid:
    def __init__(self, height, width=None):
        self.height = height
        self.width = width
        if self.width is None:
            self.width = height

        self.squares = [[NonoGrid.Square() for s in range(self.width)] for r in range(self.height)]

        self.spacer = 5

        # command-line output implementation details.
        self._left_spacer = "|"
        self._top_spacer = "-"

    def __str__(self):
        out = ""

        # Set up left hints for display (padding!).
        max_left_hint_size = 1
        display_left_hints = []
        for item in self.left_hints:

            new_item = ""
            for hint in item:
                # Space out double-digit hints for legibility.
                if len(str(hint)) > 1:
                    new_item += f"{self._left_spacer}{hint}{self._left_spacer}"
                else:
                    new_item += f"{hint}"

            if len(new_item) > max_left_hint_size:
                max_left_hint_size = len(new_item)

            display_left_hints.append(new_item)

        # Set up top hints for display (also padding!).
        max_top_hint_size = 1
        display_top_hints = []
        for item in self.top_hints:

            new_item = ""
            for hint in item:
                # Space out double-digit hints for legibility.
                if len(str(hint)) > 1:
                    new_item += f"{self._top_spacer}{hint}{self._top_spacer}"
                else:
                    new_item += f"{hint}"

            if len(new_item) > max_top_hint_size:
                max_top_hint_size = len(new_item)

            display_top_hints.append(new_item)

        # Pad top hints (can't do in-line like with left hints).
        for i, item in enumerate(display_top_hints):
            if len(item) < max_top_hint_size:
                display_top_hints[i] = f"{' ' * (max_top_hint_size - len(item))}{item}"

        # Print top hints.
        for i in range(max_top_hint_size):

            # Space out left hints.
            out += f"{' ' * (max_left_hint_size + 1)}"

            for c, col in enumerate(display_top_hints):
                # Space between columns for clarity.
                out += f" {col[i]}"

                # Space every self.spacer columns, also for clarity.
                if c != 0 and (c+1) % self.spacer == 0:
                    out += "  "

            out += "\n"

        # Hint/top row divider.
        # Pad out left hints, do corner, two marks per square, two marks per divider, sub one for
        # the end.
        # Add right corner and newline
        out += (" " * max_left_hint_size) + \
                "+" + \
                "-" * (((len(self.squares) * 2) + (len(self.squares) // self.spacer) * 2) - 1) +\
                "+\n"

        for r, row in enumerate(self.squares):

            # Don't forget to put in left hints.
            for lh in display_left_hints[r]:
                out += lh

            # Divider between left hints and squares.
            out += f"{' ' * (max_left_hint_size - len(display_left_hints[r]))}|"

            for c, square in enumerate(row):

                # Spacing to make things nicer.
                if c != 0 and (c+1) % self.spacer == 0:
                    out += f" {square} |"
                else:
                    out += f" {square}"

            if r != len(self.squares) - 1:
                out += "\n"

            # Add divider rows between squares.
            if (r+1) % self.spacer == 0 and r > 0 and r < len(self.squares) - 1:
                out += (" " * max_left_hint_size) + \
                        "|" + \
                        "-" * (((len(self.squares)*2) + (len(self.squares)//self.spacer)*2) - 1) +\
                        "|\n"

        # Hint/top row divider.
        # Same as top.
        out += "\n"
        out += (" " * max_left_hint_size) + \
                "+" + \
                "-" * (((len(self.squares) * 2) + (len(self.squares) // self.spacer) * 2) - 1) +\
                "+\n"

        return out

    def clear(self):
        """Clear grid."""
        for row in self.squares:
            for square in row:
                square.clear()

    def gen_hints(self):
        """Generate nonogram hints."""
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

            # Handle empty row.
            if self.left_hints[r] == []:
                self.left_hints[r] = [0]

        # Handle last column.
        for c in range(len(self.squares[0])):
            if col_counts[c] > 0:
                self.top_hints[c].append(col_counts[c])

            # Handle empty columns.
            if self.top_hints[c] == []:
                self.top_hints[c] = [0]

        # Blank out empty rows.
        for r, row in enumerate(self.squares):
            for c, square in enumerate(self.squares[r]):
                if 0 in self.left_hints[r] or 0 in self.top_hints[c]:
                    square.denied = True

    class Square:
        def __init__(self):
            # User indicators.
            self.filled = False
            self.marked = False
            self.denied = False

            # True info.
            self.has_value = False

        def __str__(self):
            if self.filled:
                return "#"
            elif self.marked:
                return "?"
            elif self.denied:
                return "X"

            return "_"

        def clear(self):
            self.filled = False
            self.marked = False
            self.denied = False
            self.has_value = False
