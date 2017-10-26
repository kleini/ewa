from abc import abstractmethod


class DriverABC(object):

    @abstractmethod
    def __init__(self, device=None):
        """
        :rtype: DriverABC
        :param device:
            The CAN interface device
        """

    @abstractmethod
    def recv(self):
        """
        Method blocks waiting for a message from the CAN bus.

        :return:
            :class:`canopen.ReceivedMessage` object.
        """
        raise NotImplementedError("Driver method to receive messages is not implemented.")

    @abstractmethod
    def send(self, msg):
        """
        Send a message to the CAN bus.

        :param msg: A :class:`can.Message` object.

        :raise: :class:`can.CanError`
            if the message could not be written.
        """
        raise NotImplementedError("Driver method to send messages is not implemented.")

    @abstractmethod
    def close(self):
        raise NotImplementedError("Driver method to close interface is not implemented.")
