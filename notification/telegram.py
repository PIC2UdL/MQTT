import telepot

from .main import Notification


class TelegramNotification(Notification):
    def __init__(self, token, chat_id, logger):
        Notification.__init__(self, token, chat_id, logger)
        self.bot = telepot.Bot(self.token)


    def notify(self, message):
        if (len(self.chat_id_list) == 1):
            self.logger.debug('Message {} send to user {}'.format(message, self.chat_id))
            self.bot.sendMessage(self.chat_id, message)

    def broadcast(self, message):
        for chat_id in self.chat_id_list:
            self.bot.sendMessage(chat_id, message)
