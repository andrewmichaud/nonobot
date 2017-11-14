import base64
import json
import zlib
from datetime import datetime
from os import path

from PIL import Image, ImageDraw, ImageFont

HERE = path.abspath(path.dirname(__file__))


class NonoGrid:
    def __init__(self, height, width=None):
        self.height = height
        self.width = width
        if self.width is None:
            self.width = height

        self.squares = [[NonoGrid.Square() for s in range(self.width)] for r in range(self.height)]

        self.spacer = 5

        # command-line output implementation details.
        self._vert_spacer = "│"
        self._horiz_spacer = "─"
        self._ul_corner = "┌"
        self._ll_corner = "└"
        self._ur_corner = "┐"
        self._lr_corner = "┘"

        self.type = None

    def __str__(self):
        out = ""

        # Print top hints.
        for i in range(self.max_top_hint_size):

            # Space out left hints.
            out += f"{' ' * (self.max_left_hint_size + 1)}"

            for c, col in enumerate(self.display_top_hints):
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
        out += (" " * self.max_left_hint_size) + \
                f"{self._ul_corner}" + self._horiz_spacer * (self.grid_size()-2)+ f"{self._ur_corner}\n"

        for r, row in enumerate(self.squares):

            # Don't forget to put in left hints.
            for lh in self.display_left_hints[r]:
                out += lh

            # Divider between left hints and squares.
            out += f"{' ' * (self.max_left_hint_size - len(self.display_left_hints[r]))}{self._vert_spacer}"

            for c, square in enumerate(row):

                # Spacing to make things nicer.
                if c == len(row)-1 or (c != 0 and (c+1) % self.spacer == 0):
                    out += f" {square} {self._vert_spacer}"
                else:
                    out += f" {square}"

            if r != self.height - 1:
                out += "\n"

            # Add divider rows between squares.
            if (r+1) % self.spacer == 0 and r > 0 and r < self.height - 1:
                out += " " * self.max_left_hint_size +\
                        "├" + self._horiz_spacer * (self.grid_size()-2) + "┤\n"

        # Hint/top row divider.
        # Similar to top.
        out += "\n"
        out += (" " * self.max_left_hint_size) + \
                self._ll_corner + self._horiz_spacer * (self.grid_size()-2) + f"{self._lr_corner}\n"

        return out

    def grid_size(self, dim=None, square_size=1, spacer_size=1, meta_spacer_size=2):
        """Do the obnoxious calculation to get the correct width or height for grid."""
        if dim is None:
            dim = self.width

        return (dim * square_size) +\
                ((dim-1) * spacer_size) +\
                (((dim//self.spacer) + 1) * meta_spacer_size) +\
                (0 if dim % self.spacer == 0 else 1 * meta_spacer_size)


    def to_picture(self, filename=None, has_value_color="white"):
        """Print grid to picture."""

        SQUARE_SIZE = 50
        HINT_SPACE_SIZE = 30
        SQUARE_DIVIDER_SIZE = 5
        SPACER_SIZE = 10
        FONT_SIZE = 45

        EMPTY = (255, 255, 255)
        BG_GREY = (0, 0, 0)
        DIVIDER = BG_GREY
        PREBLOCKED_GREY = (200, 209, 211)

        if filename is None:
            filename = path.join(path.abspath(path.dirname(__file__)), "nonogrid.jpg")

        left_hint_width = SQUARE_SIZE * (len(self.display_left_hints[0]))
        top_hint_height = SQUARE_SIZE * (len(self.display_top_hints[0]))

        width = left_hint_width + self.grid_size(dim=self.width, square_size=SQUARE_SIZE,
                                                 spacer_size=SPACER_SIZE,
                                                 meta_spacer_size=SQUARE_DIVIDER_SIZE)

        height = top_hint_height + self.grid_size(dim=self.height, square_size=SQUARE_SIZE,
                                                  spacer_size=SPACER_SIZE,
                                                  meta_spacer_size=SQUARE_DIVIDER_SIZE)

        im = Image.new("RGB", (width, height), BG_GREY)

        dr = ImageDraw.Draw(im)

        fnt = ImageFont.truetype(path.join(HERE, "FreeMono.ttf"), FONT_SIZE)

        # PIL coordinates start at the upper left corner.

        y0 = SQUARE_DIVIDER_SIZE

        # Print top hints.
        for i in range(len(self.display_top_hints[0])):

            # Space out left hints.
            x0 = (self.max_left_hint_size * HINT_SPACE_SIZE) + SQUARE_DIVIDER_SIZE + (SQUARE_SIZE * 0.5)

            for hi, item in enumerate(list(map(lambda x: x[i], self.display_top_hints))):
                dr.text((x0, y0), item, font=fnt, fill=(255,255,255,255))
                x0 += SQUARE_SIZE + SQUARE_DIVIDER_SIZE

                if (hi+1) % 5 == 0:
                    x0 += SPACER_SIZE

            y0 += HINT_SPACE_SIZE * 1.5

        # Handle squares (and left hints).
        for r, row in enumerate(self.squares):

            x0 = SQUARE_DIVIDER_SIZE
            for lh, hint in enumerate(self.display_left_hints[r]):
                dr.text((x0, y0), hint, font=fnt, fill=(255,255,255,255))
                x0 += HINT_SPACE_SIZE

            # Space hints from squares.
            x0 += SPACER_SIZE

            for c, square in enumerate(row):
                if square.has_value:
                    fill = has_value_color
                elif self.top_hints[c] == [0] or self.left_hints[r] == [0]:
                    fill = PREBLOCKED_GREY
                else:
                    fill = EMPTY

                dr.rectangle(xy=[(x0, y0), (x0+SQUARE_SIZE, y0+SQUARE_SIZE)],
                                              fill=fill)

                x0 += SQUARE_SIZE + SQUARE_DIVIDER_SIZE

                # Divide into sets of five.
                if (c+1) % 5 == 0:
                    x0 += SPACER_SIZE

            y0 += SQUARE_SIZE + SQUARE_DIVIDER_SIZE

            # Divide into sets of five.
            if (r+1) % 5 == 0:
                y0 += SPACER_SIZE

        im.save(filename)

    def clear(self):
        """Clear grid."""
        for row in self.squares:
            for square in row:
                square.clear()

    def set_hints_for_display(self):
        """Put padding in hints so they can be printed."""
        # Set up left hints for display (padding!).
        self.max_left_hint_size = 1
        self.display_left_hints = []
        for item in self.left_hints:

            new_item = ""
            for hint in item:
                # Space out double-digit hints for legibility.
                if len(str(hint)) > 1:
                    new_item += f"{self._vert_spacer}{hint}{self._vert_spacer}"
                else:
                    new_item += f"{hint}"

            if len(new_item) > self.max_left_hint_size:
                self.max_left_hint_size = len(new_item)

            self.display_left_hints.append(new_item)

        # Set up top hints for display (also padding!).
        self.max_top_hint_size = 1
        self.display_top_hints = []
        for item in self.top_hints:

            new_item = ""
            for hint in item:
                # Space out double-digit hints for legibility.
                if len(str(hint)) > 1:
                    new_item += f"{self._horiz_spacer}{hint}{self._horiz_spacer}"
                else:
                    new_item += f"{hint}"

            if len(new_item) > self.max_top_hint_size:
                self.max_top_hint_size = len(new_item)

            self.display_top_hints.append(new_item)

        # Pad left hints.
        for i, item in enumerate(self.display_left_hints):
            if len(item) < self.max_left_hint_size:
                self.display_left_hints[i] = f"{' ' * (self.max_left_hint_size - len(item))}{item}"

        # Pad top hints.
        for i, item in enumerate(self.display_top_hints):
            if len(item) < self.max_top_hint_size:
                self.display_top_hints[i] = f"{' ' * (self.max_top_hint_size - len(item))}{item}"

    def gen_hints(self):
        """Generate nonogram hints."""
        self.left_hints = [[] for r in range(self.height)]
        self.top_hints = [[] for c in range(self.width)]

        # Generate hints from squares.
        col_counts = [0] * self.width
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
        for c in range(self.width):
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


        self.set_hints_for_display()

    def encode(self):
        """Encode bot squares to a condensed form for easy tweeting/sharing."""
        binary_squares = []
        for row in self.squares:
            for square in row:
                binary_squares.append("1" if square.has_value else "0")

        squares_binary = "".join(binary_squares)
        squares_hex = "{:0x}".format(int(squares_binary, 2))

        data = {"height": self.height, "width": self.width, "squares": squares_hex}
        data_compressed = zlib.compress(str(data).encode())
        data_encoded = base64.urlsafe_b64encode(data_compressed).decode()

        return f"{data_encoded}"

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


def decode(nonostring):
    """Restore NonoGrid from condensed form."""

    decoded = base64.urlsafe_b64decode(nonostring)
    uncompressed = zlib.decompress(decoded).decode().replace("'", '"')
    redict = json.loads(uncompressed)
    height = redict["height"]
    width = redict["width"]
    size = height * width
    unpadded_binary = redict["squares"]

    grid = NonoGrid(height, width)

    unpadded_binary = str(bin(int(unpadded_binary, 16))[2:])
    padded_binary = unpadded_binary.zfill(size)

    squares = []
    row = []
    for c, char in enumerate(padded_binary):

        if c % width == 0 and c != 0:
            squares.append(row)
            row = []

        square = NonoGrid.Square()
        if char == '1':
            square.has_value = True

        row.append(square)

    squares.append(row)

    grid.squares = squares

    return grid
