from .constants import *

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

