import itertools
from os import path

from PIL import Image

HERE = path.abspath(path.dirname(__file__))

OUTLINE_COLOR = (0, 0, 0, 254)
BG_COLOR = (255, 255, 255, 254)

OUTLINE_CUTOFF = 50

IN_NAME = path.join(HERE, "in.jpg")
OUT_NAME = path.join(HERE, "out.png")

class OutlineData:
    """Data for outlining."""
    def __init__(self, in_name=IN_NAME, out_name=OUT_NAME):
        self.in_image = Image.open(in_name)
        self.height = self.in_image.height
        self.width = self.in_image.width

        self.out_image = Image.new("RGBA", (self.width, self.height), BG_COLOR)
        self.out_name = out_name

        self.in_pixels = self.in_image.load()
        self.out_pixels = self.out_image.load()

    def outline(self):
        """Attempt to draw the outline of an image."""

        for y in range(0, self.height, 2):
            for x in range(0, self.width, 2):
                neighbors = get_neighbors(self.in_pixels, x, y, self.height, self.width)
                if should_outline([self.in_pixels[(x, y)]] + neighbors):
                    self.out_pixels[(x, y)] = OUTLINE_COLOR

    def save(self):
        """Save out image."""
        self.out_image.save(self.out_name)

    def get_energies(self):
        energies = [[0] * im.width] * im.height
        print(energies)

def should_outline(to_check):
    """Check if pixel should be outlined based on its neighbors."""
    for pair in itertools.product(to_check, repeat=2):
        if max(list((abs(a-b) for a, b in zip(*pair)))) > OUTLINE_CUTOFF:
            return True

    return False

def get_neighbors(pixels, x, y, height, width):
    """Get neighbors of a pixel."""
    neighbors = []
    if x > 0:
        neighbors.append(pixels[(x-1, y)])

    if x < width - 1:
        neighbors.append(pixels[(x+1, y)])

    if y > 0:
        neighbors.append(pixels[(x, y-1)])

    if y < height - 1:
        neighbors.append(pixels[(x, y+1)])
    # Diagonals?
    return neighbors
