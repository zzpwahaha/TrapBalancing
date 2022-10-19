import ctypes

gmoogLib = ctypes.cdll.LoadLibrary(
    'C:/Chimera/gmoogLib/gmoogLib/x64/Release/gmoogLib.dll')
class GM_python(object):
    def __init__(self):
        gmoogLib.gm_new.argtypes = []
        gmoogLib.gm_new.restype = ctypes.c_void_p

        gmoogLib.gm_test.argtypes = [ctypes.c_void_p]
        gmoogLib.gm_test.restype = ctypes.c_int

        gmoogLib.gm_zeroAll.argtypes = [ctypes.c_void_p]
        gmoogLib.gm_zeroAll.restype = ctypes.c_void_p

        gmoogLib.gm_endMessage.argtypes = [ctypes.c_void_p]
        gmoogLib.gm_endMessage.restype = ctypes.c_void_p

        gmoogLib.gm_setDAC.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(
            ctypes.c_float), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
        gmoogLib.gm_setDAC.restype = ctypes.c_void_p

        self.obj = gmoogLib.gm_new()

    def test(self):
        gmoogLib.gm_test(self.obj)

    def zeroAll(self):
        gmoogLib.gm_zeroAll(self.obj)

    def endMessage(self):
        gmoogLib.gm_endMessage(self.obj)

    def setDAC(self, dac, channels, freqs, amps, phases):
        gmoogLib.gm_setDAC(self.obj, dac, channels, freqs, amps, phases)
