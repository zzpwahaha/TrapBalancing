from cProfile import label
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

    # set the amplitude to init amp before any optimization, so that it is indepedent of previous run
    gmoog.zeroAll()
    freq_tones0.writeToGIGAMOOG(gmoog)
    freq_tones1.writeToGIGAMOOG(gmoog)
    gmoog.endMessage()
    sleep(1)
    zclient.triggerGigamoog()
    sleep(1)

    optimizer = TweezerGrid2D(freq_axis0=freq_tones0,freq_axis1=freq_tones1, gmoog=gmoog)
    drawer = realTimeDrawer()

    img_avg = mako.getAvgImages(num = 20, time_interval = 0.05, debug=False)
    # np.savetxt('./test/img_avg_init.txt',img_avg)
    maximaLocs = findAtomLocs(img_avg, window=None, neighborhood_size=95., threshold=16, sort='MatchArray', debug_plot=False)
    print(f"Found {len(maximaLocs):d} maximas", maximaLocs)

    trap_depth, trap_depth_uncertainty = getTrapDepthData(trap_data_file=trap_depth_datafile)
    print("Loaded trap depth:" , trap_depth)
    print(f"The maximum relative trap depth uncertainty is {np.max(trap_depth_uncertainty/trap_depth)*100:2.2f}%")

    # get the initial tweezer peak with the inital GM amplitude
    twz_amps0 = getTweezerAmplitudes(img_avg, maximaLocs, amp_option='fit', showResult=False)
    print("Calculated tweezer amplitudes", twz_amps0)

    print("Start to balance the trap ... ")

    max_steps = 200
    current_step = 0
    err = np.abs((trap_depth - trap_depth.mean()) / trap_depth.mean()).max() * 100
    err_store = []
    
    with open('./result/result.txt', 'w') as f:
        f.close()

    while (err > 2.5) and (current_step < max_steps):
        print(f"****************************************step {current_step:d} start***************************************************")
        print(f"Performing optimization with step: {current_step:d}, error is {err:.2f}")
        img_avg = mako.getAvgImages(num = 20, time_interval = 0.05, debug=False)
        twz_amps = getTweezerAmplitudes(img_avg, maximaLocs, amp_option='fit', showResult=False)
        trap_depth_mapped = trap_depth / twz_amps0 * twz_amps
        if (err > 25):
            dac0_amp, dac1_amp, allerr = optimizer.getGMAmplitudes(
                trap_depth=unp.nominal_values(trap_depth_mapped), method='cross', ampscale=0.5, showPlot=False)
        elif (err>18):
            dac0_amp, dac1_amp, allerr = optimizer.getGMAmplitudes(
                trap_depth=unp.nominal_values(trap_depth_mapped), method='randomCross', ampscale=1, showPlot=False)
        else:
            dac0_amp, dac1_amp, allerr = optimizer.getGMAmplitudes(
                trap_depth=unp.nominal_values(trap_depth_mapped), method='randomCross', ampscale=2, showPlot=False)
        sleep(0.1)
        # zclient._triggerGigamoogWithTweezersOn()
        zclient.triggerGigamoog()

        err_store.append(allerr)
        err = np.abs(allerr).max()
        print(f"****************************************step {current_step:d} end***************************************************")
        print("Max error: ", err)
        print("dac0 amplitude: ", dac0_amp)
        print("dac1 amplitude: ", dac1_amp)
        drawer.updateXY(np.arange(allerr.size), allerr.flatten(), type='trap_depth')
        drawer.updateXY([np.arange(dac0_amp.size), np.arange(dac0_amp.size)], [dac0_amp, dac1_amp], type='dac_output')
        drawer.updateXY([np.arange(current_step+1), np.arange(current_step+1)], [np.max(np.abs(err_store), axis=(1,2)), np.std(err_store, axis=(1,2))], type='history')
        drawer.fig.suptitle(f"Step #{current_step+1:d}")

        with open('./result/result.txt', 'a') as f:
            f.write(f"Step #{current_step+1:d}\r\n")
            for cmd in freq_tones0.get_GM_Command():
                f.write(cmd+"\r")
            for cmd in freq_tones1.get_GM_Command():
                f.write(cmd+"\r")
            f.write('\r\n')

        current_step += 1;
        sleep(1)
    input("Press Enter to exit...")
    

def evaluateTrapDepthResult():
    # dac0_opt_amp = [30.33, 26.05, 22.33, 27.06, 28.60, 30.50, 29.82, 23.84, 27.93]
    # dac1_opt_amp = [22.08, 23.89, 28.33, 30.50, 28.85, 25.17, 22.23, 26.20, 30.38]

    # gmoog = GM_python()
    # zclient = zynq_tcp_client()
    
    # freq_tones0 = FrequencyTones(0, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
    # freq_tones0.set_initial_amps(dac0_opt_amp)
    # freq_tones1 = FrequencyTones(1, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
    # freq_tones1.set_initial_amps(dac1_opt_amp)

    # # set the amplitude to init amp before any optimization, so that it is indepedent of previous run
    # gmoog.zeroAll()
    # freq_tones0.writeToGIGAMOOG(gmoog)
    # freq_tones1.writeToGIGAMOOG(gmoog)
    # gmoog.endMessage()


    mako = mako_camera(ipaddr=tweezer_moncam_ip, settingAddr=tweezer_moncam_setting)
    img_avg0 = mako.getAvgImages(debug=True)
    maximaLocs = findAtomLocs(img_avg0, window=None, neighborhood_size=95., threshold=16, sort='MatchArray', debug_plot=False)
    twz_amps0 = getTweezerAmplitudes(img_avg0, maximaLocs, amp_option='fit', showResult=False)
    # twz_amps0 = unp.nominal_values(twz_amps0)

    img_avg = mako.getAvgImages(num = 20, time_interval = 0.05, debug=False)
    twz_amps = getTweezerAmplitudes(img_avg, maximaLocs, amp_option='fit', showResult=False)
    # plt.plot(unp.nominal_values(twz_amps0))
    # plt.plot(unp.nominal_values(twz_amps))
    # plt.show()

    trap_depth, trap_depth_uncertainty = getTrapDepthData(trap_data_file=trap_depth_datafile)
    trap_depth_mapped = unp.nominal_values(trap_depth / twz_amps0 * twz_amps)
    # trap_depth_mapped = unp.nominal_values(trap_depth_mapped)
    allerr = (trap_depth_mapped.reshape([9,9])[::-1,:] - trap_depth_mapped.mean()) / trap_depth_mapped.mean() * 100
    print("All errors: ", allerr)
    plt.plot(np.arange(allerr.size), allerr.flatten(), label='current')
    plt.plot(np.arange(allerr.size), (trap_depth.reshape([9,9])[::-1,:] - trap_depth.mean()).flatten()/trap_depth.mean()*100, label='initial')
    plt.legend()
    plt.show()





if __name__ == '__main__':
    trap_balancing()
    # evaluateTrapDepthResult()