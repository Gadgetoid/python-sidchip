from .voice import SIDVoice
from math import sin
from time import time

class SIDEffect(SIDVoice):
   def __init__(self, parent):
       self.__dict__['_parent'] = parent

   def __setattr__(self, name, value):
       if name in self.__dict__.keys():
           self.__dict__[name] = value
       elif '_parent' in self.__dict__.keys():
           self.__dict__['_parent'].__dict__[name] = value

   def __getattr__(self, name):
       if name in self.__dict__.keys():
           return self.__dict__[name]

       elif '_parent' in self.__dict__.keys() and hasattr(self.__dict__['_parent'], name):
           return getattr(self.__dict__['_parent'],name)

       elif '_parent' in self.__dict__.keys() and  name in self.__dict__['_parent'].__dict__.keys():
           return self.__dict__['_parent'].__dict__[name]

       else:
           raise AttributeError("No attribute {name}".format(name=name))

class Vibrato(SIDEffect):
    def __init__(self, parent, frequency=10, depth=100):

        self.__dict__['_vibrato_frequency'] = frequency
        self.__dict__['_vibrato_depth'] = depth

        SIDEffect.__init__(self, parent)

    def _get_frequency(self):
        vibrato = ((sin(time() * self._vibrato_frequency) + 1) / 2) * self._vibrato_depth

        return self._parent.frequency + vibrato

    def _set_frequency(self, value):
        self._parent.frequency = value

    frequency = property(_get_frequency, _set_frequency)

