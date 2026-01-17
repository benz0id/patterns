from patts import SimplePatterns
from board_init import DisplayAdapter
#from time import sleep
#from random import randint


# SPDX-FileCopyrightText: 2019 Carter Nelson for Adafruit Industries
#
# SPDX-License-Identifier: MIT




# SPDX-FileCopyrightText: 2019 Carter Nelson for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import board
import terminalio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
display = DisplayAdapter()

wait = input('a')

sp = SimplePatterns(display)

while True:
    sp.rain()

# Set text, font, and color
text = "Oliver"
#font = terminalio.FONT
font = bitmap_font.load_font("/5x5.bdf")
color = (0, 0, 20)

# Create the tet label
text_area = label.Label(font, text=text, color=color)

# Set the location
text_area.anchor_point = (0.0, 0.0)
text_area.anchored_position = (0, 0)
text_area.scale = 1

# Show it
display.show(text_area)

# Loop forever so you can enjoy your text
while True:
    pass
