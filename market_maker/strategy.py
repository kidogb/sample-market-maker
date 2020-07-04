import talib
from market_maker.utils import log
from .lucy_bot import Lucy
import pandas as pd
from datetime import datetime

logger = log.setup_custom_logger('strategy')


class StrategyManager:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.round_trip = {}
        self.orders_history = []
        self.in_position = False
        self.take_a_rest = False
        self.long_condition = False
        self.short_condition = False
        self.exit_long_condition = False
        self.exit_short_condition = False
        self.stop_long_condition = False
        self.stop_short_condition = False
        self.bot = Lucy()
        self.bot.run()

    def ema_cross(self, data, candle=90):
        EMA_SLOW = 258 * candle
        EMA_FAST = 175 * candle
        DD = 0.7625952582816842
        TP = 0.8560976329922
        TRAILING = 0.10114088761330153
        RSI = 10 * candle
        RSI_LOW = 54.89825885458724
        RSI_HIGH = 64.97392476489256

        # EMA_SLOW = 3 * candle
        # EMA_FAST = 2 * candle
        # DD = 0.7625952582816842
        # TP = 0.8560976329922
        # TRAILING = 0.10114088761330153
        # RSI = 2 * candle
        # RSI_LOW = 27.559218467340816
        # RSI_HIGH = 64.73199279543923
        last_data = data.iloc[-1]
        price = last_data['mid']
        self.bot.curr_price = price

        ema_slow = talib.EMA(data['mid'], timeperiod=EMA_SLOW)
        ema_fast = talib.EMA(data['mid'], timeperiod=EMA_FAST)
        rsi = talib.RSI(data['mid'], timeperiod=RSI)

        if len(ema_slow) >= EMA_SLOW + 1:
            prev_ema_fast = ema_fast.values[len(ema_fast) - 2]
            prev_ema_slow = ema_slow.values[len(ema_slow) - 2]
            curr_ema_slow = ema_slow.values[len(ema_slow) - 1]
            curr_ema_fast = ema_fast.values[len(ema_fast) - 1]
            curr_rsi = rsi.values[len(rsi) - 1]

            self.take_a_rest = curr_rsi >= RSI_LOW and curr_rsi <= RSI_HIGH

            self.long_condition = not self.take_a_rest and not self.in_position and prev_ema_fast <= prev_ema_slow and \
                                  curr_ema_fast > curr_ema_slow and price > curr_ema_slow
            self.exit_long_condition = self.in_position and curr_ema_fast < curr_ema_slow and price < curr_ema_slow
            if self.long_condition:
                self.in_position = True
                self.round_trip['start'] = last_data['timestamp']
                self.round_trip['entry'] = price
                self.round_trip['run_up'] = price
                self.round_trip['dd'] = price
                self.round_trip['side'] = "long"
                logger.info("Start Long: %s", price)
                long_str = "--------------------------------------\n{time}: #{id}\nOpen long order: {entry}, " \
                           "lev: x50-100".format(id=len(self.orders_history) + 1,
                                                 time=datetime.strptime(self.round_trip['start'],
                                                                        '%Y-%m-%dT%H:%M:%S.%fZ').strftime(
                                                     "%b %d %Y %H:%M:%S"), entry=self.round_trip['entry'])
                self.bot.send(long_str)

            if self.in_position:
                # re-calculate run_up and dd price and stop_price
                self.round_trip['run_up'] = max(price, self.round_trip['run_up'])
                self.round_trip['dd'] = min(price, self.round_trip['dd'])
                # calculate stop price
                if "stop" in self.round_trip:
                    prev_stop_price = self.round_trip['stop']
                else:
                    prev_stop_price = None
                self.round_trip['stop'] = self.round_trip['entry'] * (1 - DD / 100)
                tp = self.round_trip['entry'] * (1 + TP / 100)
                if price >= tp:
                    # raise stop price
                    self.round_trip['stop'] = (self.round_trip['run_up'] -
                                               self.round_trip['entry']) * TRAILING + self.round_trip['entry']
                if prev_stop_price != self.round_trip['stop']:
                    alter_stop_price_str = "Stop price is: {stop}".format(stop=self.round_trip['stop'])
                    self.bot.send(alter_stop_price_str)
                self.stop_long_condition = price <= self.round_trip['stop']

            if self.stop_long_condition or self.exit_long_condition:
                self.round_trip['end'] = last_data['timestamp']
                self.round_trip['exit'] = price
                order_type = "stop" if self.stop_long_condition else "exit"
                if order_type == "stop":
                    logger.info("Stop long: %s", price)
                else:
                    logger.info("Exit long: %s", price)
                self.round_trip['type'] = order_type
                profit = 100 * (price - self.round_trip['entry']) / self.round_trip['entry']
                self.round_trip['profit'] = profit
                self.round_trip['type'] = order_type
                exit_long_str = "{time}: \n{type} long order #{id} at: {exit}.\nProfit: {profit}" \
                                "\nDrawdown: {dd}. Run up: {ru} \n--------------------------------------\n\n".format(
                    id=len(self.orders_history) + 1,
                    time=datetime.strptime(self.round_trip['start'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime(
                        "%b %d %Y %H:%M:%S"), exit=self.round_trip['exit'], type=self.round_trip['type'].upper(),
                    profit=self.round_trip['profit'], dd=self.round_trip['dd'], ru=self.round_trip['run_up'])
                self.bot.send(exit_long_str)
                self.orders_history.append(self.round_trip)
                self.bot.orders_history = self.orders_history
                pd.DataFrame(self.orders_history).to_csv("xbtusd-orders-history.csv", index=False)
                # reset
                self.round_trip = {}
                self.in_position = False
                self.long_condition = False
                self.exit_long_condition = False
                self.stop_long_condition = False
