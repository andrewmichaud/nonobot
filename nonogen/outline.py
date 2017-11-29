import collections
import itertools
import random
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
        self.rel_x = 0
        self.parent_choices = []
        self.parent = None
        self.children = []
        self.pixel = None
        self.marked = False

    def __str__(self):
        return str(self.__dict__)

    def __lt__(self, other):
        return self.energy < other.energy

    def __le__(self, other):
        return self.energy <= other.energy

    def __gt__(self, other):
        return self.energy > other.energy

    def __ge__(self, other):
        return self.energy >= other.energy

    def __eq__(self, other):
        return self.energy == other.energy

    def __ne__(self, other):
        return self.energy != other.energy

    def fix_rel_x(self):
        """Fix rel x."""
        self.rel_x -= 1

        return self

    def choose_parent(self):
        """Choose parent and update my energy."""
        self.energy = get_energy(self.pixel)

        self.parent = random.choice(self.parent_choices)
        min_energy = self.parent.energy
        for choice in self.parent_choices:
            if choice.energy < min_energy:
                min_energy = choice.energy
                self.parent = choice

        if min_energy < sys.maxsize - self.energy:
            self.energy = min_energy + self.energy
        else:
            self.energy = sys.maxsize

    def choose_children(self, energies):
        """Pick children for updating later if we get chosen as part of a seam."""

        # No children in the last row.
        if self.y == len(energies) - 1:
            return

        # Parents only need to choose children once.
        if len(self.children) > 0:
            return

        # Ensure we always have three children, to make later logic simpler.
        # Left.
        if self.x > 0:
            self.children.append(energies[self.y+1][self.x-1])
        else:
            self.children.append(None)

        # Middle
        self.children.append(energies[self.y+1][self.x])

        # Right.
        if self.x < len(energies[0]) - 1:
            self.children.append(energies[self.y+1][self.x+1])
        else:
            self.children.append(None)

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

def horiz_seamcarve(in_name=IN_NAME, count=10, show=True):
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

    energies = calculate_energies(im_pixels, im.height, im.width)

    # Get sorted list of bottom row to get our seams.
    seam_starts = sorted(random.sample(energies[-1], len(energies[-1])))

    # Carve!
    count = min(count, im.width)
    for i in range(count):

        min_sc_data = seam_starts[i]

        # Get top of seam.
        seam = collections.deque([min_sc_data])
        parent = min_sc_data.parent
        while parent is not None:
            seam.appendleft(parent)
            parent = parent.parent

        for s, elem in enumerate(seam):

            # Update out for each pixel in seam.
            if show:
                out_pixels[elem.y][elem.x] = (255, 0, 0, 254)
            else:
                out_pixels[elem.y] = out_pixels[elem.y][:elem.rel_x] + \
                        out_pixels[elem.y][elem.rel_x+1:]

            # Remove pixel from energies.
            energies[elem.y] = energies[elem.y][:elem.rel_x] +\
                    list(map(lambda x: x.fix_rel_x(), energies[elem.y][elem.rel_x+1:]))

            if s < len(seam) - 1:
                # Have each child of pixel update.
                # They can't choose this pixel in the seam anymore.
                # TODO this is gonna be annoying to generalize.

                left_child = elem.children[0]
                middle_child = elem.children[1]
                right_child = elem.children[2]

                # Handle left child.
                if left_child is not None:
                    left_child.parent_choices = left_child.parent_choices[0:2]

                    # Watch right edge of image (moving target because of deletions).
                    if elem.rel_x < len(energies[elem.y]):
                        left_child.parent_choices.append(energies[elem.y][elem.rel_x])

                    left_child.choose_parent()

                # Handle middle child.
                middle_child.parent_choices = middle_child.parent_choices[0:1] +\
                        middle_child.parent_choices[2:3]

                # Watch right edge of image (moving target because of deletions).
                if elem.rel_x < len(energies[elem.y]):
                    middle_child.parent_choices.append(energies[elem.y][elem.rel_x])

                middle_child.choose_parent()

                # Handle right child.
                right_child.parent_choices = right_child.parent_choices[1:3]

                # Watch left edge of image (moving target because of deletions).
                if elem.rel_x > 0:
                    right_child.parent_choices = [energies[elem.y][elem.rel_x-1]] +\
                        right_child.parent_choices

                right_child.choose_parent()

    return out_pixels

def calculate_energies(im_pixels, height, width):
    """Calculate grid of energies for image."""
    energies = [[SeamCarveData() for i in range(width)] for r in range(height)]

    # Do first row.
    for x in range(width):
        sc_data = energies[0][x]
        sc_data.x = x
        sc_data.y = 0
        sc_data.rel_x = x
        sc_data.pixel = im_pixels[(x, 0)]
        sc_data.energy = get_energy(im_pixels[(x, 0)])

    # Do the rest.
    for y in range(1, height):
        for x in range(width):

            # Set up sc_data.
            sc_data = energies[y][x]
            sc_data.x = x
            sc_data.y = y
            sc_data.rel_x = x
            sc_data.pixel = im_pixels[(x, y)]

            # Choose parent options, minding edges.
            # Left.
            if x > 0:
                sc_data.parent_choices.append(energies[y-1][x-1])

            # Middle.
            sc_data.parent_choices.append(energies[y-1][x])

            # Right.
            if x < width - 1:
                sc_data.parent_choices.append(energies[y-1][x+1])

            # Have parents choose children.
            for parent in sc_data.parent_choices:
                parent.choose_children(energies)

            # Choose cheapest parent.
            sc_data.choose_parent()

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
