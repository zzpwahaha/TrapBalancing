
import sys
from typing import Optional
sys.path.append('./3rd_Party/Vimba_4.2/VimbaPython/Source')
from vimba import *


def print_preamble():
    print('///////////////////////////////////////////')
    print('/// Vimba API Asynchronous Grab Example ///')
    print('///////////////////////////////////////////\n')


def print_usage():
    print('Usage:')
    print('    python asynchronous_grab.py [camera_id]')
    print('    python asynchronous_grab.py [/h] [-h]')
    print()
    print('Parameters:')
    print('    camera_id   ID of the camera to use (using first camera if not specified)')
    print()


def abort(reason: str, return_code: int = 1, usage: bool = False):
    print(reason + '\n')

    if usage:
        print_usage()

    sys.exit(return_code)


def parse_args() -> Optional[str]:
    args = sys.argv[1:]
    argc = len(args)

    for arg in args:
        if arg in ('/h', '-h'):
            print_usage()
            sys.exit(0)

    if argc > 1:
        abort(reason="Invalid number of arguments. Abort.", return_code=2, usage=True)

    return None if argc == 0 else args[0]


def get_camera(camera_id: Optional[str]) -> Camera:
    with Vimba.get_instance() as vimba:
        if camera_id:
            try:
                return vimba.get_camera_by_id(camera_id)

            except VimbaCameraError:
                abort('Failed to access Camera \'{}\'. Abort.'.format(camera_id))

        else:
            cams = vimba.get_all_cameras()
            if not cams:
                abort('No Cameras accessible. Abort.')

            return cams[0]


def setup_camera(cam: Camera):
    with cam:
        # Try to adjust GeV packet size. This Feature is only available for GigE - Cameras.
        try:
            cam.GVSPAdjustPacketSize.run()

            while not cam.GVSPAdjustPacketSize.is_done():
                pass

        except (AttributeError, VimbaFeatureError):
            pass


def frame_handler(cam: Camera, frame: Frame):
    print('{} acquired {}'.format(cam, frame), flush=True)

    cam.queue_frame(frame)


def main():
    print_preamble()
    # cam_id = parse_args()

    with Vimba.get_instance():
        with get_camera('10.10.0.8') as cam:

            setup_camera(cam)
            print('Press <enter> to stop Frame acquisition.')

            try:
                # Start Streaming with a custom a buffer of 10 Frames (defaults to 5)
                cam.start_streaming(handler=frame_handler, buffer_count=10)
                input()

            finally:
                cam.stop_streaming()


if __name__ == '__main__':
    main()
