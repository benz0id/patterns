from patts import Rain, BubbleSort
from board_init import DisplayAdapter
from receiver import Receiver
from time import sleep
display = DisplayAdapter()

run = False

rain = Rain(display)
sort = BubbleSort(display)

if run:
    while True:
        rain.run(30)
        sort.run(30)
else:
    rain.clear()
    rain.show()
    sleep(92180938249080)

# rec = Receiver(display)
# rec.run_bitmaptools()
