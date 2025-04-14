import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
import sys
sys.path.append('C:\Chimera\B240_data_analysis\Library\ChimeraGenTools')
from AnalysisHelpers import getRawAtomImages, fitManyGaussian2D, fitPic, fitGaussian2D, unp, crop
# import AnalysisHelpers as ah

def getTweezerAmplitudes(picture, tweezerLocs, amp_option='fit', showResult=False):
    idv_atom_imgs = getRawAtomImages(
        picture, tweezerLocs, boundary=[-10, -10, 10, 10])
    if amp_option != 'fit' and amp_option != 'sum':
        raise ValueError(f"Invalid amplitude option {amp_option:s}. Valid options are: \'fit\' and \'sum\'")

    gauss_amp = []
    if amp_option == 'fit':
        for _img in idv_atom_imgs:
            _res = fitGaussian2D(_img, guessSigma_x=10, guessSigma_y=10, showFit=False)
            gauss_amp.append(_res['popt_unc'][0])
        gauss_amp = np.array(gauss_amp)
    elif amp_option == 'sum':
        for _img in idv_atom_imgs:
            _res = _img.sum() - _img.min() * _img.size
            gauss_amp.append(_res)
        gauss_amp = np.array(gauss_amp)
    else:
        pass  # this shouldn't happen

    if showResult:
        plt.errorbar(np.arange(len(tweezerLocs)),
                     unp.nominal_values(gauss_amp), unp.std_devs(gauss_amp), c='b', lw=2, marker='.', ms=10)
    return gauss_amp

def getTrapDepthData(trap_data_file):
    # this will take the trap depth, generated with Andor image in ChimeraGenTool, and flip it so that the returned trap depth will
    # match the amplitude measured in the monitoring MAKO camera
    with h5.File(r'./TrapDepthData/'+trap_data_file, 'r') as f:
        trap_depth = f['trap_depth'][()]
        trap_depth_uncertainty = f['trap_depth_uncertainty'][()]
    trap_depth = trap_depth[::-1]
    trap_depth_uncertainty = trap_depth_uncertainty[::-1]
    return trap_depth, trap_depth_uncertainty


