

# TODO rename to Message
class ReceivedMessage(object):
    def __init__(self, ident, length, data):
        self.ident = ident
        self.length = length
        self.data = data
