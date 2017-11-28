import itertools
import sys
from copy import deepcopy
from os import path

from PIL import Image

HERE = path.abspath(path.dirname(__file__))

OUTLINE_COLOR = (0, 0, 0, 254)
BG_COLOR = (255, 255, 255, 254)

OUTLINE_CUTOFF = 50

IN_NAME = path.join(HERE, "in.jpg")
OUT_NAME = path.join(HERE, "out.png")

class SeamCarveData:
    """Data for seamcarving."""
    def __init__(self):
        self.energy = 0
        self.x = 0
        self.y = 0
        self.parent = None
        self.pixel = None
        self.marked = False


    def __str__(self):
        return str(self.__dict__)

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

        self.shrink_factor = 40

        self.final = Image.new("RGBA", (self.width//self.shrink_factor,
                                        self.height//self.shrink_factor), BG_COLOR)

    def outline(self):
        """Attempt to draw the outline of an image."""
        for y in range(0, self.height, self.shrink_factor):
            for x in range(0, self.width, self.shrink_factor):
                neighbors = get_neighbors(self.in_pixels, x, y, self.height, self.width)
                if should_outline([self.in_pixels[(x, y)]] + neighbors):
                    self.out_pixels[(x, y)] = OUTLINE_COLOR

    def save(self):
        """Save out image."""
        self.out_image.save(self.out_name)
        pixels = self.final.load()
        for y in range(0, self.height-self.shrink_factor, self.shrink_factor):
            for x in range(0, self.width-self.shrink_factor, self.shrink_factor):
                pixels[(x//self.shrink_factor, y//self.shrink_factor)] = self.out_pixels[(x,y)]

        self.final.save("out_final.png")

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

def horiz_seamcarve(in_name=IN_NAME, count=100, show=True):
    """Seamcarve image N times."""
    im = Image.open(in_name)
    im_pixels = im.load()

    # Create copy of out pixels we can manipulate and then save.
    out_pixels = []
    for y in range(im.height):
        row = []
        for x in range(im.width):
            row.append(im_pixels[(x, y)])

        out_pixels.append(row)

    # Carve!
    for i in range(count):
        if i == 0:
            base_energies = create_base_energy(im_pixels, im.height, im.width)
            energies = calculate_energies(im_pixels, base_energies, im.height, im.width)
        else:
            energies = calculate_energies(im_pixels, energies, im.height, im.width)

        # Find start point.
        y = im.height-1
        min_sc_data = energies[y][0]
        for x in range(1, im.width, 1):
            if not energies[y][x].marked and energies[y][x].energy < min_sc_data.energy:
                min_sc_data = energies[y][x]

        sc_data = min_sc_data
        while sc_data is not None:
            # Mark if show is set to true, otherwise delete.
            if show:
                out_pixels[sc_data.y][sc_data.x] = (255, 0, 0, 254)
            else:
                out_pixels[sc_data.y].pop(sc_data.x-i)

            sc_data.marked = True

            sc_data = sc_data.parent

    return out_pixels

def calculate_energies(im_pixels, energies, height, width):
    """(Re)calculate grid of energies for image."""

    # Do the rest.
    for y in range(1, height):
        for x in range(width):
            sc_data = energies[y][x]
            sc_data.x = x
            sc_data.y = y
            sc_data.pixel = im_pixels[(x, y)]

            here_energy = get_energy(im_pixels[(x, y)])

            if x > 0 and not energies[y-1][x-1].marked:
                ul_between = get_energy_between(sc_data, energies[y-1][x-1])
            else:
                ul_between = sys.maxsize

            if energies[y-1][x].marked:
                up_between = sys.maxsize
            else:
                up_between = get_energy_between(sc_data, energies[y-1][x])

            if x < width - 1 and not energies[y-1][x+1].marked:
                ur_between = get_energy_between(sc_data, energies[y-1][x+1])
            else:
                ur_between = sys.maxsize

            min_of = min(ul_between, up_between, ur_between)
            if min_of == sys.maxsize:
                sc_data.energy = min_of
            else:
                sc_data.energy = here_energy + min_of

            if ul_between == min_of:
                sc_data.parent = energies[y-1][x-1]

            elif up_between == min_of:
                sc_data.parent = energies[y-1][x]

            else:
                sc_data.parent = energies[y-1][x+1]

            energies[y][x] = sc_data

    return energies

def create_base_energy(im_pixels, height, width):
    """Create base energies array."""
    energies = [[SeamCarveData() for i in range(width)] for r in range(height)]

    # Do first row.
    for x in range(width):
        sc_data = energies[0][x]
        sc_data.x = x
        sc_data.y = 0
        sc_data.pixel = im_pixels[(x, 0)]
        sc_data.energy = get_energy(im_pixels[(x, 0)])
        energies[0][x] = sc_data

    return energies

def save_pixels(pixels):
    """Save array of pixels to an RGBA image."""
    height = len(pixels)
    width = len(pixels[0])

    out_image = Image.new("RGBA", (width, height), BG_COLOR)

    out_pixels = out_image.load()

    for y in range(height):
        # print(pixels[y][0])
        for x in range(width):
            out_pixels[(x, y)] = pixels[y][x]

    out_image.save("seamcarved_image.png")

# TODO also handle non-RGBA.
def get_energy_between(me, them):
    """Get energy between two SeamCarveDatas (does not include energy of 'me')."""
    # Get max difference in RGB components for two pixels.
    diff = max(list((abs(a-b) for a, b in zip(me.pixel[:3], them.pixel[:3]))))

    return them.energy + diff

# TODO support more than RGBA.
def get_energy(pixel):
    """Get magnitude of pixel, use for energy."""
    return pixel[0] + pixel[1] + pixel[2]
