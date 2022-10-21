from frequency_tones import FrequencyTones
import numpy as np
import matplotlib.pyplot as plt
import ctypes
from GMoogProxy import GM_python


class TweezerGrid2D:
    '''
    freq_axis0 corresponds to gigamoog dac0
    freq_axis1 corresponds to gigamoog dac1
        In the current tweezer monitoring system, the DAC0 is horizontal and DAC1 is veritcal.
        In the pcolormesh plot, the correpsonding freq tone is 
            |DAC1 freq low, DAC0 freq low --------------- DAC1 freq low, DAC0 freq high  |
            |             :                                              :               |
            |             :                                              :               |
            |             :                                              :               |
            |DAC1 freq high, DAC0 freq low --------------- DAC1 freq high, DAC0 freq high|

        In the 2d array data structure, the correpsonding freq tone is 
            [[DAC1 freq high, DAC0 freq low] --------------- [DAC1 freq high, DAC0 freq high] ],
             [             :                                              :                   ],
             [             :                                              :                   ],
             [             :                                              :                   ],
             [[DAC1 freq low, DAC0 freq low] --------------- [DAC1 freq low, DAC0 freq high]  ]]

            In this sense, trap_depth.reshape((self.freq_axis1.num_tones, self.freq_axis0.num_tones))[::-1,:] will give the correct trap depth matrix, in 
            which the frequency increases for both axis 


    '''
    def __init__(self, freq_axis0: FrequencyTones, freq_axis1: FrequencyTones, gmoog: GM_python):
        self.freq_axis0 = freq_axis0
        self.freq_axis1 = freq_axis1
        self.gmoog = gmoog

    def getGMAmplitudes(self, trap_depth: np.ndarray, method = 'cross', ampscale = 0.01, showPlot = False):
        '''
        This trap_depth 1D array, should be the one that already scaled by the tweezer monitor cam intensity
            trap_depth read from h5 file is in mK, so it is on the order of magnitude of 1.
            After normalize to the tweezer monitor cam, it should be still on that order of magnitude
            This can be used as a guidance of the ampscale
        '''
        if trap_depth.shape[0] != self.freq_axis0.num_tones * self.freq_axis1.num_tones:
            raise ValueError(
                f"The shape of trap_depth supplied, {trap_depth.shape[0]:d} is incomplatible with the product of the two freq tones"+
                f" {self.freq_axis0.num_tones:d}x{self.freq_axis1.num_tones:d} = {self.freq_axis0.num_tones*self.freq_axis1.num_tones:d}")
        
        if method != 'cross' and method != 'mean' and method != 'randomCross':
            raise ValueError(f'Invalid method selection: {method:s}. Valid methods are cross, mean and randomCross')

        n0 = self.freq_axis0.num_tones
        n1 = self.freq_axis1.num_tones

        trap_depth_matrix = trap_depth.reshape((n1,n0))[::-1,:]

        err = (trap_depth_matrix-trap_depth.mean())/trap_depth.mean() * 100
        maxerr = np.max(np.abs(err))

        if showPlot:
            fig, ax = plt.subplots()
            ax.pcolormesh(err)
            ax.set_xlabel("DAC 0")
            ax.set_ylabel("DAC 1")
            ax.set_title('Mean val: ' + trap_depth.mean())
            cbar = fig.colorbar(ax=ax, mappable=ax.collections[0])
            cbar.set_label('Fractional offset (%)')
        
        if method == 'cross':
            amp_D0 = trap_depth_matrix[n0//2,:]  #DAC0
            amp_D1 = trap_depth_matrix[:,n1//2]  #DAC1    

        elif method == 'mean':
            amp_D0 = trap_depth_matrix.mean(axis = 0)  #DAC0
            amp_D1 = trap_depth_matrix.mean(axis = 1)  #DAC1

        elif method == 'randomCross':
            amp_D0 = trap_depth_matrix[np.random.randint(n1),:]  #DAC0
            amp_D1 = trap_depth_matrix[:,np.random.randint(n0)]  #DAC1    

        ampoutD0 = self.freq_axis0.opt_amps - (amp_D0-amp_D0.mean())*ampscale
        ampoutD1 = self.freq_axis1.opt_amps - (amp_D1-amp_D1.mean())*ampscale
        
        passed = self.freq_axis0.checkAmplitudeLimit(amps=ampoutD0)
        if not passed:
            _ = self.freq_axis0.checkAmplitudeLimit(amps=ampoutD0)
            if not _:
                raise RuntimeError("The limit check failed the second time, which shouldn't happen. Aborted.")

        passed = self.freq_axis1.checkAmplitudeLimit(amps=ampoutD1)
        if not passed:
            _ = self.freq_axis1.checkAmplitudeLimit(amps=ampoutD1)
            if not _:
                raise RuntimeError("The limit check failed the second time, which shouldn't happen. Aborted.")

        self.freq_axis0.updateOptimalAmps(amp_D0)
        self.freq_axis1.updateOptimalAmps(amp_D1)

        self.freq_axis0.print_GM_Command()
        self.freq_axis1.print_GM_Command()

        return self.freq_axis0.opt_amps, self.freq_axis1.opt_amps, maxerr

        # self.gmoog.zeroAll()
        # self.freq_axis0.writeToGIGAMOOG(self.gmoog)
        # self.freq_axis1.writeToGIGAMOOG(self.gmoog)
        # self.gmoog.endMessage()

