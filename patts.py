import displayio
import random
import time
from board_init import display, DisplayAdapter

# Global Brightness Setting (0.0 to 1.0)
BRIGHTNESS = 0.1

def scale_rgb(color):
    """
    Scales RGB values by BRIGHTNESS.
    Enforces a hardware floor: if a channel is > 0, it must be >= 16
    to be visible on this specific display hardware.
    """
    scaled_color = []
    for c in color:
        if c == 0:
            scaled_color.append(0)
        else:
            # Scale, but ensure it doesn't fall below the visible threshold of 16
            val = int(c * BRIGHTNESS)
            scaled_color.append(max(16, val))
    return tuple(scaled_color)

def rb_grad(num):
    palette = displayio.Palette(num)
    for i in range(1, num):
        # Calculate gradient then scale
        r = 255 // (num - i)
        b = 255 // (i)
        palette[i] = scale_rgb((r, 0, b))
    return palette

class Pattern:
    def __init__(self, display):
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

    def paint_line(self, x_dir = 1, b = 0, col = 1):
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
        if new_col:
            for i in range(1, thick + 1):
                fac = (1 / thick) * ((i) ** (2) // thick ** (1) )
                adj = 0
                n_col = (int(new_col[0] * fac + adj), int(new_col[1] * fac+  adj), int(new_col[2] * fac + adj))
                self.palette[i] = scale_rgb(n_col)

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
        self.palette[1] = scale_rgb((255, 255, 255))
        for c in range(self.display.width):
            for r in range(self.display.height):
                    self.arr[c, r] = 1
        self.show()
        time.sleep(secs)
        self.clear()

class Sorter(Pattern):
    def __init__(self, display):
        super().__init__(display)
        # Delay for fast sorts (seconds) to make them visible
        self.fast_delay = 0.05

    def run(self, t: float):
        self.loop(t)

    def update_column(self, col, val, colour = 1):
        # Clear the top part of the column
        for row in range(self.display.height - val):
            self.arr[col, row] = 0
        # Draw the bar at the bottom
        for row in range(self.display.height - val, self.display.height):
            # Map height to palette index (gradient)
            self.arr[col, row] = (val - 1) // 2

    def update_display(self, lst, colour = 1) -> None:
        for col, val in enumerate(lst):
            self.update_column(col, val, colour)

    # --- O(n^2) Simple Sorts ---

    def bubble_sort(self, lst):
        n = len(lst)
        for i in range(n - 1, 0, -1):
            for j in range(0, i):
                if lst[j] > lst[j + 1]:
                    lst[j], lst[j + 1] = lst[j + 1], lst[j]
                    self.update_column(j, lst[j])
                    self.update_column(j + 1, lst[j + 1])
                    self.show()

    def selection_sort(self, lst):
        n = len(lst)
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                if lst[j] < lst[min_idx]:
                    min_idx = j
            if min_idx != i:
                lst[i], lst[min_idx] = lst[min_idx], lst[i]
                self.update_column(i, lst[i])
                self.update_column(min_idx, lst[min_idx])
                self.show()

    def insertion_sort(self, lst):
        for i in range(1, len(lst)):
            key = lst[i]
            j = i - 1
            while j >= 0 and key < lst[j]:
                lst[j + 1] = lst[j]
                self.update_column(j + 1, lst[j+1])
                self.show()
                j -= 1
            lst[j + 1] = key
            self.update_column(j + 1, key)
            self.show()

    def gnome_sort(self, lst):
        index = 0
        n = len(lst)
        while index < n:
            if index == 0:
                index += 1
            if lst[index] >= lst[index - 1]:
                index += 1
            else:
                lst[index], lst[index - 1] = lst[index - 1], lst[index]
                self.update_column(index, lst[index])
                self.update_column(index - 1, lst[index - 1])
                self.show()
                index -= 1

    def cocktail_shaker_sort(self, lst):
        n = len(lst)
        swapped = True
        start = 0
        end = n - 1
        while swapped:
            swapped = False
            # Forward pass
            for i in range(start, end):
                if lst[i] > lst[i + 1]:
                    lst[i], lst[i + 1] = lst[i + 1], lst[i]
                    self.update_column(i, lst[i])
                    self.update_column(i + 1, lst[i + 1])
                    self.show()
                    swapped = True
            if not swapped:
                break
            swapped = False
            end -= 1
            # Backward pass
            for i in range(end - 1, start - 1, -1):
                if lst[i] > lst[i + 1]:
                    lst[i], lst[i + 1] = lst[i + 1], lst[i]
                    self.update_column(i, lst[i])
                    self.update_column(i + 1, lst[i + 1])
                    self.show()
                    swapped = True
            start += 1

    # --- O(n log n) & Faster Sorts (Slowed down for visibility) ---

    def comb_sort(self, lst):
        n = len(lst)
        gap = n
        shrink = 1.3
        sorted = False
        while not sorted:
            gap = int(gap / shrink)
            if gap <= 1:
                gap = 1
                sorted = True
            i = 0
            while i + gap < n:
                if lst[i] > lst[i + gap]:
                    lst[i], lst[i + gap] = lst[i + gap], lst[i]
                    self.update_column(i, lst[i])
                    self.update_column(i + gap, lst[i + gap])
                    self.show()
                    time.sleep(self.fast_delay)
                    sorted = False
                i += 1

    def shell_sort(self, lst):
        n = len(lst)
        gap = n // 2
        while gap > 0:
            for i in range(gap, n):
                temp = lst[i]
                j = i
                while j >= gap and lst[j - gap] > temp:
                    lst[j] = lst[j - gap]
                    self.update_column(j, lst[j])
                    self.show()
                    j -= gap
                lst[j] = temp
                self.update_column(j, lst[j])
                self.show()
                time.sleep(self.fast_delay)
            gap //= 2

    def heap_sort(self, lst):
        n = len(lst)

        def heapify(n, i):
            largest = i
            l = 2 * i + 1
            r = 2 * i + 2
            if l < n and lst[l] > lst[largest]:
                largest = l
            if r < n and lst[r] > lst[largest]:
                largest = r
            if largest != i:
                lst[i], lst[largest] = lst[largest], lst[i]
                self.update_column(i, lst[i])
                self.update_column(largest, lst[largest])
                self.show()
                time.sleep(self.fast_delay)
                heapify(n, largest)

        # Build max heap
        for i in range(n // 2 - 1, -1, -1):
            heapify(n, i)

        # Extract elements
        for i in range(n - 1, 0, -1):
            lst[i], lst[0] = lst[0], lst[i]
            self.update_column(i, lst[i])
            self.update_column(0, lst[0])
            self.show()
            time.sleep(self.fast_delay)
            heapify(i, 0)

    def quick_sort(self, lst):
        def partition(low, high):
            pivot = lst[high]
            i = low - 1
            for j in range(low, high):
                if lst[j] < pivot:
                    i += 1
                    lst[i], lst[j] = lst[j], lst[i]
                    self.update_column(i, lst[i])
                    self.update_column(j, lst[j])
                    self.show()
            lst[i + 1], lst[high] = lst[high], lst[i + 1]
            self.update_column(i + 1, lst[i + 1])
            self.update_column(high, lst[high])
            self.show()
            time.sleep(self.fast_delay)
            return i + 1

        def sort(low, high):
            if low < high:
                pi = partition(low, high)
                sort(low, pi - 1)
                sort(pi + 1, high)

        sort(0, len(lst) - 1)

    def merge_sort(self, lst):
        def merge(l, m, r):
            n1 = m - l + 1
            n2 = r - m
            L = lst[l : m + 1]
            R = lst[m + 1 : r + 1]
            i = 0
            j = 0
            k = l
            while i < n1 and j < n2:
                if L[i] <= R[j]:
                    lst[k] = L[i]
                    i += 1
                else:
                    lst[k] = R[j]
                    j += 1
                self.update_column(k, lst[k])
                self.show()
                time.sleep(self.fast_delay)
                k += 1
            while i < n1:
                lst[k] = L[i]
                self.update_column(k, lst[k])
                self.show()
                time.sleep(self.fast_delay)
                i += 1
                k += 1
            while j < n2:
                lst[k] = R[j]
                self.update_column(k, lst[k])
                self.show()
                time.sleep(self.fast_delay)
                j += 1
                k += 1

        def sort(l, r):
            if l < r:
                m = (l + r) // 2
                sort(l, m)
                sort(m + 1, r)
                merge(l, m, r)

        sort(0, len(lst) - 1)

    def sort_show(self):
        lst = [random.randrange(1, self.display.height + 1) for _ in range(self.display.width)]
        self.update_display(lst)
        self.show()

        algos = [
            self.bubble_sort,
            self.selection_sort,
            self.insertion_sort,
            self.gnome_sort,
            self.cocktail_shaker_sort,
            self.comb_sort,
            self.shell_sort,
            self.heap_sort,
            self.quick_sort,
            self.merge_sort
        ]

        algo = random.choice(algos)
        algo(lst)

    def loop(self, t: int=None):
        start_time = time.time()
        stop = False
        while not stop:
            self.sort_show()
            time.sleep(1)

            if t is not None:
                stop = time.time() - start_time > t

class GameOfLife(Pattern):
    def __init__(self, display):
        super().__init__(display)
        self.w = display.width
        self.h = display.height

        self.stride = self.w + 2
        self.buf_size = (self.w + 2) * (self.h + 2)

        self.b1 = bytearray(self.buf_size)
        self.b2 = bytearray(self.buf_size)

    def randomize(self, density):
        threshold = 1.0 - density
        for y in range(1, self.h + 1):
            base = y * self.stride
            for x in range(1, self.w + 1):
                self.b1[base + x] = 1 if random.random() > threshold else 0
        self.draw_from_buffer(self.b1)

    def draw_from_buffer(self, buf):
        for y in range(self.h):
            row_offset = (y + 1) * self.stride + 1
            for x in range(self.w):
                age = buf[row_offset + x]
                if age == 0:
                    color_idx = 0
                elif age <= 3:
                    color_idx = 1 # Young
                else:
                    color_idx = 2 # Old
                if self.arr[x, y] != color_idx:
                    self.arr[x, y] = color_idx
        self.show()

    def update_ghost_cells(self, buf):
        w, h, s = self.w, self.h, self.stride
        buf[(h + 1) * s + 1 : (h + 1) * s + 1 + w] = buf[s + 1 : s + 1 + w]
        buf[1 : 1 + w] = buf[h * s + 1 : h * s + 1 + w]
        for y in range(0, h + 2):
            row = y * s
            buf[row] = buf[row + w]
            buf[row + w + 1] = buf[row + 1]

    def run(self, t: int = None, density: float = 0.2, stagnation_limit: int = 20, color=None):
        base_color = color if color else (255, 255, 255)
        self.palette[1] = scale_rgb(base_color)
        self.palette[2] = scale_rgb((255, 0, 0))

        start_time = time.time()
        stop = False

        self.randomize(density)
        active_buf = self.b1
        next_buf = self.b2

        last_pop = -1
        stagnant_frames = 0

        while not stop:
            self.update_ghost_cells(active_buf)
            pop = 0
            changes = False
            for y in range(1, self.h + 1):
                row_start = y * self.stride + 1
                row_end = row_start + self.w
                for i in range(row_start, row_end):
                    n = (int(active_buf[i - self.stride - 1] > 0) +
                         int(active_buf[i - self.stride] > 0)     +
                         int(active_buf[i - self.stride + 1] > 0) +
                         int(active_buf[i - 1] > 0) +
                         int(active_buf[i + 1] > 0) +
                         int(active_buf[i + self.stride - 1] > 0) +
                         int(active_buf[i + self.stride] > 0)     +
                         int(active_buf[i + self.stride + 1] > 0))
                    age = active_buf[i]
                    is_alive = age > 0
                    if is_alive:
                        if n == 2 or n == 3:
                            new_age = age + 1
                            if new_age > 6:
                                next_buf[i] = 0
                                changes = True
                            else:
                                next_buf[i] = new_age
                                pop += 1
                                if new_age != age: changes = True
                        else:
                            next_buf[i] = 0
                            changes = True
                    else:
                        if n == 3:
                            next_buf[i] = 1
                            pop += 1
                            changes = True
                        else:
                            next_buf[i] = 0
            active_buf, next_buf = next_buf, active_buf
            self.draw_from_buffer(active_buf)
            if pop == 0:
                stagnant_frames += 1
            else:
                stagnant_frames = 0
            if stagnant_frames > stagnation_limit:
                self.randomize(density)
                stagnant_frames = 0
                active_buf = self.b1
                next_buf = self.b2
            if t is not None and (time.time() - start_time > t):
                stop = True

class Rain(Pattern):
    def run(self, t: int = 5):
        self.rain(t)

    def rain(self, t: int = None):
        spawn_prob = 1/300
        max_speed = 10
        min_speed = 1
        max_colour = 2
        min_colour = 1

        start_time = time.time()
        stop = False

        self.palette[1] = scale_rgb((0, 0, 150))
        self.palette[2] = scale_rgb((16, 16, 255))
        drops = []
        while not stop:
            new_drops = []
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
