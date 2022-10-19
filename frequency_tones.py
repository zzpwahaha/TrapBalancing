from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt


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

if __name__ == '__main__':
    ft0 = FrequencyTones(0, 9, 98, 25.2/9, 28.3)
    ft1 = FrequencyTones(0, 9, 98, 25.2/9, 28.3)
    ft0.print_GM_Command()
    print()
    ft1.print_GM_Command()

    ft0.plotTimeTraces()
    ft1.plotTimeTraces()