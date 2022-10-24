import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
import sys
sys.path.append('C:\Chimera\B240_data_analysis\Library\ChimeraGenTools')
from AnalysisHelpers import getRawAtomImages, fitManyGaussian2D, fitPic, fitGaussian2D, unp

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
        self.fig, self._axes = plt.subplots(figsize=[18,6], ncols=3)
        self._all_plot_types = ['trap_depth', 'dac_output', 'history']
        self.axes = {plot_type: ax for plot_type, ax in zip(self._all_plot_types, self. _axes)}

        self.axes['trap_depth'].set_xlabel('trap label')
        self.axes['trap_depth'].set_ylabel('trap depth mapped')

        self.axes['history'].set_xlabel('num of steps')
        self.axes['history'].set_ylabel('max err')

        self.axes['dac_output'].set_xlabel('dac channel')
        self.axes['dac_output'].set_ylabel('output amp')

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
def getAmplitudeFromGigamoogInput(ginput:str = ginput):
    ginput = list(filter(None, ginput.split('set DAC')))
    ginput = [list(filter(None, _ginput.split(' '))) for _ginput in ginput]
    amp = []
    for gi in ginput:
        amp.append(gi[2])
    
    for idx, _amp in enumerate(amp):
        print(f"{_amp:s}, ", end='')
        if idx == 8:
            print(" ")

if __name__ == '__main__':
    # trap_depth_datafile = 'trap_depth_2022-10-19.h5'
    # trap_depth, trap_depth_uncertainty = getTrapDepthData(trap_data_file=trap_depth_datafile)
    # plt.plot(trap_depth.reshape(9,9)[::-1,:].flatten())
    # plt.show()

    getAmplitudeFromGigamoogInput()