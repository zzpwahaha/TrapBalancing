import socket
import sys

# 2022/10/18
trg_command = [b't00002710_b00006B00000000D0',
               b't00002774_b01006B00000000D0',
               b't000027D8_b00006B00000000D0']


class zynq_tcp_client:
    def __init__(self):
        self.server_address = ("10.10.0.2", 8080)
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connectByteLen = 64
        self.dioByteLen = 28
        self.dacByteLen = 42
        self.ddsByteLen = 46

    def connect(self):
        self.sock.connect(self.server_address)

    def _sendMessage(self, message, length):
        messagePad = message.ljust(length, b'\0')
        self.sock.sendall(messagePad)

    def _triggerGigamoogWithTweezersOn(self):
        try:
            self._sendMessage(f'DIOseq_{len(trg_command):d}'.encode('utf-8'), self.connectByteLen)
            for _cmd in trg_command:
                self._sendMessage(_cmd, self.dioByteLen)
            self._sendMessage(b'end_0', self.connectByteLen)
            self._sendMessage(b'trigger', self.connectByteLen)
        except:
            print('write failed')

    def triggerGigamoog(self):
        self.connect()
        self._triggerGigamoogWithTweezersOn()
        self.disconnect()


    # def turnOffTTLs(self):
    #     try:
    #         self.sendMessage(b'DIOseq_1', self.connectByteLen)
    #         self.sendMessage(b't000186A0_b0000000000000000', self.dioByteLen)
    #         self.sendMessage(b'end_0', self.connectByteLen)
    #         self.sendMessage(b'trigger', self.connectByteLen)
    #     except:
    #         print('write failed')

    # def triggerBlueMot(self):
    #     try:
    #         self.sendMessage(b'DIOseq_1', self.connectByteLen)
    #         self.sendMessage(b't000186A0_b000000000007000C', self.dioByteLen)
    #         self.sendMessage(b'end_0', self.connectByteLen)
    #         self.sendMessage(b'trigger', self.connectByteLen)
    #     except:
    #         print('write failed')

    def disconnect(self):

        # print('closing socket')
        self.sock.close()


if __name__ == "__main__":
    client = zynq_tcp_client()
    client.connect()
    client._triggerGigamoogWithTweezersOn()
    client.disconnect()
