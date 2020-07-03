from telegram import Bot
from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler, MessageHandler, Filters


class Lucy:
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    def __init__(self):
        self.lucy_bot = Bot(token="1375720857:AAG7QlWP9eRTnWriPFUBambTrApKXuxcG_E")
        self.updater = Updater(token="1375720857:AAG7QlWP9eRTnWriPFUBambTrApKXuxcG_E", use_context=True)
        self.dispatcher = self.updater.dispatcher
        start_handler = CommandHandler('start', Lucy.start)
        echo_handler = MessageHandler(Filters.text & (~Filters.command), Lucy.echo)
        caps_handler = CommandHandler('caps', Lucy.caps)
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(echo_handler)
        self.dispatcher.add_handler(caps_handler)

    @staticmethod
    def start(updater, context):
        context.bot.send_message(chat_id=updater.effective_chat.id, text="I'm a bot, please talk to me!")

    @staticmethod
    def echo(updater, context):
        context.bot.send_message(chat_id=updater.effective_chat.id, text=updater.message.text)

    @staticmethod
    def caps(updater, context):
        text_caps = ' '.join(context.args).upper()
        context.bot.send_message(chat_id=updater.effective_chat.id, text=text_caps)

    def send(self, msg):
            """
            Send a mensage to a telegram user specified on chatId
            chat_id must be a number!
            """
            self.lucy_bot.send_message(546616705, text=msg)

    def run(self):
        self.updater.start_polling()
        self.updater.idle()


