from cProfile import label
import sys
import ctypes
from time import gmtime, sleep, time
from datetime import timedelta
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
tweezer_moncam_setting = './tweezer_monitor_20250413_1x13.xml'

# trap_depth_datafile = 'trap_depth_2022-10-19.h5'
# dac0_init_amp = np.array([27.92, 28.22, 28.32, 28.37, 28.47, 28.62, 28.92, 29.07, 29.17])
# dac1_init_amp = np.array([26.92, 27.32, 27.42, 27.57, 27.82, 28.02, 28.42, 28.62, 28.87])
# MAX_AMPLITUDE = 30.8
# freq_tones0 = FrequencyTones.fromFixedFrequencySpacing(0, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
# freq_tones0.set_initial_amps(dac0_init_amp)
# freq_tones1 = FrequencyTones.fromFixedFrequencySpacing(1, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
# freq_tones1.set_initial_amps(dac1_init_amp)

# 2023/03/23 trap depth balancing for 2x9 grid
# GRID = [2,9]
# trap_depth_datafile = 'trap_depth_2023-3-23.h5'
# dac0_init_amp = np.array([30.67, 27.82, 25.83, 26.10, 28.02, 30.19, 30.78, 28.63, 28.14])
# dac1_init_amp = np.array([30.79, 30.75])
# MAX_AMPLITUDE = 31
# freq_tones0 = FrequencyTones(DACoffset=0, numtones=2, 
#                              freqs=np.array([86.80, 88.00, 89.60, 91.60, 94.00, 96.80, 100.00, 103.60, 107.60]),
#                              phases=np.array([3, 66, 169, 251, 322, 315, 353, 0, 0]), 
#                              amplitude=28.3, max_amp= MAX_AMPLITUDE)
# freq_tones0.set_initial_amps(dac0_init_amp)
# freq_tones1 = FrequencyTones(DACoffset=1, numtones=2, 
#                              freqs=np.array([91.6, 103.6]),
#                              phases=np.array([251, 0]), 
#                              amplitude=28.3, max_amp= MAX_AMPLITUDE)
# freq_tones1.set_initial_amps(dac1_init_amp)


# 2023/03/24 trap depth balancing for 2x2 grid
# GRID = [2,2]
# trap_depth_datafile = 'trap_depth_2023-3-24.h5'
# dac0_init_amp = np.array([24.6, 25.06])
# dac1_init_amp = np.array([25.49, 25.99])
# MAX_AMPLITUDE = 31
# freq_tones0 = FrequencyTones(DACoffset=0, numtones=2, 
#                              freqs=np.array([94.00, 103.6]),
#                              phases=np.array([89.2, 0]), 
#                              amplitude=28.3, max_amp= MAX_AMPLITUDE)
# freq_tones0.set_initial_amps(dac0_init_amp)
# freq_tones1 = FrequencyTones(DACoffset=1, numtones=2, 
#                              freqs=np.array([91.6, 103.6]),
#                              phases=np.array([341.2, 0]), 
#                              amplitude=28.3, max_amp= MAX_AMPLITUDE)
# freq_tones1.set_initial_amps(dac1_init_amp)

# 2023/03/24 trap depth balancing for 2x9 grid
# GRID = [2,2]
# trap_depth_datafile = 'trap_depth_2023-8-31.h5'
# dac0_init_amp = np.array([25.59, 25.63, 24.55, 23.94, 22.81, 23.82, 25.19, 26.20, 25.54])
# dac1_init_amp = np.array([26.57, 27.01])
# MAX_AMPLITUDE = 31
# freq_tones0 = FrequencyTones(DACoffset=0, numtones=9, 
#                              freqs=np.array([86.80, 88.00, 89.60, 91.60, 94.00, 96.80, 100.00, 103.60, 107.60]),
#                              phases=np.array([171.90, 181.50, 323.00, 341.20, 89.20, 48.20, 65.40, 0.00, 0.00]), 
#                              amplitude=28.3, max_amp= MAX_AMPLITUDE)
# freq_tones0.set_initial_amps(dac0_init_amp)
# freq_tones1 = FrequencyTones(DACoffset=1, numtones=2, 
#                              freqs=np.array([91.6, 103.6]),
#                              phases=np.array([341.2, 0]), 
#                              amplitude=28.3, max_amp= MAX_AMPLITUDE)
# freq_tones1.set_initial_amps(dac1_init_amp)

