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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def notify(self, user, message):
        self.sock.sendto(message, user)

    def broadcast(self, message):
        ip_address = '0.0.0.0'
        port = 10000

        self.sock.sendto(message,(ip_address, port))
