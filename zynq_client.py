import socket
import sys
from time import sleep

# 2022/10/18
# trg_command = [b't00002710_b00006B00000000D0',
#                b't00002774_b01006B00000000D0',
#                b't000027D8_b00006B00000000D0']
# static_output_command = [b't00002710_b00006B00000000D0']

# 2023/03/23
trg_command = [b't00002710_b0000EB00000000D0',
               b't00002774_b0100EB00000000D0',
               b't000027D8_b0000EB00000000D0']
static_output_command = [b't00002710_b0000EB00000000D0']


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
        try:
            self.sock.connect(self.server_address)
        except OSError as err:
            # print("Warning: error occured during connecting to zynq: ",err.strerror)
            # print("Try to reset the socket and reconnect. This should only happen when the connection is closed and the self.sock need to be re-initialize before connect.") 
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            self._sendMessage(b'end_0', self.connectByteLen)

            self._sendMessage(f'DIOseq_{len(static_output_command):d}'.encode('utf-8'), self.connectByteLen)
            for _cmd in static_output_command:
                self._sendMessage(_cmd, self.dioByteLen)
            self._sendMessage(b'end_0', self.connectByteLen)
            self._sendMessage(b'trigger', self.connectByteLen)
            self._sendMessage(b'end_0', self.connectByteLen)


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
    client.triggerGigamoog()
    # sleep(1)
    # client.triggerGigamoog()

'''
received "DIOseq_3                                                        "
dev =  DIOseq
num_bytes =  84

 snapshot 0
b't00002710_b00006B00000000D0\x00'

 snapshot 1
b't00002774_b01006B00000000D0\x00'

 snapshot 2
b't000027D8_b00006B00000000D0\x00'
DIO points
b't00002710_b00006B00000000D0\x00'
b't00002774_b01006B00000000D0\x00'
b't000027D8_b00006B00000000D0\x00'
GPIO_seq_point(address =  0 ,time= 10000 ,outputA =  0x000000d0 ,outputB =  0x00006b00 )
GPIO_seq_point(address =  1 ,time= 10100 ,outputA =  0x000000d0 ,outputB =  0x01006b00 )
GPIO_seq_point(address =  2 ,time= 10200 ,outputA =  0x000000d0 ,outputB =  0x00006b00 )
GPIO_seq_point(address =  3 ,time= 0 ,outputA =  0x00000000 ,outputB =  0x00000000 )
mod enabled from zynq
set_bit 1
MOD IS ON, CAN RUN SEQUENCER FOR EXPERIMENT OR CHANGE DAC, TTL NOW
'''