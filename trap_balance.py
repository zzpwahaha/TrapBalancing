import sys
import ctypes
from time import sleep
import h5py as h5
import numpy as np
import matplotlib.pyplot as plt

from GMoogProxy import GM_python
from frequency_tones import FrequencyTones
from zynq_client import zynq_tcp_client
from mako_camera import mako_camera
from tweezer_grid_2d import TweezerGrid2D
from miscellaneous import *

sys.path.append('C:\Chimera\B240_data_analysis\Library\ChimeraGenTools')
from AnalysisHelpers import findAtomLocs

tweezer_moncam_ip = '10.10.0.8'
tweezer_moncam_setting = './tweezer_monitor.xml'
trap_depth_datafile = 'trap_depth_2022-10-19.h5'

dac0_init_amp = np.array([27.92, 28.22, 28.32, 28.37, 28.47, 28.62, 28.92, 29.07, 29.17])
dac1_init_amp = np.array([26.92, 27.32, 27.42, 27.57, 27.82, 28.02, 28.42, 28.62, 28.87])
MAX_AMPLITUDE = 30.5


def trap_balancing():
    gmoog = GM_python()
    zclient = zynq_tcp_client()
    mako = mako_camera(ipaddr=tweezer_moncam_ip, settingAddr=tweezer_moncam_setting)
    
    freq_tones0 = FrequencyTones(0, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
    freq_tones0.set_initial_amps(dac0_init_amp)
    freq_tones1 = FrequencyTones(1, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
    freq_tones1.set_initial_amps(dac1_init_amp)
    
    optimizer = TweezerGrid2D(freq_axis0=freq_tones0,freq_axis1=freq_tones1, gmoog=gmoog)


    img_avg = mako.getAvgImages(num = 20, time_interval = 0.05, debug=True)
    maximaLocs = findAtomLocs(img_avg, window=None, neighborhood_size=95., threshold=16, sort='MatchArray', debug_plot=False)
    print(f"Found {len(maximaLocs):d} maximas", maximaLocs)

    trap_depth, trap_depth_uncertainty = getTrapDepthData(trap_data_file=trap_depth_datafile)
    print("Loaded trap depth:" , trap_depth)
    print(f"The maximum relative trap depth uncertainty is {np.max(trap_depth_uncertainty/trap_depth):2.2e}")
    
    twz_amps0 = getTweezerAmplitudes(img_avg, maximaLocs, amp_option='fit', showResult=False)
    print("Calculated tweezer amplitudes", twz_amps0)

    print("Start to balance the trap ... ")

    max_steps = 3
    current_step = 0
    err = 10
    # zclient.connect()
    while (err > 2.5) and (current_step < max_steps):
        print(f"****************************************step {current_step:d} start***************************************************")
        print(f"Performing optimization with step: {current_step:d}, error is {err:.2f}")
        img_avg = mako.getAvgImages(num = 20, time_interval = 0.05, debug=True)
        twz_amps = getTweezerAmplitudes(img_avg, maximaLocs, amp_option='fit', showResult=False)
        trap_depth_mapped = trap_depth / twz_amps0 * twz_amps
        if (err > 10):
            dac0_amp, dac1_amp, err = optimizer.getGMAmplitudes(
                trap_depth=unp.nominal_values(trap_depth_mapped), method='mean', ampscale=0*0.02, showPlot=False)
        else:
            dac0_amp, dac1_amp, err = optimizer.getGMAmplitudes(
                trap_depth=unp.nominal_values(trap_depth_mapped), method='randomCross', ampscale=0*0.001, showPlot=False)
        sleep(0.3)
        # zclient._triggerGigamoogWithTweezersOn()
        zclient.triggerGigamoog()
        print(f"****************************************step {current_step:d} end***************************************************")
        print("Max error: ", err)
        print("dac0 amplitude: ", dac0_amp)
        print("dac1 amplitude: ", dac1_amp)
        current_step += 1;
        sleep(2)
    # zclient.disconnect()


if __name__ == '__main__':
    trap_balancing()