import talib
import numpy as np

from .user import *


def init(context):
    context.food_list = ["600519.XSHG","603288.XSHG"]
    context.food_percent = 0.6
    context.food = 0
    # Food and Beverage
    context.medi_list = ["600276.XSHG","600436.XSHG"]
    context.medi_percent = 0.4
    context.medi = 0
    # Medicine and Biotech
    context.asc_signal = 2
    context.desc_signal = 2
    context.high_macd_list = {}
    context.low_macd_list = {}
    # Other Strategy Parameters


def my_strategy(context):
	# Demo: A simple sector rotation strategy mainly to illustrate how to use this library.

    if (context.now <= 20190101 and context.now >= 20180101) or (context.now <= 20200315 and context.now >= 20200101):
        buy_signal = 5
        sell_signal = 1
    else: 
        buy_signal = 5
        sell_signal = 3
    universe = [x for x in context.ini_stock_pool if not if_suspend(context, x)]
    buylist_1 = []
    sellist_1 = []
    
    if (context.now <= 20190101 and context.now >= 20180101) or (context.now <= 20200315 and context.now >= 20200101):
        buylist_2 = []
        sellist_2 = []
        for stock in set(universe) - set(context.stock_pool):
            close = get_stock_data(context, stock, 34, if_ex = True)
            macd, macdsignal, macdhist = talib.MACD(close["close"].values, fastperiod=12, slowperiod=26, signalperiod=9)
            macd = float(macd[np.isnan(macd) == False])
            if macd > 0:
                if stock not in context.high_macd_list.keys():
                    context.high_macd_list[stock] = (1, macd)
                else:
                    context.high_macd_list[stock] = (context.high_macd_list[stock][0] + 1, (context.high_macd_list[stock][0] * context.high_macd_list[stock][1] + macd) / (context.high_macd_list[stock][0] + 1))
                if context.high_macd_list[stock][0] >= buy_signal:
                    buylist_1.append((stock, classify(context, stock)))
                    context.output_message("Generate Buying Signal 1 - %s without current positions" % (stock))
                    context.output_message(" In consecutive %d days, short-period MA Lines have been over long-period MA Lines." % (buy_signal))
            elif macd < 0:
                if stock in context.high_macd_list.keys():
                    del context.high_macd_list[stock]
            
            context.close_extra = get_stock_data(context, stock, (context.asc_signal + 1), if_ex = True)
            count = 0
            for i in range(context.asc_signal):
                if close["close"].values[- (1 + i)] > close["close"].values[- (2 + i)]:
                    count += 1
            if count == context.asc_signal:
                buylist_2.append((stock, classify(context, stock)))
                context.output_message("Generate Buying Signal 2 - %s without current positions" % (stock))
                context.output_message(" In consecutive %d days, this underlying has been generating revenues." % (context.asc_signal))
            
        for stock in set(universe) & set(context.stock_pool):
            close = get_stock_data(context, stock, 34, if_ex = True)
            macd, macdsignal, macdhist = talib.MACD(close["close"].values, fastperiod=12, slowperiod=26, signalperiod=9)
            macd = float(macd[np.isnan(macd)==False])
            macdsignal = macdsignal[np.isnan(macdsignal)==False]
            macdhist = macdhist[np.isnan(macdhist)==False]
            if macd < 0:
                if stock not in context.low_macd_list.keys():
                    context.low_macd_list[stock] = 1
                else:
                    context.low_macd_list[stock] += 1
                if context.low_macd_list[stock] >= sell_signal:
                    sellist_1.append((stock, classify(context, stock)))
                    context.output_message("Generate Selling Signal 1 - %s with current positions" % (stock))
                    context.output_message(" In consecutive %d days, short-period MA Lines have been below long-period MA Lines." % (sell_signal))

            elif macd > 0:
                if stock in context.low_macd_list.keys():
                    del context.low_macd_list[stock]
            
            context.close_extra = get_stock_data(context, stock, (context.desc_signal + 1), if_ex = True)
            count = 0
            for i in range(context.desc_signal):
                if close["close"].values[- (1 + i)] < close["close"].values[- (2 + i)]:
                    count += 1
            if count == context.desc_signal:
                sellist_2.append((stock, classify(context, stock)))
                context.output_message("Generate Selling Signal 2 - %s with current positions" % (stock))
                context.output_message(" In consecutive %d days, this underlying has been suffering from losses." % (context.desc_signal))
    
        for stock in set(sellist_1) | set(sellist_2):
            stock_order_shares(context, stock[0], -context.stock_map1[stock[0]])
            switch(context, stock[0])
        
        if context.food == 0:
            best = (" ", 0)
            for y in set([x[0] for x in buylist_1 if x[1] == "food"]) & set([x[0] for x in buylist_2 if x[1] == "food"]):
                if context.high_macd_list[y][1] > best[1]:
                    best = (y, context.high_macd_list[y][1])
            if best != (" ", 0):
                stock_order_value(context, best[0], context.cur_capital * context.food_percent)
                del context.high_macd_list[best[0]]
                context.food = 1
        if context.medi == 0:
            best = (" ", 0)
            for y in set([x[0] for x in buylist_1 if x[1] == "medi"]) & set([x[0] for x in buylist_2 if x[1] == "medi"]):
                if context.high_macd_list[y][1] > best[1]:
                    best = (y, context.high_macd_list[y][1])
            if best != (" ", 0):
                stock_order_value(context, best[0], context.cur_capital * context.medi_percent)
                del context.high_macd_list[best[0]]
                context.medi = 1
    
    else:
        for stock in set(universe) - set(context.stock_pool):
            close = get_stock_data(context, stock, 34, if_ex = True)
            macd, macdsignal, macdhist = talib.MACD(close["close"].values, fastperiod=12, slowperiod=26, signalperiod=9)
            macd = float(macd[np.isnan(macd)==False])
            if macd > 0:
                if stock not in context.high_macd_list.keys():
                    context.high_macd_list[stock] = (1, macd)
                else:
                    context.high_macd_list[stock] = (context.high_macd_list[stock][0] + 1, (context.high_macd_list[stock][0] * context.high_macd_list[stock][1] + macd) / (context.high_macd_list[stock][0] + 1))
                if context.high_macd_list[stock][0] >= buy_signal:
                    buylist_1.append((stock, classify(context, stock)))
                    context.output_message("Generate Buying Signal - %s without current positions" % (stock))
                    context.output_message(" In consecutive %d days, short-period MA Lines have been over long-period MA Lines." % (buy_signal))
            elif macd < 0:
                if stock in context.high_macd_list.keys():
                    del context.high_macd_list[stock]
        for stock in set(universe) & set(context.stock_pool):
            close = get_stock_data(context, stock, 34, if_ex = True)
            macd, macdsignal, macdhist = talib.MACD(close["close"].values, fastperiod=12, slowperiod=26, signalperiod=9)
            macd = float(macd[np.isnan(macd)==False])
            macdsignal = macdsignal[np.isnan(macdsignal)==False]
            macdhist = macdhist[np.isnan(macdhist)==False]
            if macd < 0:
                if stock not in context.low_macd_list.keys():
                    context.low_macd_list[stock] = 1
                else:
                    context.low_macd_list[stock] += 1
                if context.low_macd_list[stock] >= sell_signal:
                    sellist_1.append((stock, classify(context, stock)))
                    context.output_message("Generate Selling Signal - %s with current positions" % (stock))
                    context.output_message(" In consecutive %d days, short-period MA Lines have been below long-period MA Lines." % (sell_signal))
            elif macd > 0:
                if stock in context.low_macd_list.keys():
                    del context.low_macd_list[stock]
        for stock in sellist_1:
            stock_order_shares(context, stock[0], -context.stock_map1[stock[0]])
            switch(context, stock[0])
        if context.food == 0:
            best = (" ", 0)
            for y in [x[0] for x in buylist_1 if x[1] == "food"]:
                if context.high_macd_list[y][1] > best[1]:
                    best = (y, context.high_macd_list[y][1])
            if best != (" ", 0):
                stock_order_value(context, best[0], context.cur_capital * context.food_percent)
                del context.high_macd_list[best[0]]
                context.food = 1
        if context.medi == 0:
            best = (" ", 0)
            for y in [x[0] for x in buylist_1 if x[1] == "medi"]:
                if context.high_macd_list[y][1] > best[1]:
                    best = (y, context.high_macd_list[y][1])
            if best != (" ", 0):
                stock_order_value(context, best[0], context.cur_capital * context.medi_percent)
                del context.high_macd_list[best[0]]
                context.medi = 1


def classify(context, stock):
    if stock in context.food_list:
        return "food"
    else:
        return "medi"


def switch(context, stock):
    if stock in context.food_list:
        context.food = 0
    elif stock in context.medi_list:
        context.medi = 0