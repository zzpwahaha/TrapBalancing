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