# 2023/09/26 trap depth balancing for 5x5 grid
# GRID = [5,5]
# trap_depth_datafile = 'trap_depth_2023-9-26.h5'
# dac0_init_amp = np.array([100,100,100,100,100])
# dac1_init_amp = np.array([100,100,100,100,100])
# MAX_AMPLITUDE = 100
# freq_tones0 = FrequencyTones(DACoffset=0, numtones=5, 
#                              freqs=np.array([87.60, 91.20, 96.00, 98.40, 105.60]),
#                              phases=np.array([0.63, 2.51, 22.62, 40.21, 123.15]), 
#                              amplitude=28.3, max_amp= MAX_AMPLITUDE, repeat=2)
# freq_tones0.set_initial_amps(dac0_init_amp)
# freq_tones1 = FrequencyTones(DACoffset=1, numtones=5, 
#                              freqs=np.array([87.60, 91.20, 96.00, 98.40, 105.60]),
#                              phases=np.array([0.63, 2.51, 22.62, 40.21, 123.15]), 
#                              amplitude=28.3, max_amp= MAX_AMPLITUDE, repeat=2)
# freq_tones1.set_initial_amps(dac1_init_amp)

# 2024/05/15 trap depth balancing for 1x13 grid
# GRID = [1,13]
# trap_depth_datafile = 'trap_depth_2024-5-15.h5'
# dac0_init_amp = np.array([95,95,95,95,95,95,95,95,95,95,95,95,95])
# dac1_init_amp = np.array([95])
# MAX_AMPLITUDE = 100
# freq_tones0 = FrequencyTones(DACoffset=0, numtones=13, 
#                              freqs=np.array([ 80.,  83.,  86.,  89.,  92.,  95.,  98., 101., 104., 107., 110., 113., 116.]),
#                              phases=np.array([ 13.8,  55.4, 124.6, 221.5, 346.2, 138.5, 318.5, 166.2,  41.5, 304.6, 235.4, 193.8, 180. ]), 
#                              amplitude=0.0, max_amp= MAX_AMPLITUDE, repeat=2)
# freq_tones0.set_initial_amps(dac0_init_amp)
# freq_tones1 = FrequencyTones(DACoffset=1, numtones=1, 
#                              freqs=np.array([98]),
#                              phases=np.array([0.0]), 
#                              amplitude=0.0, max_amp= MAX_AMPLITUDE, repeat=4)
# freq_tones1.set_initial_amps(dac1_init_amp)
# GRID = [1,13]
# trap_depth_datafile = 'trap_depth_2024-5-15-round2.h5'
# dac0_init_amp = np.array([69.77, 74.35, 82.96, 84.14, 74.32, 66.27, 71.61, 86.20, 100.00, 88.44, 77.74, 74.36, 91.09])
# dac1_init_amp = np.array([95.00])
# MAX_AMPLITUDE = 100
# freq_tones0 = FrequencyTones(DACoffset=0, numtones=13, 
#                              freqs=np.array([ 80.00, 83.00, 86.00, 89.00, 92.00, 95.00, 98.00, 101.00, 104.00, 107.00, 110.00, 113.00, 116.00]),
#                              phases=np.array([ 70.70, 294.20, 299.10, 91.00, 35.80, 15.50, 248.70, 162.60, 217.80, 172.30, 167.40, 303.90, 233.20 ]), 
#                              amplitude=0.0, max_amp= MAX_AMPLITUDE, repeat=2)
# freq_tones0.set_initial_amps(dac0_init_amp)
# freq_tones1 = FrequencyTones(DACoffset=1, numtones=1, 
#                              freqs=np.array([98]),
#                              phases=np.array([0.0]), 
#                              amplitude=0.0, max_amp= MAX_AMPLITUDE, repeat=4)
# freq_tones1.set_initial_amps(dac1_init_amp)
# GRID = [1,13]
# trap_depth_datafile = 'trap_depth_2024-5-15-round3.h5'
# dac0_init_amp = np.array([72.20, 74.17, 77.99, 80.78, 76.55, 68.98, 75.21, 87.68, 89.66, 90.72, 76.00, 76.74, 94.56])
# dac1_init_amp = np.array([95.00])
# MAX_AMPLITUDE = 100
# freq_tones0 = FrequencyTones(DACoffset=0, numtones=13, 
#                              freqs=np.array([ 80.00, 83.00, 86.00, 89.00, 92.00, 95.00, 98.00, 101.00, 104.00, 107.00, 110.00, 113.00, 116.00]),
#                              phases=np.array([ 70.80, 296.40, 217.20, 173.90, 251.20, 168.10, 209.50, 316.30, 239.00, 152.10, 231.30, 132.20, 41.40 ]), 
#                              amplitude=0.0, max_amp= MAX_AMPLITUDE, repeat=2)
# freq_tones0.set_initial_amps(dac0_init_amp)
# freq_tones1 = FrequencyTones(DACoffset=1, numtones=1, 
#                              freqs=np.array([98]),
#                              phases=np.array([0.0]), 
#                              amplitude=0.0, max_amp= MAX_AMPLITUDE, repeat=4)
# freq_tones1.set_initial_amps(dac1_init_amp)
# GRID = [1,13]
# trap_depth_datafile = 'trap_depth_2024-5-16-round4.h5'
# dac0_init_amp = np.array([68.84, 76.70, 82.39, 78.80, 74.11, 68.28, 69.93, 83.12, 96.67, 88.41, 76.78, 83.27, 93.94])
# dac1_init_amp = np.array([95.00])
# MAX_AMPLITUDE = 100
# freq_tones0 = FrequencyTones(DACoffset=0, numtones=13, 
#                              freqs=np.array([ 80.00, 83.00, 86.00, 89.00, 92.00, 95.00, 98.00, 101.00, 104.00, 107.00, 110.00, 113.00, 116.00]),
#                              phases=np.array([ 13.8,  55.4, 124.6, 221.5, 346.2, 138.5, 318.5, 166.2,  41.5, 304.6, 235.4, 193.8, 180. ]), 
#                              amplitude=0.0, max_amp= MAX_AMPLITUDE, repeat=2)
# freq_tones0.set_initial_amps(dac0_init_amp)
# freq_tones1 = FrequencyTones(DACoffset=1, numtones=1, 
#                              freqs=np.array([98]),
#                              phases=np.array([0.0]), 
#                              amplitude=0.0, max_amp= MAX_AMPLITUDE, repeat=4)
# freq_tones1.set_initial_amps(dac1_init_amp)
# GRID = [1,13]
# trap_depth_datafile = 'trap_depth_2024-5-16-round5.h5'
# dac0_init_amp = np.array([70.50, 75.79, 83.02, 82.18, 74.48, 69.90, 74.14, 86.33, 92.70, 88.02, 78.43, 74.40, 91.38])
# dac1_init_amp = np.array([95.00])
# MAX_AMPLITUDE = 100
# freq_tones0 = FrequencyTones(DACoffset=0, numtones=13, 
#                              freqs=np.array([ 80.00, 83.00, 86.00, 89.00, 92.00, 95.00, 98.00, 101.00, 104.00, 107.00, 110.00, 113.00, 116.00]),
#                              phases=np.array([ 13.8,  55.4, 124.6, 221.5, 346.2, 138.5, 318.5, 166.2,  41.5, 304.6, 235.4, 193.8, 180. ]), 
#                              amplitude=0.0, max_amp= MAX_AMPLITUDE, repeat=2)
# freq_tones0.set_initial_amps(dac0_init_amp)
# freq_tones1 = FrequencyTones(DACoffset=1, numtones=1, 
#                              freqs=np.array([98]),
#                              phases=np.array([0.0]), 
#                              amplitude=0.0, max_amp= MAX_AMPLITUDE, repeat=4)
# freq_tones1.set_initial_amps(dac1_init_amp)

