#!/usr/bin/env python3
import random

import nono
import nonogen
import outline

if __name__ == "__main__":
    out_pixels = outline.horiz_seamcarve()
    outline.save_pixels(out_pixels)