class realTimeDrawer():
    def __init__(self):
        plt.ion()
        # here we are creating sub plots
        self.fig, self._axes = plt.subplots(figsize=[20,12], ncols=4, nrows=2)
        self._all_plot_types = ['trap_depth', 'dac_output', 'history', 'twz_amp']
        self.axes = {plot_type: ax for plot_type, ax in zip(self._all_plot_types, self._axes.flatten())}
        self.maxilocs_dplot_axes = self._axes[1,:]

        self.axes['trap_depth'].set_xlabel('trap label')
        self.axes['trap_depth'].set_ylabel('trap depth mapped')

        self.axes['history'].set_xlabel('num of steps')
        self.axes['history'].set_ylabel('max err')

        self.axes['dac_output'].set_xlabel('dac channel')
        self.axes['dac_output'].set_ylabel('output amp')

        self.axes['twz_amp'].set_xlabel('trap label')
        self.axes['twz_amp'].set_ylabel('tweezer amplitude')

    def updateXY(self, x, y, type = 'trap_depth'):
        if type=='trap_depth':
            if not self.axes[type].lines:
                self.axes[type].plot(x,y,label='current')
                self.axes[type].plot(x,y,label='initial')
                self.axes[type].legend()
            # updating data values
            self.axes[type].lines[0].set_xdata(x)
            self.axes[type].lines[0].set_ydata(y)

        if type == 'dac_output':
            if not self.axes[type].lines:
                self.axes[type].plot(x[0],y[0], label='dac0')
                self.axes[type].plot(x[1],y[1], label='dac1')
                self.axes[type].plot(x[0],y[0], label='initial dac0')
                self.axes[type].plot(x[1],y[1], label='initial dac1')
                self.axes[type].legend()

            for _x,_y,_l in zip(x,y,self.axes[type].lines):
                _l.set_xdata(_x)
                _l.set_ydata(_y)

        if type == 'history':
            if not self.axes[type].lines:
                self.axes[type].plot([],[], label='max')
                self.axes[type].plot([],[], label='std')
                self.axes[type].legend()

            for _x,_y,_l in zip(x,y,self.axes[type].lines):
                _l.set_xdata(_x)
                _l.set_ydata(_y)

        if type == 'twz_amp':
            if not self.axes[type].lines:
                self.axes[type].plot(x, y, label='current')
                self.axes[type].plot(x, y, label='initial')
                self.axes[type].legend()

            self.axes[type].lines[0].set_xdata(x)
            self.axes[type].lines[0].set_ydata(y)


        # recompute the ax.dataLim
        self.axes[type].relim()
        # update ax.viewLim using the new dataLim
        self.axes[type].autoscale_view()

        # drawing updated values
        self.fig.canvas.draw()
    
        # This will run the GUI event
        # loop until all UI events
        # currently waiting have been processed
        self.fig.canvas.flush_events()

    def updateMaximaLocs(self, pic, maximaLocs, window = None):
        ax = self.maxilocs_dplot_axes
        fig = self.fig
        p = ax[0].pcolormesh(*crop(pic, window, forPlot=True))
        ax[0].set_aspect('equal')
        fig.colorbar(p, ax = ax[0])
        # if window is None:
        #     window = [0,0,pic.shape[-1], pic.shape[-2]]
        # ax[0].plot([window[0]+_max[0] for _max in maximaLocs],
        #         [window[1]+_max[1] for _max in maximaLocs], marker='.', ms=2, ls='', mec='k', mfc='k')
        # ax[1].pcolormesh(*crop(pic, window, forPlot=True, startXYZero=True))
        # ax[1].set_aspect('equal')
        # ax[1].plot([_max[0] for _max in maximaLocs],
        #         [_max[1] for _max in maximaLocs], marker='.', ms=2, ls='', mec='k', mfc='k')
        ax[1].pcolormesh(*crop(pic, window, forPlot=True, startXYZero=True))
        ax[1].set_aspect('equal')
        ax[1].plot([_max[0] for _max in maximaLocs],
                [_max[1] for _max in maximaLocs], marker='.', ms=2, ls='', mec='k', mfc='k')        
        for _idx, _max in enumerate(maximaLocs):
            ax[1].text(x=_max[0]+1,y=_max[1]+1,s="{:d}".format(_idx),c='white',ha='center', va='center')


