from sidchip import SIDChip
from sidchip.voice import SIDVoice
from sidchip.effect import Vibrato
import time

sid = SIDChip()
sid.voice1.midi_to_frequency(69)
sid.voice1 = Vibrato(sid.voice1, frequency=1,  depth=100)
sid.voice1 = Vibrato(sid.voice1, frequency=10, depth=1000)

#sid.voice2 = Vibrato(sid.voice2, frequency=10, depth=500)

print("Voice freq: ", sid.voice1.frequency)

for x in range(100):
    print(sid.get_regs())
    time.sleep(0.01)

