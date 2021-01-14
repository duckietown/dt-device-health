from .raspberry_pi import RaspberryPi
from .nvidia_jetson import NvidiaJetson


def get_board():
    if NvidiaJetson.is_instance_of():
        return NvidiaJetson()
    return RaspberryPi()
