import sys
import ctypes
from time import sleep
import numpy as np
import matplotlib.pyplot as plt

from GMoogProxy import GM_python
from frequency_tones import FrequencyTones
from zynq_client import zynq_tcp_client
from mako_camera import mako_camera

tweezer_moncam_ip = '10.10.0.8'
tweezer_moncam_setting = './tweezer_monitor.xml'

# gmoog = GM_python()
zclient = zynq_tcp_client()
mako = mako_camera(ipaddr=tweezer_moncam_ip, settingAddr=tweezer_moncam_setting)
img_avg = mako.getAvgImages()
plt.pcolormesh(img_avg)
plt.show()




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
