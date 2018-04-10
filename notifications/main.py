import socket

class Notification(object):
    """Notification"""
    def __init__(self):
        super(Notification, self).__init__()

    def notify(self, string):
        pass

class MockNotification(Notification):
    def __init__(self):
        super(MockNotification, self).__init__()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def notify(self, user, message):
        self.sockd.sendto(message, user)

    def broadcast(self, message):
        self.sock.sendall(message)