GRID = [1,13]
trap_depth_datafile = 'trap_depth_2025-4-13.h5'
dac0_init_amp = np.array([72.42, 74.52, 81.02, 82.33, 74.60, 66.77, 74.23, 87.94, 94.54, 88.74, 76.99, 76.47, 90.71])
dac1_init_amp = np.array([95.00])
MAX_AMPLITUDE = 100
freq_tones0 = FrequencyTones(DACoffset=0, numtones=13, 
                             freqs=np.array([ 80.00, 83.00, 86.00, 89.00, 92.00, 95.00, 98.00, 101.00, 104.00, 107.00, 110.00, 113.00, 116.00]),
                             phases=np.array([ 13.8,  55.4, 124.6, 221.5, 346.2, 138.5, 318.5, 166.2,  41.5, 304.6, 235.4, 193.8, 180. ]), 
                             amplitude=0.0, max_amp= MAX_AMPLITUDE, repeat=2)
freq_tones0.set_initial_amps(dac0_init_amp)
freq_tones1 = FrequencyTones(DACoffset=1, numtones=1, 
                             freqs=np.array([98]),
                             phases=np.array([0.0]), 
                             amplitude=0.0, max_amp= MAX_AMPLITUDE, repeat=6)
freq_tones1.set_initial_amps(dac1_init_amp)



