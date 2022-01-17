from visca_over_ip.camera import Camera


class CachingCamera(Camera):
    """Uses caching to improve performance and decrease network traffic.
    Will quickly break if multiple controllers are connected to a given camera.
    """
    def __init__(self, ip, port=52381):
        super().__init__(ip, port)

        self.state = {
            'focus_mode': super().get_focus_mode(),
            'pan_tilt_stop': False,
            'zoom_stop': False
        }

    def get_focus_mode(self) -> str:
        return self.state['focus_mode']

    def set_focus_mode(self, mode: str):
        super().set_focus_mode(mode)
        self.state['focus_mode'] = mode

    def pantilt(self, pan_speed: int, tilt_speed: int, pan_position=None, tilt_position=None, relative=False):
        if pan_speed == 0 and tilt_speed == 0:
            if self.state['pan_tilt_stop'] is False:
                super().pantilt(pan_speed, tilt_speed, pan_position, tilt_position, relative)

            self.state['pan_tilt_stop'] = True

        else:
            super().pantilt(pan_speed, tilt_speed, pan_position, tilt_position, relative)
            self.state['pan_tilt_stop'] = False

    def zoom(self, speed: int):
        if speed == 0:
            if self.state['zoom_stop'] is False:
                super().zoom(speed)

            self.state['zoom_stop'] = True

        else:
            super().zoom(speed)
            self.state['zoom_stop'] = False
