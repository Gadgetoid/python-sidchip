from sidchip import SIDChip
from sidchip.voice import SIDVoice
from sidchip.effect import Vibrato, Gate
from transport import DummyTransport as Transport
import time
import random
import math

time_step = 0

t = Transport('/dev/tty.usbserial-DA00V5UX')

sid = SIDChip()
sid.voice1.midi_to_frequency(50)

sid.voice1 = Vibrato(sid.voice1, frequency=100,  depth=500, delta=lambda: time_step)
sid.voice1 = Gate(sid.voice1, frequency=20, delta=lambda: time_step)

sid.voice1.triangle = True
sid.voice1.gate = True
sid.voice1.adsr(6,0,15,2)

sid.filter.volume = 15

print("Voice freq: ", sid.voice1.frequency)

note_speed = 1

notes = [40, 45, 41, 47]

s = time.time()

while True:
    time_step += 1

    n = int(((time.time() - s) * note_speed) % len(notes))

    sid.voice1.midi_to_frequency(notes[n])

    #print(sid.get_regs())
    t.send(sid.get_regs())
    time.sleep(0.01)

