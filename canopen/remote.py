

# TODO Read remote heartbeat time.

# TODO Listen for heartbeat messages and be online when last heartbeat message is younger the current time minus
#      heartbeat time
class Remote(object):

    def __init__(self, id=None):
        self.id = id
        self.online = False

    def online(self):
        # TODO Read remote heartbeat time
        return self.online