def writeTwoTonesToGIGAMOOG(freq_tones0:FrequencyTones, freq_tones1:FrequencyTones, gmoog:GM_python, zclient:zynq_tcp_client):
    gmoog.zeroAll()
    freq_tones0.writeToGIGAMOOG(gmoog)
    freq_tones1.writeToGIGAMOOG(gmoog)
    gmoog.endMessage()
    sleep(1)
    zclient.triggerGigamoog()

def trap_balancing():
    gmoog = GM_python()
    zclient = zynq_tcp_client()
    mako = mako_camera(ipaddr=tweezer_moncam_ip, settingAddr=tweezer_moncam_setting)
    
    # freq_tones0 = FrequencyTones(0, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
    # freq_tones0.set_initial_amps(dac0_init_amp)
    # freq_tones1 = FrequencyTones(1, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
    # freq_tones1.set_initial_amps(dac1_init_amp)


    # set the amplitude to init amp before any optimization, so that it is indepedent of previous run
    writeTwoTonesToGIGAMOOG(freq_tones0=freq_tones0,freq_tones1=freq_tones1, gmoog=gmoog, zclient=zclient)
    sleep(1)

    optimizer = TweezerGrid2D(freq_axis0=freq_tones0,freq_axis1=freq_tones1, gmoog=gmoog)
    drawer = realTimeDrawer()
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    drawer.updateXY([np.arange(dac0_init_amp.size), np.arange(dac1_init_amp.size)], [dac0_init_amp, dac1_init_amp], type='dac_output')

    img_avg = mako.getAvgImages(num = 20, time_interval = 0.05, debug=False)
    # hardcode maximaLocs, since the findAtomlocs function somehow takes a lot of time
    maximaLocs = \
        [(121, 49), (199, 49), (277, 49), (355, 49), (434, 49), (512, 49), (590, 49), (669, 49), (748, 50), (826, 50), (905, 50), (984, 50), (1064, 50)]
        # [(114, 48), (190, 48), (266, 48), (342, 48), (418, 48), (495, 48), (571, 48), (648, 48), (724, 48), (801, 48), (878, 48), (955, 48), (1032, 48)]
        #[[79, 82], [171, 83], [293, 83], [354, 83], [538, 83], [81, 267], [172, 267], [294, 267], [356, 267], [540, 267], [81, 329], [173, 328], [295, 329], [356, 329], [540, 329], [82, 451], [174, 451], [296, 451], [357, 451], [541, 451], [83, 543], [174, 543], [297, 543], [358, 543], [542, 543]]
        #[[280, 277], [311, 277], [353, 277], [406, 277], [469, 277], [542, 277], [626, 277], [721, 277], [827, 277], [282, 593], [314, 593], [356, 593], [408, 593], [471, 593], [544, 593], [629, 593], [724, 593], [829, 593]]
        # findAtomLocs(img_avg, window=None, neighborhood_size=95., threshold=16, sort='MatchArray', debug_plot=False, n_cluster_row=2,
        #                       advanced_option = dict({"active":True, "image_threshold":1000, "score_threshold":100}))
        # np.array([[160, 304], [191, 304], [233, 304], [285, 305], [348, 304], [421, 305], [505, 305], [599, 305], [704, 305], [161, 619], [193, 619], [235, 619], [287, 619], [349, 619], [423, 620], [506, 620], [601, 620], [706, 620]])
        # np.array([[350, 301], [602, 302], [352, 616], [603, 617]])

    drawer.updateMaximaLocs(pic = img_avg, maximaLocs= maximaLocs, window=None)
    print(f"Found {len(maximaLocs):d} maximas", maximaLocs)
    # np.savetxt('./test/img_avg_withWrongLocs.txt',img_avg)

    trap_depth, trap_depth_uncertainty = getTrapDepthData(trap_data_file=trap_depth_datafile)
    print("Loaded trap depth:" , trap_depth)
    print(f"The maximum relative trap depth uncertainty is {np.max(trap_depth_uncertainty/trap_depth)*100:2.2f}%")

    # get the initial tweezer peak with the inital GM amplitude
    twz_amps0 = getTweezerAmplitudes(img_avg, maximaLocs, amp_option='fit', showResult=False)
    drawer.updateXY(np.arange(twz_amps0.size) ,unp.nominal_values(twz_amps0).reshape(freq_tones1.num_tones, freq_tones0.num_tones)[::-1,:].flatten(), type='twz_amp')
    print("Calculated tweezer amplitudes", twz_amps0)

    print("Start to balance the trap ... ")

    max_steps = 5000
    current_step = 0
    err = np.abs((trap_depth - trap_depth.mean()) / trap_depth.mean()).max() * 100
    err_store = []

    with open('./result/result.txt', 'w') as f:
        f.close()
    start_time = time()
    while (err > 0.1) and (current_step < max_steps):
        if (current_step + 1) % 10 == 0:
            print(f"****************** Check tweezer monitor camera amlitude by going back to init amp********************")
            dac0_opt_amp = freq_tones0.opt_amps
            dac1_opt_amp = freq_tones1.opt_amps
            freq_tones0.updateOptimalAmps(dac0_init_amp)
            freq_tones1.updateOptimalAmps(dac1_init_amp)
            writeTwoTonesToGIGAMOOG(freq_tones0=freq_tones0,freq_tones1=freq_tones1, gmoog=gmoog, zclient=zclient)
            sleep(1)

            img_avg = mako.getAvgImages(num = 20, time_interval = 0.05, debug=False)
            twz_amps0 = getTweezerAmplitudes(img_avg, maximaLocs, amp_option='fit', showResult=False)
            drawer.updateXY(np.arange(twz_amps0.size) ,unp.nominal_values(twz_amps0).reshape(freq_tones1.num_tones, freq_tones0.num_tones)[::-1,:].flatten(), type='twz_amp')

            print("Finishing checking, writing back the previous optimal DAC control amplitude")
            print("DAC0 check: ", freq_tones0.opt_amps)
            print("DAC1 check: ", freq_tones1.opt_amps)
            freq_tones0.updateOptimalAmps(dac0_opt_amp)
            freq_tones1.updateOptimalAmps(dac1_opt_amp)
            writeTwoTonesToGIGAMOOG(freq_tones0=freq_tones0,freq_tones1=freq_tones1, gmoog=gmoog, zclient=zclient)
            print("DAC0 after check: ", freq_tones0.opt_amps)
            print("DAC1 after check: ", freq_tones1.opt_amps)
            sleep(1)
            

        print(f"****************************************step {current_step:d} start***************************************************")
        print(f"Performing optimization with step: {current_step:d}, error is {err:.2f}")
        img_avg = mako.getAvgImages(num = 20, time_interval = 0.05, debug=False)
        twz_amps = getTweezerAmplitudes(img_avg, maximaLocs, amp_option='fit', showResult=False)
        trap_depth_mapped = trap_depth / twz_amps0 * twz_amps
        if (err > 25):
            dac0_amp, dac1_amp, allerr = optimizer.getGMAmplitudes(
                trap_depth=unp.nominal_values(trap_depth_mapped), method='mean', ampscale=10, showPlot=False)
        elif (err>15):
            dac0_amp, dac1_amp, allerr = optimizer.getGMAmplitudes(
                trap_depth=unp.nominal_values(trap_depth_mapped), method='mean', ampscale=5, showPlot=False)
        elif (err>2):
            dac0_amp, dac1_amp, allerr = optimizer.getGMAmplitudes(
                trap_depth=unp.nominal_values(trap_depth_mapped), method='mean', ampscale=3, showPlot=False)
        else:
            dac0_amp, dac1_amp, allerr = optimizer.getGMAmplitudes(
                trap_depth=unp.nominal_values(trap_depth_mapped), method='mean', ampscale=1, showPlot=False)
        sleep(0.1)
        # zclient._triggerGigamoogWithTweezersOn()
        zclient.triggerGigamoog()

        err_store.append(allerr)
        err = np.abs(allerr).max()
        print(f"****************************************step {current_step:d} end at time: {str(timedelta(seconds=time()-start_time)):s}************************************")
        print("Max error: ", err)
        print("dac0 amplitude: ", dac0_amp)
        print("dac1 amplitude: ", dac1_amp)
        drawer.updateXY(np.arange(allerr.size), allerr.flatten(), type='trap_depth')
        drawer.updateXY([np.arange(dac0_amp.size), np.arange(dac1_amp.size)], [dac0_amp, dac1_amp], type='dac_output')
        drawer.updateXY([np.arange(current_step+1), np.arange(current_step+1)], [np.max(np.abs(err_store), axis=(1,2)), np.std(err_store, axis=(1,2))], type='history')
        drawer.fig.suptitle(f"Step #{current_step+1:d} at time: {str(timedelta(seconds=time()-start_time)):s}")

        with open('./result/result.txt', 'a') as f:
            f.write(f"Step #{current_step+1:d} max_err = {err:.2f}\r\n")
            for cmd in freq_tones0.get_GM_Command():
                f.write(cmd+"\r")
            for cmd in freq_tones1.get_GM_Command():
                f.write(cmd+"\r")
            f.write('\r\n')

        current_step += 1;
        sleep(0.5)
    input("Press Enter to exit...")
    