ginput = 'set DAC0 0  30.33  86.80  20.00\
set DAC0 1  26.05  89.60  80.00\
set DAC0 2  22.33  92.40 180.00\
set DAC0 3  27.06  95.20 320.00\
set DAC0 4  28.60  98.00 140.00\
set DAC0 5  30.50 100.80   0.00\
set DAC0 6  29.82 103.60 260.00\
set DAC0 7  23.84 106.40 200.00\
set DAC0 8  27.93 109.20 180.00\
set DAC1 0  22.08  86.80  20.00\
set DAC1 1  23.89  89.60  80.00\
set DAC1 2  28.33  92.40 180.00\
set DAC1 3  30.50  95.20 320.00\
set DAC1 4  28.85  98.00 140.00\
set DAC1 5  25.17 100.80   0.00\
set DAC1 6  22.23 103.60 260.00\
set DAC1 7  26.20 106.40 200.00\
set DAC1 8  30.38 109.20 180.00'
ginput = 'set DAC0 0  30.41  86.80  20.00\
set DAC0 1  27.63  89.60  80.00\
set DAC0 2  25.70  92.40 180.00\
set DAC0 3  25.90  95.20 320.00\
set DAC0 4  27.76  98.00 140.00\
set DAC0 5  30.14 100.80   0.00\
set DAC0 6  30.50 103.60 260.00\
set DAC0 7  28.44 106.40 200.00\
set DAC0 8  27.94 109.20 180.00\
set DAC1 0  24.97  86.80  20.00\
set DAC1 1  25.72  89.60  80.00\
set DAC1 2  28.23  92.40 180.00\
set DAC1 3  30.50  95.20 320.00\
set DAC1 4  30.22  98.00 140.00\
set DAC1 5  27.88 100.80   0.00\
set DAC1 6  26.23 103.60 260.00\
set DAC1 7  25.85 106.40 200.00\
set DAC1 8  30.00 109.20 180.00'
ginput = 'set DAC0 0  30.35  86.80  20.00\
set DAC0 1  27.58  89.60  80.00\
set DAC0 2  25.61  92.40 180.00\
set DAC0 3  26.00  95.20 320.00\
set DAC0 4  27.92  98.00 140.00\
set DAC0 5  30.06 100.80   0.00\
set DAC0 6  30.49 103.60 260.00\
set DAC0 7  28.46 106.40 200.00\
set DAC0 8  28.13 109.20 180.00\
set DAC1 0  25.04  86.80  20.00\
set DAC1 1  25.71  89.60  80.00\
set DAC1 2  28.12  92.40 180.00\
set DAC1 3  30.50  95.20 320.00\
set DAC1 4  30.13  98.00 140.00\
set DAC1 5  27.80 100.80   0.00\
set DAC1 6  26.17 103.60 260.00\
set DAC1 7  25.71 106.40 200.00\
set DAC1 8  29.83 109.20 180.00'
ginput = 'set DAC0 0  30.67  86.80  3\
set DAC0 1  27.82  88.00  66\
set DAC0 2  25.83  89.60  169\
set DAC0 3  26.10  91.60  251\
set DAC0 4  28.02  94.00  322\
set DAC0 5  30.19  96.80  315\
set DAC0 6  30.78 100.00  353\
set DAC0 7  28.63 103.60  0\
set DAC0 8  28.14 107.60  0'
ginput = 'set DAC0 0  29.36  86.80 171.90\
set DAC0 1  29.41  88.00 181.50\
set DAC0 2  28.17  89.60 323.00\
set DAC0 3  27.47  91.60 341.20\
set DAC0 4  26.17  94.00  89.20\
set DAC0 5  27.33  96.80  48.20\
set DAC0 6  28.90 100.00  65.40\
set DAC0 7  30.06 103.60   0.00\
set DAC0 8  29.30 107.60   0.00\
set DAC1 0  30.49  91.60 341.20\
set DAC1 1  30.99 103.60   0.00'
ginput = 'set DAC0 0  25.59  86.80 171.90\
set DAC0 1  25.63  88.00 181.50\
set DAC0 2  24.55  89.60 323.00\
set DAC0 3  23.94  91.60 341.20\
set DAC0 4  22.81  94.00  89.20\
set DAC0 5  23.82  96.80  48.20\
set DAC0 6  25.19 100.00  65.40\
set DAC0 7  26.20 103.60   0.00\
set DAC0 8  25.54 107.60   0.00\
set DAC1 0  26.57  91.60 341.20\
set DAC1 1  27.01 103.60   0.00'
ginput='set DAC0 0  25.59  86.80 171.90\
set DAC0 1  25.63  88.00 181.50\
set DAC0 2  24.55  89.60 323.00\
set DAC0 3  23.94  91.60 341.20\
set DAC0 4  22.81  94.00  89.20\
set DAC0 5  23.82  96.80  48.20\
set DAC0 6  25.19 100.00  65.40\
set DAC0 7  26.20 103.60   0.00\
set DAC0 8  25.54 107.60   0.00\
set DAC1 0  26.57  91.60 341.20\
set DAC1 1  27.01 103.60   0.00'
ginput= 'set DAC0 0 100.00 87.60 0.63\
set DAC0 1 100.00 87.60 0.63\
set DAC0 10 100.00 91.20 2.51\
set DAC0 11 100.00 91.20 2.51\
set DAC0 20 100.00 96.00 22.62\
set DAC0 21 100.00 96.00 22.62\
set DAC0 30 100.00 98.40 40.21\
set DAC0 31 100.00 98.40 40.21\
set DAC0 40 100.00 105.60 123.15\
set DAC0 41 100.00 105.60 123.15'
ginput = 'set DAC0 0  69.77  80.00  70.70\
set DAC0 1  69.77  80.00  70.70\
set DAC0 2  74.35  83.00 294.20\
set DAC0 3  74.35  83.00 294.20\
set DAC0 4  82.96  86.00 299.10\
set DAC0 5  82.96  86.00 299.10\
set DAC0 6  84.14  89.00  91.00\
set DAC0 7  84.14  89.00  91.00\
set DAC0 8  74.32  92.00  35.80\
set DAC0 9  74.32  92.00  35.80\
set DAC0 10  66.27  95.00  15.50\
set DAC0 11  66.27  95.00  15.50\
set DAC0 12  71.61  98.00 248.70\
set DAC0 13  71.61  98.00 248.70\
set DAC0 14  86.20 101.00 162.60\
set DAC0 15  86.20 101.00 162.60\
set DAC0 16 100.00 104.00 217.80\
set DAC0 17 100.00 104.00 217.80\
set DAC0 18  88.44 107.00 172.30\
set DAC0 19  88.44 107.00 172.30\
set DAC0 20  77.74 110.00 167.40\
set DAC0 21  77.74 110.00 167.40\
set DAC0 22  74.36 113.00 303.90\
set DAC0 23  74.36 113.00 303.90\
set DAC0 24  91.09 116.00 233.20\
set DAC0 25  91.09 116.00 233.20'
ginput = 'set DAC0 0  72.20  80.00  90.80\
set DAC0 1  72.20  80.00  90.80\
set DAC0 2  74.17  83.00 296.40\
set DAC0 3  74.17  83.00 296.40\
set DAC0 4  77.99  86.00 217.20\
set DAC0 5  77.99  86.00 217.20\
set DAC0 6  80.78  89.00 173.90\
set DAC0 7  80.78  89.00 173.90\
set DAC0 8  76.55  92.00 251.20\
set DAC0 9  76.55  92.00 251.20\
set DAC0 10  68.98  95.00 168.10\
set DAC0 11  68.98  95.00 168.10\
set DAC0 12  75.21  98.00 209.50\
set DAC0 13  75.21  98.00 209.50\
set DAC0 14  87.68 101.00 316.30\
set DAC0 15  87.68 101.00 316.30\
set DAC0 16  89.66 104.00 239.00\
set DAC0 17  89.66 104.00 239.00\
set DAC0 18  90.72 107.00 152.10\
set DAC0 19  90.72 107.00 152.10\
set DAC0 20  76.00 110.00 231.30\
set DAC0 21  76.00 110.00 231.30\
set DAC0 22  76.74 113.00 132.20\
set DAC0 23  76.74 113.00 132.20\
set DAC0 24  94.56 116.00  41.40\
set DAC0 25  94.56 116.00  41.40'
ginput = 'set DAC0 0  68.84  80.00  96.50\
set DAC0 1  68.84  80.00  96.50\
set DAC0 2  76.70  83.00  62.50\
set DAC0 3  76.70  83.00  62.50\
set DAC0 4  82.39  86.00 204.60\
set DAC0 5  82.39  86.00 204.60\
set DAC0 6  78.80  89.00 243.70\
set DAC0 7  78.80  89.00 243.70\
set DAC0 8  74.11  92.00 352.70\
set DAC0 9  74.11  92.00 352.70\
set DAC0 10  68.28  95.00 271.40\
set DAC0 11  68.28  95.00 271.40\
set DAC0 12  69.93  98.00 123.50\
set DAC0 13  69.93  98.00 123.50\
set DAC0 14  83.12 101.00 122.70\
set DAC0 15  83.12 101.00 122.70\
set DAC0 16  96.67 104.00  13.70\
set DAC0 17  96.67 104.00  13.70\
set DAC0 18  88.41 107.00  74.70\
set DAC0 19  88.41 107.00  74.70\
set DAC0 20  76.78 110.00 292.50\
set DAC0 21  76.78 110.00 292.50\
set DAC0 22  83.27 113.00  14.50\
set DAC0 23  83.27 113.00  14.50\
set DAC0 24  93.94 116.00 212.00\
set DAC0 25  93.94 116.00 212.00'
ginput = 'set DAC0 0  70.50  80.00  13.80\
set DAC0 1  70.50  80.00  13.80\
set DAC0 2  75.79  83.00  55.40\
set DAC0 3  75.79  83.00  55.40\
set DAC0 4  83.02  86.00 124.60\
set DAC0 5  83.02  86.00 124.60\
set DAC0 6  82.18  89.00 221.50\
set DAC0 7  82.18  89.00 221.50\
set DAC0 8  74.48  92.00 346.20\
set DAC0 9  74.48  92.00 346.20\
set DAC0 10  69.90  95.00 138.50\
set DAC0 11  69.90  95.00 138.50\
set DAC0 12  74.14  98.00 318.50\
set DAC0 13  74.14  98.00 318.50\
set DAC0 14  86.33 101.00 166.20\
set DAC0 15  86.33 101.00 166.20\
set DAC0 16  92.70 104.00  41.50\
set DAC0 17  92.70 104.00  41.50\
set DAC0 18  88.02 107.00 304.60\
set DAC0 19  88.02 107.00 304.60\
set DAC0 20  78.43 110.00 235.40\
set DAC0 21  78.43 110.00 235.40\
set DAC0 22  74.40 113.00 193.80\
set DAC0 23  74.40 113.00 193.80\
set DAC0 24  91.38 116.00 180.00\
set DAC0 25  91.38 116.00 180.00'

