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
        start_handler = CommandHandler('start', self.start)
        price_handler = CommandHandler('price', self.price)
        advice_handler = CommandHandler('advice', self.advice)
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(price_handler)
        self.dispatcher.add_handler(advice_handler)

        self.curr_price = None
        self.orders_history = []

    def start(self, context):
        context.bot.send_message(chat_id=self.updater.effective_chat.id, text="Good things will come!")

    def advice(self, context):
        # self.orders_history
        # context.bot.send_message(chat_id=self.updater.effective_chat.id, text=self.updater.message.text)
        pass

    def price(self, context):
        current_price = self.curr_price
        context.bot.send_message(chat_id=self.updater.effective_chat.id,
                                 text="Current price is: {price}".format(price=current_price))

    def send(self, msg):
        """
        Send a mensage to a telegram user specified on chatId
        chat_id must be a number!
        """
        self.lucy_bot.send_message(546616705, text=msg)

    def run(self):
        self.updater.start_polling()
        self.updater.idle()
