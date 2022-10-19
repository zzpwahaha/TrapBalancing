import sys
import ctypes
from time import sleep
import numpy as np
import matplotlib.pyplot as plt
sys.path.append('./3rd_Party/Vimba_4.2/VimbaPython/Source')
import vimba
from dataclasses import dataclass
from zynq_client import zynq_tcp_client



tweezer_moncam_ip = '10.10.0.8'
tweezer_moncam_setting = './tweezer_monitor.xml'


gmoogLib = ctypes.cdll.LoadLibrary(
    'C:/Chimera/gmoogLib/gmoogLib/x64/Release/gmoogLib.dll')


class GM_python(object):
    def __init__(self):
        gmoogLib.gm_new.argtypes = []
        gmoogLib.gm_new.restype = ctypes.c_void_p

        gmoogLib.gm_test.argtypes = [ctypes.c_void_p]
        gmoogLib.gm_test.restype = ctypes.c_int

        gmoogLib.gm_zeroAll.argtypes = [ctypes.c_void_p]
        gmoogLib.gm_zeroAll.restype = ctypes.c_void_p

        gmoogLib.gm_endMessage.argtypes = [ctypes.c_void_p]
        gmoogLib.gm_endMessage.restype = ctypes.c_void_p

        gmoogLib.gm_setDAC.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(
            ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
        gmoogLib.gm_setDAC.restype = ctypes.c_void_p

        self.obj = gmoogLib.gm_new()

    def test(self):
        gmoogLib.gm_test(self.obj)

    def zeroAll(self):
        gmoogLib.gm_zeroAll(self.obj)

    def endMessage(self):
        gmoogLib.gm_endMessage(self.obj)

    def setDAC(self, dac, channels, freqs, amps, phases):
        gmoogLib.gm_setDAC(self.obj, dac, channels, freqs, amps, phases)


@dataclass
class FrequencyTones:
    def __init__(self, DACoffset, numtones, freq_center, freq_spacing, amplitude):
        self.DACoffset = DACoffset  # which dac is using in gm
        self.num_tones = numtones
        self.freq_center = freq_center
        self.freq_spacing = freq_spacing
        self.nominal_amplitude = amplitude

        self.tone_idx = np.arange(self.num_tones)
        self.freqs = self.freq_center + self.freq_spacing * \
            np.arange(-(self.num_tones-1)/2, self.num_tones/2, 1)
        # follows https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1054411 only works for equally spaced tones
        self.phases = np.pi*((self.tone_idx+1)**2)/(self.num_tones)
        self.phase_degs = np.round(self.phases*180/np.pi % 360, 1)
        self.init_amps = np.ones(self.num_tones)*self.nominal_amplitude
        self.opt_amps = self.init_amps.copy()

    def print_GM_Command(self):
        for ind in self.tone_idx:
            print('set DAC{:d} {:d} {:6.2f} {:6.2f} {:6.2f}'.format(
                0+self.DACoffset, ind, self.init_amps[ind], self.freqs[ind], self.phase_degs[ind]))

    def plotTimeTraces(self):
        t_list = np.linspace(0, 100e-6, int(100e-6*96e6*100)+1)
        rf_pulses = []
        rf_pulses_opt = []
        rf_pulses_naive = []
        for idx in self.tone_idx:
            rf_pulses.append(
                self.init_amps[idx]*np.sin(self.freqs[idx]*1e6*t_list + self.phases[idx]))
            rf_pulses_opt.append(
                self.opt_amps[idx]*np.sin(self.freqs[idx]*1e6*t_list + self.phases[idx]))
            rf_pulses_naive.append(
                self.init_amps[idx]*np.sin(self.freqs[idx]*1e6*t_list + 0))
        rf_pulse = np.array(rf_pulses).sum(axis=0)
        rf_pulses_opt = np.array(rf_pulses_opt).sum(axis=0)
        rf_pulse_naive = np.array(rf_pulses_naive).sum(axis=0)

        plt.plot(t_list, rf_pulse_naive, label=r'No peak reducing')
        plt.plot(t_list, rf_pulses_opt, label=r'Optmized')
        plt.plot(t_list, rf_pulse, label=r'Peak reducing, not optimized')
        plt.legend(loc='upper right')
        plt.show()


# gmoog = GM_python()
zclient = zynq_tcp_client()


imgs = []
def handler(cam: vimba.Camera, frame: vimba.Frame):
    print('Frame acquired : {} '. format(frame), flush=True)
    imgs.append(frame.as_numpy_ndarray())
    cam.queue_frame(frame)

def setup_camera(cam: vimba.Camera):
    with cam:
        # Try to adjust GeV packet size. This Feature is only available for GigE - Cameras.
        try:
            cam.load_settings(tweezer_moncam_setting, vimba.PersistType.NoLUT)
            cam.GVSPAdjustPacketSize.run()
            while not cam.GVSPAdjustPacketSize.is_done():
                pass
            cam.TriggerSelector.set('FrameStart')
            cam.TriggerMode.set('On')
            cam.TriggerSource.set('Software')
            cam.AcquisitionMode.set('Continuous')
        except (AttributeError, vimba.VimbaFeatureError, )  as err:
            print(err)
            print(err.args)

# vimba related example is at C:\Users\Public\Documents\Allied Vision\Vimba_4.2
with vimba.Vimba.get_instance() as vba:
    # with vba.get_camera_by_id(tweezer_moncam_ip) as cam:
    cam = vba.get_camera_by_id(tweezer_moncam_ip)
    print(cam.get_model())
    setup_camera(cam)
    cam.start_streaming(handler=handler)        
    for i in range(10):
        cam.TriggerSoftware.run()
        sleep(0.1)
    cam.stop_streaming()
        

plt.pcolormesh(np.array(imgs).mean(axis=0)[:,:,0])
plt.show()

print("Vimba version: {:s}".format(vimba.__version__))
# ft0 = FrequencyTones(0, 9, 98, 25.2/9, 28.3)
# ft1 = FrequencyTones(0, 9, 98, 25.2/9, 28.3)
# ft0.print_GM_Command()
# print()
# ft1.print_GM_Command()

# ft0.plotTimeTraces()
# ft1.plotTimeTraces()


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
