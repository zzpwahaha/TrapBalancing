import sys
import ctypes
from time import sleep
import numpy as np
import matplotlib.pyplot as plt

from GMoogProxy import GM_python
from frequency_tones import FrequencyTones
from zynq_client import zynq_tcp_client
from mako_camera import mako_camera

sys.path.append('C:\Chimera\B240_data_analysis\Library\ChimeraGenTools')
from AnalysisHelpers import findAtomLocs, getRawAtomImages

tweezer_moncam_ip = '10.10.0.8'
tweezer_moncam_setting = './tweezer_monitor.xml'

# gmoog = GM_python()
# zclient = zynq_tcp_client()
# mako = mako_camera(ipaddr=tweezer_moncam_ip, settingAddr=tweezer_moncam_setting)
# img_avg = mako.getAvgImages(time_interval = 0.05)

# np.savetxt('img_avg_test.txt',img_avg)
img_avg = np.loadtxt('img_avg_test.txt')
# fig, ax = plt.subplots()
# ax.pcolormesh(img_avg)
# ax.set_aspect(1)
plt.show()
# window = [0,0,img_avg.shape[1], img_avg.shape[0]]
# maximaLocs = findAtomLocs(img_avg, window=None, neighborhood_size=90., threshold=15, sort='MatchArray', debug_plot=True)
maximaLocs = findAtomLocs(img_avg, window=None, neighborhood_size=95., threshold=16, sort='MatchArray', debug_plot=False)
# plt.show()
print(maximaLocs)
idv_atom_img = getRawAtomImages(img_avg, maximaLocs, boundary = [-10,-10,10,10])
fig, ax = plt.subplots()
ax.pcolormesh(idv_atom_img[0])
ax.set_aspect(1)
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
