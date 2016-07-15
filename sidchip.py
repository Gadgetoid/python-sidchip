from math import log, sin
import time
import serial

MODE_PAL  = 985248
MODE_NTSC = 1022727
MIDI_A4 = 69
FREQ_A4 = 440.

class Transport:
    def __init__(self, port):
        self.serial = serial.Serial(port, 115200)

    def send(self, regs):
        data = [chr(13),'S','D','M','P'] + [chr(x) for x in regs]

        self.serial.write(''.join(data))
        self.serial.flush()

    def __del__(self):
        self.send([0] * 25)
        self.serial.close()

class SIDVoice:
    def __init__(self, number, mode=MODE_PAL):
        self.number = number
        self.mode = mode

        self.frequency = 0    # Regs 0 and 1
        self.duty_cycle = 0   # Regs 2 and 3

        self.noise = False    # Reg 4, bit 7
        self.pulse = False    # Reg 4, bit 6
        self.sawtooth = False # Reg 4, bit 5
        self.triangle = False # Reg 4, bit 4
        self.test = False     # Reg 4, bit 3
        self.ring = False     # Reg 4, bit 2
        self.sync = False     # Reg 4, bit 1
        self.gate = False     # Reg 4, bit 0

        self.attack = 0
        self.decay = 0
        self.sustain = 0
        self.release = 0

        self.max_adsr = (1 << 4) - 1
        self.max_duty_cycle = (1 << 12) - 1

    def adsr(self, a, d, s, r):
        self.attack = a
        self.decay = d
        self.sustain = s
        self.release = r

    def pitch_to_frequency(self, hz):
        self.frequency = (pow(256,3) / float(self.mode)) * float(hz)

    def frequency_to_pitch(self):
        return round(self.frequency / (pow(256,3) / float(self.mode)),2)

    def midi_to_frequency(self, midi_number):
        pitch = FREQ_A4 * 2 ** ((midi_number - MIDI_A4) * (1./12.))
        self.pitch_to_frequency(pitch)

    def frequency_to_midi(self):
        if self.frequency_to_pitch() > 0:
            result = int(12 * (log(self.frequency_to_pitch(),2) - log(FREQ_A4,2)) + MIDI_A4)
            if result > 0: return result

        return None

    def get_regs(self):
        regs = [0] * 7

        regs[0] = int(self.frequency) & 0xff
        regs[1] = (int(self.frequency) >> 8) & 0xff

        regs[2] = int(self.duty_cycle) & 0xff
        regs[3] = (int(self.duty_cycle) >> 8) & 0xf

        regs[4] = (
                ((self.noise    & 1) << 7) |
                ((self.pulse    & 1) << 6) |
                ((self.sawtooth & 1) << 5) |
                ((self.triangle & 1) << 4) |
                ((self.test     & 1) << 3) |
                ((self.ring     & 1) << 2) |
                ((self.sync     & 1) << 1) |
                ((self.gate     & 1) << 0)
            )

        regs[5] = ((self.attack  & 0xf) << 4) | (self.decay   & 0xf)

        regs[6] = ((self.sustain & 0xf) << 4) | (self.release & 0xf)

        return regs

    def set_regs(self, regs):
        self.frequency  = regs[0] | (regs[1] << 8)

        self.duty_cycle = regs[2] | (regs[3] << 8)

        self.noise    = (regs[4] & (1 << 7)) > 0
        self.pulse    = (regs[4] & (1 << 6)) > 0
        self.sawtooth = (regs[4] & (1 << 5)) > 0
        self.triangle = (regs[4] & (1 << 4)) > 0
        self.test     = (regs[4] & (1 << 3)) > 0
        self.ring     = (regs[4] & (1 << 2)) > 0
        self.sync     = (regs[4] & (1 << 1)) > 0
        self.gate     = (regs[4] & (1 << 0)) > 0

        self.attack   = (regs[5] & 0xf0) >> 4
        self.decay    = (regs[5] & 0x0f)

        self.sustain  = (regs[6] & 0xf0) >> 4
        self.release  = (regs[6] & 0x0f)

    def __str__(self):
        return '''
--- SID Voice{number} ---
Frequency: {frequency}
Duty:      {duty_cycle}

Noise:     {noise}
Pulse:     {pulse}
Sawtooth:  {sawtooth}
Triangle:  {triangle}

Test:      {test}
Ring:      {ring}
Sync:      {sync}
Gate:      {gate}

Attack:    {attack}
Decay:     {decay}
Sustain:   {sustain}
Release:   {release}
------------------
'''.format(
        number = self.number,
        frequency = self.frequency,
        duty_cycle = self.duty_cycle,
        noise = self.noise,
        pulse = self.pulse,
        sawtooth = self.sawtooth,
        triangle = self.triangle,
        test = self.test,
        ring = self.ring,
        sync = self.sync,
        gate = self.gate,
        attack = self.attack,
        decay = self.decay,
        sustain = self.sustain,
        release = self.release
    )


class SIDFilter:
    def __init__(self):
        self.cutoff = 0
        self.resonance = 0
        self.external = False
        self.voice3 = False
        self.voice2 = False
        self.voice1 = False
        self.mute3 = False
        self.high_pass = False
        self.band_pass = False
        self.low_pass = False
        self.volume = 0

        self.max_cutoff = (1 << 11) - 1
        self.max_resonance = (1 << 4) - 1

    def get_regs(self):
        regs = [0] * 4

        regs[0] = int(self.cutoff) & 0x7
        regs[1] = (int(self.cutoff) >> 3) & 0xff

        regs[2] = (
                ((int(self.resonance) & 0xf) << 4) | 
                ((self.external  & 1)   << 3) |
                ((self.voice3    & 1)   << 2) |
                ((self.voice2    & 1)   << 1) |
                ((self.voice1    & 1)   << 0)
            )

        regs[3] = (
                ((self.mute3     & 1) << 7) |
                ((self.high_pass & 1) << 6) |
                ((self.band_pass & 1) << 5) |
                ((self.low_pass  & 1) << 4) |
                (self.volume & 0xf)
            )

        return regs

    def set_regs(self, regs):
        self.cutoff = regs[0] | (regs[1] << 3)

        self.resonance = regs[2] >> 4

        self.external = (regs[2] & (1 << 3)) > 0
        self.voice3   = (regs[2] & (1 << 2)) > 0
        self.voice2   = (regs[2] & (1 << 1)) > 0
        self.voice1   = (regs[2] & (1 << 0)) > 0

        self.mute3    = (regs[3] & (1 << 7)) > 0
        self.high_pass= (regs[3] & (1 << 6)) > 0
        self.band_pass= (regs[3] & (1 << 5)) > 0
        self.low_pass = (regs[3] & (1 << 4)) > 0

        self.volume   = regs[3] & 0xf

    def __str__(self):
        return '''
--- SID Filter ---
Cutoff:    {cutoff}
Resonance: {resonance}
External:  {external}
Voice1:    {voice1}
Voice2:    {voice2}
Voice3:    {voice3}

Mute3:     {mute3}
High Pass: {high_pass}
Band Pass: {band_pass}
Low Pass:  {low_pass}

Volume:    {volume}
------------------
'''.format(
        cutoff    = self.cutoff,
        resonance = self.resonance,
        external  = self.external,
        voice1    = self.voice1,
        voice2    = self.voice2,
        voice3    = self.voice3,
        mute3     = self.mute3,
        high_pass = self.high_pass,
        band_pass = self.band_pass,
        low_pass  = self.low_pass,
        volume    = self.volume
    )

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
