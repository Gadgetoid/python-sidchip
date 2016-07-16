import serial

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
