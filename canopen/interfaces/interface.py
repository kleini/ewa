from canopen.interfaces.socketcan import SocketCAN


class Interface(object):

    def __new__(cls, device=None, *args, **kwargs):
        cls = SocketCAN
        return cls(device=device)
