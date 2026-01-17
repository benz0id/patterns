from patts import Rain, Sorter, GameOfLife
from board_init import DisplayAdapter
from receiver import Receiver
from time import sleep
display = DisplayAdapter()

run = True

rain = Rain(display)
sort = Sorter(display)
gol = GameOfLife(display)

if run:
    while True:
        rain.run(60)
        sort.run(60)
        gol.run(t=60, density=0.12, stagnation_limit=20, color=(265, 265, 265))
else:
    rain.clear()
    rain.show()
    sleep(92180938249080)

# rec = Receiver(display)
# rec.run_bitmaptools()