def getAmplitudeFromGigamoogInput(ginput:str = ginput, repeat=2):
    ginput = list(filter(None, ginput.split('set DAC')))
    ginput = [list(filter(None, _ginput.split(' '))) for _ginput in ginput]
    amp = []
    for gi in ginput:
        amp.append(gi[2])
    amp = np.array(amp)
    for idx, _amp in enumerate(amp[::repeat]):
        print(f"{_amp:s}, ", end='')
        # if idx == 8:
        #     print(" ")
    return np.array([float(_) for _ in amp])

def getFrequencyFromGigamoogInput(ginput:str = ginput, repeat=2):
    ginput = list(filter(None, ginput.split('set DAC')))
    ginput = [list(filter(None, _ginput.split(' '))) for _ginput in ginput]
    amp = []
    for gi in ginput:
        amp.append(gi[3])
    amp = np.array(amp)
    for idx, _amp in enumerate(amp[::repeat]):
        print(f"{_amp:s}, ", end='')
        # if idx == 8:
        #     print(" ")

def getPhaseFromGigamoogInput(ginput:str = ginput, repeat=2):
    ginput = list(filter(None, ginput.split('set DAC')))
    ginput = [list(filter(None, _ginput.split(' '))) for _ginput in ginput]
    amp = []
    for gi in ginput:
        amp.append(gi[4])
    amp = np.array(amp)
    for idx, _amp in enumerate(amp[::repeat]):
        print(f"{_amp:s}, ", end='')
        # if idx == 8:
        #     print(" ")

if __name__ == '__main__':
    # trap_depth_datafile = 'trap_depth_2022-10-19.h5'
    # trap_depth, trap_depth_uncertainty = getTrapDepthData(trap_data_file=trap_depth_datafile)
    # plt.plot(trap_depth.reshape(9,9)[::-1,:].flatten())
    # plt.show()

    _ = getAmplitudeFromGigamoogInput()
    print()
    # print(_)
    # print(_ * (4/4.6)**(1/4))
    getFrequencyFromGigamoogInput()
    print()
    getPhaseFromGigamoogInput()