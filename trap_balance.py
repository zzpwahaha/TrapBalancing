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

sys.path.append('C:\Chimera\B240_data_analysis\Library\ChimeraGenTools')
from AnalysisHelpers import findAtomLocs, getRawAtomImages, fitManyGaussian2D, fitPic, fitGaussian2D, unp

tweezer_moncam_ip = '10.10.0.8'
tweezer_moncam_setting = './tweezer_monitor.xml'
trap_depth_datafile = 'trap_depth_2022-10-19.h5'

# gmoog = GM_python()
# zclient = zynq_tcp_client()
# mako = mako_camera(ipaddr=tweezer_moncam_ip, settingAddr=tweezer_moncam_setting)
# img_avg = mako.getAvgImages(time_interval = 0.05)


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

# np.savetxt('img_avg_test.txt',img_avg)
img_avg = np.loadtxt('img_avg_test.txt')
# fig, ax = plt.subplots()
# ax.pcolormesh(img_avg)
# ax.set_aspect(1)
# plt.show()
# window = [0,0,img_avg.shape[1], img_avg.shape[0]]
# maximaLocs = findAtomLocs(img_avg, window=None, neighborhood_size=90., threshold=15, sort='MatchArray', debug_plot=True)
maximaLocs = findAtomLocs(img_avg, window=None, neighborhood_size=95.,
                          threshold=16, sort='MatchArray', debug_plot=False)
# plt.show()
print(maximaLocs)
# idv_atom_imgs = getRawAtomImages(img_avg, maximaLocs, boundary=[-10, -10, 10, 10])
# fig, ax = plt.subplots()
# ax.pcolormesh(idv_atom_imgs[0])
# ax.set_aspect(1)
# plt.show()
trap_depth, trap_depth_uncertainty = getTrapDepthData(trap_data_file=trap_depth_datafile)
print(f"The maximum relative trap depth uncertainty is {np.max(trap_depth_uncertainty/trap_depth):2.2e}")
twz_amps0 = getTweezerAmplitudes(img_avg, maximaLocs, amp_option='fit', showResult=False)
# twz_amps0 = getTweezerAmplitudes(img_avg, maximaLocs, amp_option='sum', showResult=True)
# plt.show()

# img_avg = mako.getAvgImages(time_interval = 0.05)
twz_amps = getTweezerAmplitudes(img_avg, maximaLocs, amp_option='fit', showResult=False)
trap_depth_mapped = trap_depth / twz_amps0 * twz_amps





plt.plot(trap_depth/twz_amps0)
plt.show()





def getNewAmps(img, ampsetD0, ampsetD1, freqsetD0, freqsetD1, phaseset0, phaseset1, masks, DACoffset = 0, method = 'cross', bgoff = (165,165), ampscale = .01, double = False):
    
    n0 = len(freqsetD0)
    n1 = len(freqsetD1)
    
    ampset100_0 = np.ones(n0)*100
    ampset100_1 = np.ones(n1)*100

    roisums = np.array(list(map(lambda mask: np.sum(mask*img), masks)))

    if DACoffset==0:
        sign = 1 # for dac 0, 1
    elif DACoffset==2:
        sign = -1 # for dac 2, 3
    else:
        raise ValueError('Invalid DAC offset.')
        
    err = (roisums.reshape((n1,n0))[::-sign,:]-roisums.mean())/roisums.mean()*100
    maxerr = np.max(np.abs(err))
    fig=plt.figure()
    plt.imshow(err)
    plt.xlabel("DAC 0")
    plt.ylabel("DAC 1")
    plt.title('Mean val:'+str(np.mean(roisums)))
    cbar = plt.colorbar()
    cbar.set_label('Fractional offset (%)')
   
    if method == 'cross':
        roisumsD0 = roisums.reshape((n1,n0))[n0//2,::sign]  #DAC0
        roisumsD1 = roisums.reshape((n1,n0))[::-sign,n1//2]  #DAC1    
        
    elif method == 'mean':
        roisumsD0 = np.mean(roisums.reshape((n1,n0))[:, ::sign], axis = 0)  #DAC0
        roisumsD1 = np.mean(roisums.reshape((n1,n0))[::-sign,:], axis = 1)  #DAC1
    
    elif method == 'randomCross':
        roisumsD0 = roisums.reshape((n1,n0))[np.random.randint(n1),::sign]  #DAC0
        roisumsD1 = roisums.reshape((n1,n0))[::-sign,np.random.randint(n0)]  #DAC1    

    else:
        raise ValueError('Invalid method selection: ' + method)
    
    ampoutD0 = ampsetD0 - (roisumsD0-np.mean(roisumsD0))*ampscale
    ampoutD1 = ampsetD1 - (roisumsD1-np.mean(roisumsD1))*ampscale
    
    ampMax = np.max([np.max(ampoutD0), np.max(ampoutD1)])
    if ampMax > 100:
        ampoutD0 = ampoutD0 - (ampMax - 100)
        ampoutD1 = ampoutD1 - (ampMax - 100)
    
    ampMin = np.min([np.min(ampoutD0), np.min(ampoutD1)])
    if ampMin < 0:
        ampoutD0 = ampoutD0 - (ampMin)
        ampoutD1 = ampoutD1 - (ampMin)
    
    #     Send new values to GMoog
        
    gmoog.zeroAll()
    
    if double:
#         amp100_0 = np.ones(n0)*100
#         amp100_1 = np.ones(n1)*100
        ##more conservative, don't start at 100.
        amp100_0 = np.ones(n0)*80
        amp100_1 = np.ones(n1)*80

        seq0 = c_float * (2 * n0)
        seq1 = c_float * (2 * n1)
        
        freqsetDD0 = np.concatenate((freqsetD0,freqsetD0))
        freqsetDD1 = np.concatenate((freqsetD1,freqsetD1))

        ampsetDD0 = np.concatenate((amp100_0, ampsetD0))
        ampsetDD1 = np.concatenate((amp100_1, ampsetD1))

        phasesetD0 = np.concatenate((phaseset0,phaseset0))
        phasesetD1 = np.concatenate((phaseset1,phaseset1))
        gmoog.setDAC(0+DACoffset, 2*n0, seq0(*freqsetDD0), seq0(*ampsetDD0), seq0(*phasesetD0))
        gmoog.setDAC(1+DACoffset, 2*n1, seq1(*freqsetDD1), seq1(*ampsetDD1), seq1(*phasesetD1))
    
    else:
        seq0 = c_float * n0
        seq1 = c_float * n1
        gmoog.setDAC(0+DACoffset, n0, seq0(*freqsetD0), seq0(*ampsetD0), seq0(*phaseset0))
        gmoog.setDAC(1+DACoffset, n1, seq1(*freqsetD1), seq1(*ampsetD1), seq1(*phaseset1))
        
    gmoog.endMessage()
    
    time.sleep(.2)
    
    return ampoutD0, ampoutD1, maxerr