import board
import displayio
import framebufferio
import rgbmatrix
import time


class DisplayAdapter:
    """Allows for the managing of multiple groups and flexible
    display control."""
    frame_delay = 0.000001
    width: int
    height: int

    def __init__(self) -> None:

        # Initialise display
        displayio.release_displays()
        matrix = rgbmatrix.RGBMatrix(
            width=64, bit_depth=4,
            rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
            addr_pins=[board.D25, board.D24, board.A3, board.A2],
            clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)
        self.display = framebufferio.FramebufferDisplay(matrix)
        self.display.auto_refresh = True

        self.width = self.display.width
        self.height = self.display.height

    def show(self, group) -> None:
        self.display.show(group)
        time.sleep(self.frame_delay)

display = DisplayAdapter()


