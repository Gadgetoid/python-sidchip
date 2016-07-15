from .constants import *
from math import log

class SIDVoice(object):
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

