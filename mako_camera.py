import sys
sys.path.append('./3rd_Party/Vimba_4.2/VimbaPython/Source')
from time import sleep
import vimba
import numpy as np
import matplotlib.pyplot as plt

class mako_camera:
    def __init__(self, ipaddr, settingAddr = None):
        self.ip = ipaddr
        self.tweezer_moncam_setting = settingAddr
        self.imgs = []
        with vimba.Vimba.get_instance() as vba:
            with vba.get_camera_by_id(self.ip) as cam:
                self.cam = cam
                self.cam_model = self.cam.get_model()
                print("Get camera: ",self.cam_model)
        self.setup_camera()


    def __hanlder(self, cam: vimba.Camera, frame: vimba.Frame):
        # print('Frame acquired : {} '. format(frame), flush=True)
        self.imgs.append(frame.as_numpy_ndarray())
        cam.queue_frame(frame)

    def __call__(self, cam: vimba.Camera, frame: vimba.Frame):
        self.__hanlder(cam, frame)

    def setup_camera(self):
        with vimba.Vimba.get_instance() as vba:
            with self.cam as cam:
                # Try to adjust GeV packet size. This Feature is only available for GigE - Cameras.
                try:
                    if self.tweezer_moncam_setting is not None:
                        cam.load_settings(self.tweezer_moncam_setting, vimba.PersistType.NoLUT)
                    cam.GVSPAdjustPacketSize.run()
                    while not cam.GVSPAdjustPacketSize.is_done():
                        pass
                    cam.TriggerSelector.set('FrameStart')
                    cam.TriggerMode.set('On')
                    cam.TriggerSource.set('Software')
                    cam.AcquisitionMode.set('Continuous')
                except (AttributeError, vimba.VimbaFeatureError, )  as err:
                    print(err)
                    print(err.args)

    def getAvgImages(self, num = 10, time_interval = 0.1, debug = False):
        if not debug:
            self.imgs = []
            with vimba.Vimba.get_instance() as vba:
                with self.cam as cam:
                    cam.start_streaming(handler=self)        
                    for i in range(num):
                        cam.TriggerSoftware.run()
                        sleep(time_interval)
                    cam.stop_streaming()
            print(f'{num:d} Frame acquired from {self.cam_model:s}', flush=True)
            return np.array(self.imgs).mean(axis=0)[:,:,0]
        else:
            return np.loadtxt("./test/img_avg_test.txt")

if __name__ == '__main__':
    tweezer_moncam_setting = './tweezer_monitor_20240515_1x13.xml'
    mako = mako_camera(ipaddr="10.10.0.8", settingAddr=tweezer_moncam_setting)
    img_avg = mako.getAvgImages(debug=False)
    # np.savetxt("./test/img_avg_test.txt", img_avg)
    print(img_avg)
    # fig, ax = plt.subplots()
    # ax.pcolormesh(img_avg)
    # ax.set_aspect(1)
    # plt.show()

    # img_avg = mako.getAvgImages(num = 20, time_interval = 0.05, debug=False)
    sys.path.append('C:\Chimera\B240_data_analysis\Library\ChimeraGenTools')
    from AnalysisHelpers import findAtomLocs
    maximaLocs = findAtomLocs(img_avg, window=None, neighborhood_size=95., threshold=20, sort='MatchArray', debug_plot=True,n_cluster_row=1,
                              advanced_option = dict({"active":False, "image_threshold":20, "score_threshold":20}))
    plt.show()
    print(maximaLocs)