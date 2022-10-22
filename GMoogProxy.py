import ctypes
from time import sleep
from zynq_client import zynq_tcp_client
import frequency_tones as ft
import numpy as np
from uncertainties import unumpy as unp
from miscellaneous import getTrapDepthData

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

        gmoogLib.gm_zeroAndSetDAC.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(
            ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
        gmoogLib.gm_zeroAndSetDAC.restype = ctypes.c_void_p

        gmoogLib.gm_zeroAndSetTwoDACs.argtypes = [ctypes.c_void_p, 
            ctypes.c_int, ctypes.c_int, ctypes.POINTER(
            ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
            ctypes.c_int, ctypes.c_int, ctypes.POINTER(
            ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
        gmoogLib.gm_zeroAndSetTwoDACs.restype = ctypes.c_void_p

        self.obj = gmoogLib.gm_new()

    # def test(self):
    #     gmoogLib.gm_test(self.obj)

    def zeroAll(self):
        gmoogLib.gm_zeroAll(self.obj)

    def endMessage(self):
        gmoogLib.gm_endMessage(self.obj)

    def setDAC(self, dac, channels, freqs, amps, phases):
        gmoogLib.gm_setDAC(self.obj, dac, channels, freqs, amps, phases)

    def zeroAndsetTwoDACs(self, dac0, channels0, freqs0, amps0, phases0, dac1, channels1, freqs1, amps1, phases1):
        gmoogLib.gm_zeroAndSetTwoDACs(self.obj, dac0, channels0, freqs0, amps0, phases0, dac1, channels1, freqs1, amps1, phases1)

def test_with_bare_command():
    DACoffset =  0
    num_tones =  9

    freqs0 =  np.array([ 86.8, 89.6, 92.4, 95.2, 98. ,100.8,103.6,106.4,109.2])
    opt_amps0 =  np.array([27.92,28.22,28.32,28.37,28.47,28.62,28.92,29.07,29.17])
    phase_degs0 =  np.array([ 20., 80.,180.,320.,140.,  0.,260.,200.,180.]) #/180*3.14

    freqs1 =  np.array([ 86.8, 89.6, 92.4, 95.2, 98. ,100.8,103.6,106.4,109.2])
    opt_amps1 =  np.array([26.92,27.32,27.42,27.57,27.82,28.02,28.42,28.62,28.87])
    phase_degs1 =  np.array([ 20., 80.,180.,320.,140.,  0.,260.,200.,180.]) #/180*3.14

    gmoog = GM_python()
    client = zynq_tcp_client()

    seq = ctypes.c_float * num_tones
    
    # gmoog.zeroAll()
    # sleep(0.5)
    # gmoog.setDAC(dac=DACoffset, channels=num_tones, freqs=seq(*freqs0), amps=seq(*opt_amps0), phases=seq(*phase_degs))
    # sleep(0.5)
    # gmoog.setDAC(dac=DACoffset+1, channels=num_tones, freqs=seq(*freqs1), amps=seq(*opt_amps1), phases=seq(*phase_degs))
    # sleep(0.5)
    # gmoog.endMessage()
    # sleep(0.5)

    gmoog.zeroAndsetTwoDACs(
        dac0=DACoffset, channels0=num_tones, freqs0=seq(*freqs0), amps0=seq(*opt_amps0), phases0=seq(*phase_degs0),
        dac1=DACoffset+1, channels1=num_tones, freqs1=seq(*freqs1), amps1=seq(*opt_amps1), phases1=seq(*phase_degs1))

    sleep(0.1)
    client.triggerGigamoog()

    for ind in np.arange(num_tones):
        print('set', "DAC"+str(0+DACoffset), ind, opt_amps0[ind], freqs0[ind], phase_degs0[ind])

    print()

    for ind in np.arange(num_tones):
        print('set', "DAC"+str(1+DACoffset), ind, opt_amps1[ind], freqs1[ind], phase_degs1[ind])

def test_with_FreqTones_class():
    MAX_AMPLITUDE = 30.5
    dac0_init_amp = np.array([27.92, 28.22, 28.32, 28.37, 28.47, 28.62, 28.92, 29.07, 29.17])
    dac1_init_amp = np.array([26.92, 27.32, 27.42, 27.57, 27.82, 28.02, 28.42, 28.62, 28.87])
    
    freq_tones0 = ft.FrequencyTones(0, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
    freq_tones0.set_initial_amps(dac0_init_amp)
    freq_tones1 = ft.FrequencyTones(1, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
    freq_tones1.set_initial_amps(dac1_init_amp)

    gmoog = GM_python()
    client = zynq_tcp_client()
    
    gmoog.zeroAll()
    freq_tones0.writeToGIGAMOOG(gmoog=gmoog)
    freq_tones1.writeToGIGAMOOG(gmoog=gmoog)
    gmoog.endMessage()
    sleep(0.1)
    client.triggerGigamoog()

def test_with_optimizer():
    import tweezer_grid_2d as op
    MAX_AMPLITUDE = 30.5
    dac0_init_amp = np.array([27.92, 28.22, 28.32, 28.37, 28.47, 28.62, 28.92, 29.07, 29.17])
    dac1_init_amp = np.array([26.92, 27.32, 27.42, 27.57, 27.82, 28.02, 28.42, 28.62, 28.87])
    
    freq_tones0 = ft.FrequencyTones(0, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
    freq_tones0.set_initial_amps(dac0_init_amp)
    freq_tones1 = ft.FrequencyTones(1, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
    freq_tones1.set_initial_amps(dac1_init_amp)

    trap_depth, trap_depth_uncertainty = getTrapDepthData(trap_data_file='trap_depth_2022-10-19.h5')
    trap_depth_mapped = trap_depth

    gmoog = GM_python()
    client = zynq_tcp_client()

    optimizer = op.TweezerGrid2D(freq_axis0=freq_tones0,freq_axis1=freq_tones1, gmoog=gmoog)
    dac0_amp, dac1_amp, err = optimizer.getGMAmplitudes(
                trap_depth=unp.nominal_values(trap_depth_mapped), method='mean', ampscale=0*0.02, showPlot=False)
    sleep(0.1)
    client.triggerGigamoog()

if __name__ == '__main__':
    test_with_bare_command()
    # test_with_FreqTones_class()
    # test_with_optimizer()
