# Python SIDChip

Python SID Chip is a Python class intended to represent the features and functions of a Commodore SID Chip, making it easier to generate the correct register data for an emulator ( such as SIDcog on the Parallax Propeller ) or for sending to a real chip.

# Components

## SIDVoice

Represents a single voice on a SID chip. Functional on its own, but mostly used as part of SIDChip to form a representation for the whole chip.

### Properties

* `frequency` - Set the raw frequency of the SID voice
* `duty_cycle` - The the duty cycle of the pulse oscillator, half of the max value is a square wave
* `noise` - True/False - Enable the noise oscillator, this shouldn't be used in conjunction with any other oscillator
* `sawtooth` - True/False - Enable the sawtooth oscillator
* `triangle` - True/Flase - Enable the triangle oscillator
* `test` - True/False
* `ring` - True/False - Ring modulation with the voice below
* `sync` - True/False
* `gate` - True/False - Enable/Disable the voice, also triggers the ADS and R stages of the envelope
* `attack` - 0 to 15
* `decay` - 0 to 15
* `sustain` - 0 to 15
* `release` - 0 to 15

### Methods

* `adsr(attack, decay, sustain, release)` - Set the envelope ADSR in one shot
* `pitch_to_frequency(hz)` - Set the raw SID freqency from a musical pitch in hz
* `frequency_to_pitch` - Get the musical pitch of the current raw SID frequency
* `midi_to_frequency(midi_number)` - Set the raw SID frequency from a MIDI note number
* `frequency_to_midi` - Get the MIDI note number of the current raw SID frequency

* `get_regs` - Return a list of the SID registers for just this voice
* `set_regs(regs)` - Set the voice properties from a list of registers

## SIDFilter

Represents the SID chip filter. 

* `cutoff`
* `resonance`
* `external`
* `voice3`
* `voice2`
* `voice1`
* `mute3`
* `high_pass`
* `band_pass`
* `low_pass`

* `volume`

## SIDChip