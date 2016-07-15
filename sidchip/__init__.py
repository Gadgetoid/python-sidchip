from .filter import SIDFilter
from .voice import SIDVoice
from .constants import *

class SIDChip:
    def __init__(self, mode=MODE_PAL):
        self.voice1 = SIDVoice(1, mode=mode)
        self.voice2 = SIDVoice(2, mode=mode)
        self.voice3 = SIDVoice(3, mode=mode)
        self.filter = SIDFilter()

        self.voices = [self.voice1, self.voice2, self.voice3]

    def get_regs(self):
        regs = []
        regs += self.voice1.get_regs()
        regs += self.voice2.get_regs()
        regs += self.voice3.get_regs()
        regs += self.filter.get_regs()

        return regs

    def set_regs(self, regs):
        self.voice1.set_regs(regs[0:7])
        self.voice2.set_regs(regs[7:14])
        self.voice3.set_regs(regs[14:21])
        self.filter.set_regs(regs[21:])

    def __str__(self):
        s_v1 = str(self.voice1).split("\n")
        s_v2 = str(self.voice2).split("\n")
        s_v3 = str(self.voice3).split("\n")
        s_f  = str(self.filter).split("\n")

        rows = max(len(s_v1), len(s_v2), len(s_v3), len(s_f))

        out = [""] * rows

        for x in range(rows):
            out[x] =  s_v1[x].ljust(20,' ')
            out[x] += s_v2[x].ljust(20,' ')
            out[x] += s_v3[x].ljust(20,' ')

            if x < len(s_f):
                out[x] += s_f[x].ljust(20,' ')

        return "\n".join(out)


if __name__ == "__main__":
    '''

    sid.voice1.gate = True
    sid.voice1.sawtooth = True

    sid.voice2.gate = True
    sid.voice2.sawtooth = True

    sid.voice3.gate = True
    sid.voice3.sawtooth = True

    regs = sid.get_regs()

    print(len(regs), regs)

    test = [134, 3, 106, 13, 64, 0, 175, 24, 14, 48, 8, 65, 0, 143, 12, 7, 48, 0, 65, 0, 170, 0, 80, 241, 31]

    sid.set_regs(test)

    print(test)
    print(sid.get_regs())
    print(sid)

    sid.voice1.pitch_to_frequency(440)
    print(sid.voice1.frequency)
    print(sid.voice1.frequency_to_pitch())
    print(sid.voice1.frequency_to_midi())
'''





    sid = SIDChip()
    sid.filter.volume = 10

    t = Transport('/dev/tty.usbserial-DA00V5UX')

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













    while True:
        for o in [-1,0]:
            for x in [69,71,73,75]:
                sid.voice1.midi_to_frequency((x+8) + (o * 12))
                sid.voice2.midi_to_frequency((x+5) + (o * 12))
                sid.voice3.midi_to_frequency(x + (o * 12))


                d = ((sin(time.time() / 2) + 1)/2)

                sid.filter.cutoff = d * sid.filter.max_cutoff
                sid.filter.resonance = (1.0 - d) * sid.filter.max_resonance

                print(sid.get_regs())
                t.send(sid.get_regs())

                time.sleep(0.1)
