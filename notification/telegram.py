import telepot

from .main import Notification


class TelegramNotification(Notification):
    def __init__(self, token, chat_id, logger):
        Notification.__init__(self, token, chat_id, logger)
        self.bot = telepot.Bot(self.token)

    def notify(self, user, message):
        logger.debug('Message {} send to user {}'.format(message, user))
        self.bot.sendMessage(self.chat_id, message)

    def broadcast(self, message):
        for chat_id in self.chat_id_list:
            self.bot.sendMessage(self.chat_id, message)