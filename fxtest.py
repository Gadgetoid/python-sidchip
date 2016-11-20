from sidchip import SIDChip
from sidchip.voice import SIDVoice
from sidchip.effect import Vibrato, Gate
from transport import PySID as Transport
import time
import random
import math

time_step = 0

t = Transport('/tmp/reSID')

sid = SIDChip()

sid.voice1 = Vibrato(sid.voice1, frequency=60,  depth=60, delta=lambda: time_step)
sid.voice2 = Gate(sid.voice2, frequency=10, delta=lambda: time_step)

sid.voice1.triangle = True
sid.voice1.gate = True
sid.voice1.adsr(6,0,10,2)

sid.voice2.triangle = True
sid.voice2.gate = True
sid.voice2.adsr(6,0,15,2)

sid.voice3.sawtooth = True
sid.voice3.gate = True
sid.voice3.adsr(6,0,4,2)

sid.filter.volume = 15

note_speed = 2

rythmn = [40, 45, 41, 47]

melody = [54,54,56,56,58,58,60,60]

bass = [28,28,29,29,30,30,29,29]

s = time.time()

while True:
    step = int((time.time() - s) * note_speed) 

    r = (step % len(rythmn))
    m = (step % len(melody))
    b = (step % len(bass))

    sid.voice1.midi_to_frequency(rythmn[r])

    sid.voice2.midi_to_frequency(melody[m])

    sid.voice3.midi_to_frequency(bass[b])

    t.send(sid.get_regs())
    time.sleep(0.01)

