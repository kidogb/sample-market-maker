# # IMPORTS
# import pandas as pd
# import math
# import time
# import sys
# # from bitmex import bitmex
# from market_maker import bitmex
# from datetime import timedelta, datetime
# from dateutil import parser
# from market_maker.settings import settings
# from time import sleep
#
#
#
# # CONSTANTS
# binsizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}
# batch_size = 750
# bitmex_client = bitmex(test=False, apiKey=settings.API_KEY, apiSecret=settings.API_SECRET)
#
#
# # FUNCTIONS
# def minutes_of_new_data(symbol, kline_size, data):
#     if len(data) > 0:
#         old = parser.parse(data["timestamp"].iloc[-1])
#     else:
#         old = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1, reverse=False).result()[0][0]['timestamp']
#     new = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=1, reverse=True).result()[0][0]['timestamp']
#     return old, new
#
#
# def minute_rounder(t):
#     # Rounds to nearest and lower than t.
#     return t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
#
#
# def get_all_bitmex(symbol, start_time, kline_size):
#     data_df = pd.DataFrame()
#     # oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df)
#     # oldest_point = datetime.fromisoformat('2020-01-01 00:05:00+00:00')
#     oldest_point = minute_rounder(start_time)
#     newest_point = oldest_point + timedelta(minute=1)
#     delta_min = (newest_point - oldest_point).total_seconds()/60
#     available_data = math.ceil(delta_min/binsizes[kline_size])
#     rounds = math.ceil(available_data / batch_size)
#     if rounds > 0:
#         for round_num in range(rounds):
#             time.sleep(1)
#             new_time = (oldest_point + timedelta(minutes=round_num * batch_size * binsizes[kline_size]))
#             data = bitmex_client.Trade.Trade_getBucketed(symbol=symbol, binSize=kline_size, count=batch_size,
#                                                          startTime=new_time).result()[0]
#             temp_df = pd.DataFrame(data)
#             data_df = data_df.append(temp_df)
#     data_df.set_index('timestamp', inplace=True)
#     return data_df
#
#
# def run_loop():
#     start = datetime.utcnow()
#     print("Start time: ", start)
#     while True:
#         sleep(60)
#         get_all_bitmex(symbol="XBTUSD", start_time=start, kline_size="1m")
#
#
# def run():
#     # Try/except just keeps ctrl-c from printing an ugly stacktrace
#     try:
#         run_loop()
#     except (KeyboardInterrupt, SystemExit):
#         sys.exit()
