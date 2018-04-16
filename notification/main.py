class Notification(object):
    """Notification"""

    def __init__(self, token, chat_id, logger):
        super(Notification, self).__init__()
        self.token = token
        self.chat_id = chat_id
        self.logger = logger
        self.chat_id_list = chat_id.split(' ')


    def notify(self, message):
        pass

    def broadcast(self, message):
        pass


class MockNotification(Notification):
    def __init__(self, token, chat_id, logger):
        Notification.__init__(self, token, chat_id, logger)
        self.logger.debug('MockNotification initialized')

    def notify(self, message):
        if (len(self.chat_id_list) == 1):
            self.logger.info('Message {} send to user {}'.format(message, self.chat_id))

    def broadcast(self, message):
        self.logger.debug("Initialized Broadcast")
        for identification in self.chat_id_list:
            self.logger.info("Message {} send to {}".format(message, identification))
        self.logger.debug("Finished broadcasting")
