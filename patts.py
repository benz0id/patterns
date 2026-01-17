import displayio
import random
import time
from board_init import display, DisplayAdapter

def rb_grad(num):
    palette = displayio.Palette(num)
    for i in range(1, num):
        palette[i] = (255 // (num - i), 0, 255 // (i))
    return palette

class Pattern:
    def __init__(self, display):
        # Configure board to show array.
        self.display = display
        self.arr = displayio.Bitmap(display.width, display.height, 12)
        self.palette = rb_grad(16)
        self.tg = displayio.TileGrid(self.arr, pixel_shader=self.palette)
        self.g = displayio.Group()
        self.g.append(self.tg)


    def show(self):
        self.display.show(self.g)


    def clear(self):
        for c in range(self.display.width):
            for r in range(self.display.height):
                    self.arr[c, r] = 0


    def set_to(self, x, y, col):
        x_in = 0 <= x < self.display.width
        y_in = 0 <= y < self.display.height
        if not (x_in and y_in):
            raise ValueError(''.join(['(', str(x), ', ', str(y), ') is not a valid coordinate']))

        self.arr[x, 31 - y] = col


    def show_axis(self, num = 5, col = 1):
        """Shows the x and y axis, with markings every <num> pixels."""
        for y in range(0, self.display.height, num):
            self.set_to(0, y, col)

        for x in range(0, self.display.width, num):
            self.set_to(x, 0, col)


    def paint_line(self, x_dir = 1, b = 0, col = 1):
        """Fills a line with equation y = x + b onto the bitarray.
        0 <= b <= self.display.width - 1"""

        max_x = self.display.width
        max_y = self.display.height

        if x_dir == 1:
            for y in range(max(0, b), min(max_y, 64 + b)):
                x = y - b
                self.set_to(x, y, col)

        else:
            for y in range(max(0, b - 63), min(max_y, b + 1)):
                x = - y + b
                self.set_to(x, y, col)


    def diag_wave(self, thick: int, speed: int, colour: int,
        up: bool = True, right: bool  = True, new_col = 0):
        """Where -1 denotes travel in the opposite direction"""
        if new_col:
            for i in range(1, thick + 1):
                fac = (1 / thick) * ((i) ** (2) // thick ** (1) )
                adj = 0
                n_col = (int(new_col[0] * fac + adj), int(new_col[1] * fac+  adj), int(new_col[2] * fac + adj))
                print(n_col)
                self.palette[i] = n_col

        if up:
            it = list(range(0, 96))
        else:
            it = list(range(31, -64, -1))

        if not right:
            it = it[::-1]

        for i, b in enumerate(it):
            if i >= thick + 1:
                    self.paint_line(not up, it[i - thick - 1], 0)
            if not new_col:
                self.paint_line(not up, b, colour)
            else:
                for j, k in enumerate(it[i: max(0, i - thick): -1]):
                    self.paint_line(not up, k, thick - j - 1)
            self.show()
            time.sleep(speed)

        for b in enumerate(it[-thick:]):
            self.paint_line(not up, it[i - thick], 0)
            self.show()
            time.sleep(speed)

    def max_white(self, secs):
        self.palette[1] = (255, 255, 255)
        for c in range(self.display.width):
            for r in range(self.display.height):
                    self.arr[c, r] = 1
        self.show()
        time.sleep(secs)
        self.clear()

class BubbleSort(Pattern):

    def __init__(self, display):
        super().__init__(display)

    def run(self, t: float):
        self.bubble_loop(t)

    def update_column(self, col, val, colour = 1):
        for row in range(self.display.height - val):
                    self.arr[col, row] = 0
        for row in range(self.display.height - val, self.display.height):
                    self.arr[col, row] = (val - 1) // 2

    def update_display(self, lst, colour = 1) -> None:
        for col, val in enumerate(lst):
            self.update_column(col, val, colour)

    def bubble_show(self):
        lst = [random.randrange(1, self.display.height + 1) for _ in range(self.display.width)]
        self.update_display(lst)
        self.show()

        for i in range(len(lst) - 1, 0, -1):
            for j in range(0, i):
                if lst[j] > lst[j + 1]:
                    lst[j], lst[j + 1] = lst[j + 1], lst[j]
                    self.update_column(j, lst[j])
                    self.update_column(j + 1, lst[j + 1])
                    self.show()

        print(lst)

    def bubble_loop(self, t: int=None):
        start_time = time.time()
        stop = False
        while not stop:
            self.bubble_show()

            if t is not None:
                stop = time.time() - start_time > t

class Rain(Pattern):

    def run(self, t: int = 5):
        self.rain(t)

    def rain(self, t: int = None):
        """Where t is the time to run the pattern in seconds."""
        # Defaults
        spawn_prob = 1/300
        max_speed = 10
        min_speed = 1
        max_colour = 2
        min_colour = 1

        start_time = time.time()
        stop = False


        self.palette[1] = (0, 0, 150)
        self.palette[2] = (16, 16, 255)
        drops = []
        while not stop:
            new_drops = []
            # Move drops down one row.
            for drop in drops:
                if(drop[2] != 0):
                    new_drops.append((drop[0], drop[1], drop[2] - 1, drop[3],drop[4]))
                elif drop[1] == self.display.height - 1:
                    self.arr[drop[:2]] = 0
                else:
                    self.arr[drop[:2]] = 0
                    new_drops.append((drop[0], drop[1] + 1, drop[3], drop[3], drop[4]))

            drops = new_drops

            for col in range(self.display.width):
                if random.random() < spawn_prob:
                    speed = random.randrange(min_speed, max_speed + 1)
                    colour = random.randrange(min_colour, max_colour + 1)
                    drops.append((col, 0, speed, speed, colour))

            for drop in drops:
                self.arr[drop[:2]] = drop[4]

            self.show()

            if t is not None:
                stop = time.time() - start_time > t










#sp = SimplePatterns(display)
#sp.bubble_show()
#
#sp = SimplePatterns(DisplayAdapter())
#sp.bubble_show()

