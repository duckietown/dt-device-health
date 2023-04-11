from .raspberry_pi import RaspberryPi
from .nvidia_jetson import NvidiaJetson
from .virtual import Virtual


def get_board():
    if Virtual.is_instance_of():
        return Virtual()
    if NvidiaJetson.is_instance_of():
        return NvidiaJetson()
    return RaspberryPi()


def board_has_gpu():
    if NvidiaJetson.is_instance_of():
        return True
    return False
