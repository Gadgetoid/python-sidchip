import serial
import os

class PySID:
    def __init__(self, nothing):
        from pysid import pysid
        self.pysid = pysid

    def send(self, regs):
        for x in range(25):
            self.pysid.write_reg(x, regs[x])

    def __del__(self):
        self.send([0] * 25)
        

class FifoTransport:
    def __init__(self, fifo_file):
        try:
            os.mkfifo(fifo_file)
        except OSError:
            pass

        self.fifo = open(fifo_file,'wb')

    def send(self, regs):
        data = [chr(13),'S','D','M','P'] + [chr(x) for x in regs]
        self.fifo.write(''.join(data))

    def __del__(self):
        self.send([0] * 25)


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


class DummyTransport:
    def __init__(self, port):
        pass
    def send(self, data):
        print(data)
