

class Notification(object):
    """Notification"""
    def __init__(self):
        super(Notification, self).__init__()

    def notify(self, string):
        pass

class MockNotification(Notification):
    def __init__(self):
        super(MockNotification, self).__init__()

    def notify(self, user, message):
        print ("Sent the messsage to the user".format(message))
        pass

    def broadcast(self, message):
        print ("Sent the messsage to all the users".format(message))
        pass
