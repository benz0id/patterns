import displayio
import random
import time
import adafruit_fancyled.adafruit_fancyled as fancy
from board_init import display, DisplayAdapter
from bitmaptools import readinto
from sys import stdin

import displayio
import adafruit_fancyled.adafruit_fancyled as fancy


SAVED_COLOURS = [
(0, 0, 0),      # empty
(199, 31, 23),  # death
(255, 131, 226),# mate
(0, 0, 0),      # null - term sig
(0, 0, 0),      # null - term sig
(206, 121, 255),# clone
(255, 181, 44), # fire
(36, 209, 1),   # born
(255, 110, 74), # reward
(0, 0, 30)      # sector boundry
]

HEATMAP_COLOURS = [
(0, 0, 0),      # empty
(199, 31, 23),  # death
(0, 0, 0),# mate
(0, 0, 0),      # null - term sig
(0, 0, 0),      # null - term sig
(102, 81, 145),# clone
(160, 81, 149), # fire
(212, 80, 135),   # born
(249, 93, 106), # reward
(255, 124, 67)      # sector boundry
]

SAVED_COLOURS = HEATMAP_COLOURS

NORM_FAC = 150

def brightness_norm(p, n):
    p_norm = []
    for c in p:
        if sum(c) == 0:
            p_norm.append(c)
            continue

        fac = n / sum(c)
        p_norm.append(tuple([int(val * fac) for val in c]))
    return p_norm

SAVED_COLOURS = brightness_norm(SAVED_COLOURS, NORM_FAC)


def get_distance(a, b):
    s = 0
    for i in range(len(a)):
        s += (a[i] - b[i]) ** 2
    return s ** (1/2)

def get_palette(num):
    palette = displayio.Palette(num)
    colours = []
    for i in range(len(SAVED_COLOURS)):
        palette[i] = SAVED_COLOURS[i]
        colours.append(SAVED_COLOURS[i])

    for i in range(len(SAVED_COLOURS), num):
        """
        print(i)
        in_range = False
        distance = False

        while not in_range or not distance:
            colour = random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)
            in_range = 50 < sum(colour) < 255
            distance = all([15 < get_distance(colour, colours[j]) for j in range(0, i)])
        colours.append(colour)
        """
        colour = 30, 30, 30
        palette[i] = colour
    return palette



def rb_grad(num, max_c=70):
    palette = displayio.Palette(num)
    for i in range(1, num):
        fac = i / num
        colour = int(max_c * fac), 0, int(max_c * (1 - fac))
        palette[i] = colour
    return palette

PALETTE_SIZE = 255

class Receiver:

    def __init__(self, display):
        # Configure board to show array.
        self.display = display
        self.palette = get_palette(PALETTE_SIZE)
        self.arr = displayio.Bitmap(display.width, display.height, PALETTE_SIZE)
        self.tg = displayio.TileGrid(self.arr, pixel_shader=self.palette)
        self.g = displayio.Group()
        self.g.append(self.tg)
        self.test()

    def test(self):
        for i in range(PALETTE_SIZE):
            self.arr[i % 64, i // 64] = i
        self.show()
        time.sleep(2)


    def show(self):
        self.display.show(self.g)

    def clear(self):
        for c in range(self.display.width):
            for r in range(self.display.height):
                    self.arr[c, r] = 0


    def run_bitmaptools(self):
        self.show()
        while True:

            #start = time.monotonic()

            pixels = displayio.Bitmap(display.width, display.height, PALETTE_SIZE)

            readinto(pixels, stdin, 8)

            #readtime = time.monotonic() - start

            #start = time.monotonic()
            tile_grid = displayio.TileGrid(pixels, pixel_shader=self.palette)
            self.g.pop()
            self.g.append(tile_grid)
            #printtime = time.monotonic() - start
            print('received')


    def run(self):
        self.show()
        while True:

            start = time.monotonic()
            # cmd = input()

            pixels = displayio.Bitmap(display.width, display.height, PALETTE_SIZE)

            x = 0
            y = 0

            for char in cmd:
                pixels[x, y] = int(char)
                x += 1
                if x >= display.width:
                    x = 0
                    y += 1

            # readtime = time.monotonic() - start

            # start = time.monotonic()
            tile_grid = displayio.TileGrid(pixels, pixel_shader=self.palette)
            self.g.pop()
            self.g.append(tile_grid)
            # printtime = time.monotonic() - start
            # print(readtime, printtime)
