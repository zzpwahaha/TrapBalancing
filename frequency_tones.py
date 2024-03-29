from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
# from GMoogProxy import GM_python
import ctypes


@dataclass
class FrequencyTones:
    def __init__(self, DACoffset, numtones, freqs, phases, amplitude, max_amp = 100, repeat=1):
        self.DACoffset = DACoffset  # which dac is using in gm
        self.num_tones = numtones
        self.nominal_amplitude = amplitude

        self.tone_idx = np.arange(self.num_tones)
        self.freqs = freqs
        self.phases = phases
        self.phase_degs = np.round(self.phases*180/np.pi % 360, 1)
        self.init_amps = np.ones(self.num_tones)*self.nominal_amplitude
        self.opt_amps = self.init_amps.copy()
        self.opt_amps_previous_values = [self.opt_amps]

        self.max_amp = max_amp
        self.repeat_num = repeat
        print(f"NOTICE: the maximum amplitude is set to {self.max_amp} and each command will be repeated {self.repeat_num} times")
        self.checkAmplitudeLimit()

    @classmethod
    def fromFixedFrequencySpacing(cls, DACoffset, numtones, freq_center, freq_spacing, amplitude, max_amp = 100):
        freqs = freq_center + freq_spacing * np.arange(-(numtones-1)/2, numtones/2, 1)
        # follows https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1054411 only works for equally spaced tones
        phases = np.pi*((np.arange(numtones)+1)**2)/(numtones)
    
        return cls(DACoffset, numtones, freqs, phases, amplitude, max_amp)

    # def __init__(self, DACoffset, numtones, freq_center, freq_spacing, amplitude, max_amp = 100):
    #     self.DACoffset = DACoffset  # which dac is using in gm
    #     self.num_tones = numtones
    #     self.freq_center = freq_center
    #     self.freq_spacing = freq_spacing
    #     self.nominal_amplitude = amplitude
    #     self.tone_idx = np.arange(self.num_tones)
    #     self.freqs = self.freq_center + self.freq_spacing * \
    #         np.arange(-(self.num_tones-1)/2, self.num_tones/2, 1)
    #     # follows https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1054411 only works for equally spaced tones
    #     self.phases = np.pi*((self.tone_idx+1)**2)/(self.num_tones)
    #     self.phase_degs = np.round(self.phases*180/np.pi % 360, 1)
    #     self.init_amps = np.ones(self.num_tones)*self.nominal_amplitude
    #     self.opt_amps = self.init_amps.copy()
    #     self.opt_amps_previous_values = [self.opt_amps]
    #     self.max_amp = max_amp
    #     print(f"NOTICE: the maximum amplitude is set to {self.max_amp}")
    #     self.checkAmplitudeLimit()

    def get_GM_Command(self):
        command = []
        for ind in self.tone_idx:
            command.append('set DAC{:d} {:d} {:6.2f} {:6.2f} {:6.2f}'.format(
                0+self.DACoffset, ind, self.opt_amps[ind], self.freqs[ind], self.phase_degs[ind]))
        return command

    def print_GM_Command(self):
        for ind in self.tone_idx:
            print('set DAC{:d} {:d} {:6.2f} {:6.2f} {:6.2f}'.format(
                0+self.DACoffset, ind, self.opt_amps[ind], self.freqs[ind], self.phase_degs[ind]))

    def set_initial_amps(self, init_amps:np.ndarray):
        if len(init_amps) != self.num_tones:
            raise ValueError(f"Input initial amplitude has different size {len(init_amps):d} as the num of freq tones {self.num_tones:d}")

        self.init_amps = init_amps
        self.opt_amps = self.init_amps.copy()

    def _set_frequencies(self, freqs):
        if len(freqs) != self.num_tones:
            raise ValueError(f"Input frequencies has different size {len(freqs):d} as the num of freq tones {self.num_tones:d}")
        self.freqs = freqs

    def updateOptimalAmps(self, opt_amps):
        self.opt_amps = opt_amps
        self.opt_amps_previous_values.append(self.opt_amps)


    def checkAmplitudeLimit(self, amps = None):
        if amps is None:
            amps = self.opt_amps
        else:
            print("Perform boundary check of the input amplitude ", amps)
        passed = True

        if np.any(amps>self.max_amp):
            passed = False
            for idx, _crit in enumerate(amps>self.max_amp):
                if _crit:
                    print(f"Values {idx:d}: {amps[idx]:.2f} in opt_amp is larger than the maximum. Will set the value to the max value {self.max_amp:.2f}")
                    amps[idx] = self.max_amp
        
        if np.any(amps<0):
            passed = False
            for idx, _crit in enumerate(amps<0):
                if _crit:
                    print(f"Values {idx:d}: {amps[idx]:.2f} in opt_amp is smaller than 0. Will set the value to the min value {0:.2f}")
                    amps[idx] = 0.0

        # or can use np.putmask(amps, amps>self.max_amp, self.max_amp)
        return passed

    def writeToGIGAMOOG(self, gmoog):
        num_tones = self.num_tones*self.repeat_num
        freqs = np.tile(self.freqs, self.repeat_num)
        opt_amps = np.tile(self.opt_amps, self.repeat_num)
        phase_degs = np.tile(self.phase_degs, self.repeat_num)


        seq = ctypes.c_double * num_tones
        # perform the last check before writing it to the gigamoog, last chance
        if self.checkAmplitudeLimit():
            gmoog.setDAC(0+self.DACoffset, num_tones, seq(*freqs), seq(*opt_amps), seq(*phase_degs))
            print(r"DACoffset = ", 0+self.DACoffset, 
                "\nnum_tones = ", num_tones, 
                "\nfreqs = ", np.array2string(freqs, separator=","), 
                "\nopt_amps = ", np.array2string(opt_amps, separator=","), 
                "\nphase_degs = ", np.array2string(phase_degs, separator=","))
        else:
            raise RuntimeError("Failed to pass the amplitude limit check before setting the GIGAMOOG!!!! Aborted.")


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

if __name__ == '__main__':
    MAX_AMPLITUDE = 30.5
    dac0_init_amp = np.array([27.92, 28.22, 28.32, 28.37, 28.47, 28.62, 28.92, 29.07, 29.17])
    dac1_init_amp = np.array([26.92, 27.32, 27.42, 27.57, 27.82, 28.02, 28.42, 28.62, 28.87])
    
    ft0 = FrequencyTones(0, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
    ft0._set_frequencies([86.800003, 89.599998, 92.400002, 95.199997, 98, 100.800003, 103.599998, 106.400002, 109.199997])
    ft0.set_initial_amps(dac0_init_amp)
    ft1 = FrequencyTones(1, 9, 98, 25.2/9, 28.3, max_amp= MAX_AMPLITUDE)
    ft1._set_frequencies([86.800003, 89.599998, 92.400002, 95.199997, 98, 100.800003, 103.599998, 106.400002, 109.199997])
    ft1.set_initial_amps(dac1_init_amp)


    ft0.print_GM_Command()
    print()
    ft1.print_GM_Command()

    ft0.plotTimeTraces()
    ft1.plotTimeTraces()