def evaluateTrapDepthResult():
    dac0_opt_amp = np.array([30.41, 27.63, 25.70, 25.90, 27.76, 30.14, 30.50, 28.44, 27.94])
    dac1_opt_amp = np.array([24.97, 25.72, 28.23, 30.50, 30.22, 27.88, 26.23, 25.85, 30.00])

    dac1_opt_amp = np.array([30.35, 27.58, 25.61, 26.00, 27.92, 30.06, 30.49, 28.46, 28.13])
    dac1_opt_amp = np.array([25.04, 25.71, 28.12, 30.50, 30.13, 27.80, 26.17, 25.71, 29.83])

    gmoog = GM_python()
    zclient = zynq_tcp_client()
    
    freq_tones0 = FrequencyTones(0, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
    freq_tones1 = FrequencyTones(1, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
    freq_tones0.set_initial_amps(dac0_init_amp)
    freq_tones1.set_initial_amps(dac1_init_amp)

    # set the amplitude to init amp before any optimization, so that it is indepedent of previous run
    writeTwoTonesToGIGAMOOG(freq_tones0=freq_tones0,freq_tones1=freq_tones1, gmoog=gmoog, zclient=zclient)
    # sleep(10)

    mako = mako_camera(ipaddr=tweezer_moncam_ip, settingAddr=tweezer_moncam_setting)
    img_avg0 = mako.getAvgImages(debug=True)
    maximaLocs = findAtomLocs(img_avg0, window=None, neighborhood_size=95., threshold=16, sort='MatchArray', debug_plot=False)
    twz_amps0 = getTweezerAmplitudes(img_avg0, maximaLocs, amp_option='fit', showResult=False)
    # twz_amps0 = unp.nominal_values(twz_amps0)

    img_avg0_cam = mako.getAvgImages(num = 20, time_interval = 0.05, debug=False)
    twz_amps0_cam = getTweezerAmplitudes(img_avg0_cam, maximaLocs, amp_option='fit', showResult=False)
    plt.plot(unp.nominal_values(twz_amps0), label=r'initial amp fit in file')
    plt.plot(unp.nominal_values(twz_amps0_cam), label = 'current amp fit from camera')
    plt.legend()
    plt.show()


    freq_tones0.set_initial_amps(dac0_opt_amp)
    freq_tones1.set_initial_amps(dac1_opt_amp)
    # set the amplitude to init amp before any optimization, so that it is indepedent of previous run
    writeTwoTonesToGIGAMOOG(freq_tones0=freq_tones0,freq_tones1=freq_tones1, gmoog=gmoog, zclient=zclient)

    img_avg = mako.getAvgImages(num = 20, time_interval = 0.05, debug=False)
    twz_amps = getTweezerAmplitudes(img_avg, maximaLocs, amp_option='fit', showResult=False)
    trap_depth, trap_depth_uncertainty = getTrapDepthData(trap_data_file=trap_depth_datafile)
    trap_depth_mapped = unp.nominal_values(trap_depth / twz_amps0 * twz_amps)
    # trap_depth_mapped = unp.nominal_values(trap_depth_mapped)
    allerr = (trap_depth_mapped.reshape([9,9])[::-1,:] - trap_depth_mapped.mean()) / trap_depth_mapped.mean() * 100
    print("All errors: ", allerr)
    plt.plot(np.arange(allerr.size), allerr.flatten(), label='current')
    plt.plot(np.arange(allerr.size), (trap_depth.reshape([9,9])[::-1,:] - trap_depth.mean()).flatten()/trap_depth.mean()*100, label='initial')

    trap_depth_mapped_cam = unp.nominal_values(trap_depth / twz_amps0_cam * twz_amps)
    # trap_depth_mapped = unp.nominal_values(trap_depth_mapped)
    allerr = (trap_depth_mapped_cam.reshape([9,9])[::-1,:] - trap_depth_mapped_cam.mean()) / trap_depth_mapped_cam.mean() * 100
    plt.plot(np.arange(allerr.size), allerr.flatten(), label='current with cam img')

    print("All errors: ", allerr)

    plt.title(f'max error: {np.abs(allerr).max():2.2f}')
    plt.legend()
    plt.show()

def fitMaximaLocs():
    img_avg = np.loadtxt('./test/img_avg_withWrongLocs.txt')
    drawer = realTimeDrawer()
    maximaLocs = findAtomLocs(img_avg, window=None, neighborhood_size=95., threshold=16, sort='MatchArray', debug_plot=False)
    drawer.updateMaximaLocs(pic = img_avg, maximaLocs= maximaLocs, window=None)
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    input("Press Enter to exit...")



if __name__ == '__main__':
    trap_balancing()
    # evaluateTrapDepthResult()
    # fitMaximaLocs()