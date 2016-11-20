#!/usr/bin/env python3

from sidchip import SIDChip
from sidchip.effect import Vibrato
import time
from math import sin
from transport import PySID as Transport


if __name__ == "__main__":

    sid = SIDChip()
    sid.filter.volume = 10

    t = Transport('/tmp/reSID')

    
    sid.voice1 = Vibrato(sid.voice1, frequency=10, depth=100)
    sid.voice1.midi_to_frequency(69)

    #while True:
    #    t.send(sid.get_regs())
    #    time.sleep(1)



    sid.filter.voice2 = True
    sid.filter.low_pass = True

    for voice in sid.voices:
        voice.pulse = False
        voice.sawtooth = False
        voice.noise = False
        voice.triangle = False
        voice.gate = True
        voice.duty_cycle = voice.max_duty_cycle / 2 # 50% duty cycle is a square wave, bro!

    sid.voice1.sawtooth = True
    sid.voice2.pulse = True
    sid.voice3.noise = True

    sid.voice1.adsr(0, 0, 13, 0)
    sid.voice2.adsr(10, 5, 3, 10)
    sid.voice3.adsr(0, 0, 13, 6)

    notes      = [
    			60, 60, 60, 60, 60, 60, 60, 60,
    			62, 62, 62, 62, 62, 62, 62, 62, 
    			64, 64, 64, 64, 64, 64, 64, 64, 
    			67, 67, 67, 67, 67, 67, 67, 67, 

                60, 60, 62, 64, 65, 67, 67, 65, 
                60, 60, 62, 64, 65, 67, 71, 68,
                60, 60, 62, 64, 65, 67, 67, 65, 
                60, 60, 62, 64, 65, 67, 71, 68,


                60, 60, 62, 64, 65, 67, 67, 65, 
                60, 60, 62, 64, 65, 67, 71, 68,
                60, 60, 62, 64, 65, 67, 67, 65, 
                60, 60, 62, 64, 65, 67, 71, 68,

                ]

    base_notes = [0,0,0,0,0,0,0,0,
                  0,0,0,0,0,0,0,0,
                  0,0,0,0,0,0,0,0,
                  0,0,0,0,0,0,0,0,

                  31, 31, 31, 31, 32, 32, 32, 32, 
                  34, 34, 34, 34, 35, 35, 35, 35, 
                  31, 31, 31, 31, 32, 32, 32, 32, 
                  35, 35, 35, 35, 34, 34, 34, 34,

                  31+12, 31, 31+12, 31, 32+12, 32, 32+12, 32, 
                  34+12, 34, 34+12, 34, 35+12, 35, 35+12, 35, 
                  31+12, 31, 31+12, 31, 32+12, 32, 32+12, 32, 
                  35+12, 35, 35+12, 35, 34+12, 34, 34+12, 34]

    drum_notes = [
            0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,0,0,
            90,90,90,90,90,90,90,90,
            90,90,60,90,90,90,60,90,

            20, 90, 60, 90, 20, 90, 60, 90, 
            20, 90, 60, 90, 20, 90, 60, 90, 
            20, 90, 60, 90, 20, 90, 60, 90, 
            20, 20, 60, 90, 20, 90, 60, 60,

            20, 90, 60, 90, 20, 90, 60, 90, 
            20, 90, 60, 90, 20, 90, 60, 90, 
            20, 90, 60, 90, 20, 90, 60, 90, 
            20, 20, 60, 90, 20, 90, 60, 60]

    vibrato_depth = 100
    vibrato_speed = 40

    filter_speed = 1

    note_speed = 4

    s = time.time()

    ln = 0

    while True:
        n = int(((time.time() - s) * note_speed) % len(notes))
        b = int(((time.time() - s) * note_speed) % len(base_notes))
        dr = int(((time.time() - s) * note_speed) % len(drum_notes))

        time_in_drum = ((time.time() - s) * note_speed) % len(drum_notes) - dr


        d = ((sin(time.time() * vibrato_speed) + 1)/2)
        c = ((sin(time.time() * filter_speed) + 1)/2)

        sid.voice1.midi_to_frequency(base_notes[b])
        sid.voice2.midi_to_frequency(notes[n])
        sid.voice3.midi_to_frequency(drum_notes[dr])
        
        sid.filter.cutoff = (sid.filter.max_cutoff / 4) + (c * (sid.filter.max_cutoff / 2))
        sid.filter.resonance = (1.0 - c) * sid.filter.max_resonance

        sid.voice2.frequency += d * vibrato_depth

        sid.voice1.gate = base_notes[b] > 0
        sid.voice3.gate = drum_notes[dr] > 0 and time_in_drum < 0.3

        if notes[n] != ln:
            sid.voice2.gate = False
            t.send(sid.get_regs())
            ln = notes[n]

        sid.voice2.gate = True
        t.send(sid.get_regs())

        time.sleep(0.001)

