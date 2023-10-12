import numpy as np
import pandas as pd


def index_order_shares(context, index_code, amount):
    # Indices Transaction Function, sell or buy a certain amount of indices.
    
    amount = int(amount)
    # Code Below is the case that order is denied, due to too few amount.
    if amount < 100 and amount >= 0:
        context.output_message("Transaction-'%s' buy '%d' '%s' failed!" % (context.now, amount, index_code))
        context.output_message(" Not enough amount for even one transaction!")
        return 1
    # Code Below is the buy order case.
    elif amount >= 100:
        buy_price = float(context.object_all[(context.object_all["datetime"] == context.now * 1000000) & (context.object_all["object"] == index_code)]["close"])
        buy_vol, buy_rest = divmod(amount, 100)
        buy_vol *= 100
        if context.cur_money_rest < buy_price * buy_vol * (1 + context.serb_ratio + context.slippage):
            context.output_message("Transaction-'%s' buy '%d' '%s' failed!" % (context.now, buy_vol, index_code))
            context.output_message(" Not enough money for this transaction!")
            context.output_message("However, open position operation will be made!")
            if context.cur_money_rest < buy_price * 100 * (1 + context.serb_ratio + context.slippage):
                context.output_message("Transaction-'%s' buy '100' '%s' failed!" % (context.now, index_code))
                context.output_message(" Not enough money for even one transaction!")
                return 1
            else:
                amount = int(context.cur_money_rest / buy_price / (1 + context.serb_ratio + context.slippage))
                buy_vol, buy_rest = divmod(amount, 100)
                buy_vol *= 100
        context.cur_capital -= buy_vol * buy_price * (context.serb_ratio + context.slippage)
        # update context.cur_capital
        context.cur_money_lock += buy_vol * buy_price
        # update context.cur_money_lock
        context.cur_money_rest -= buy_vol * buy_price * (1 + serb_ratio + slippage)
        # update context.cur_money_lock
        context.my_capital = context.my_capital.append(
            {
                "date": context.now, 
                "code": index_code, 
                "money_lock": buy_vol * buy_price,
                "deal_action": "buy",
                "deal_price": buy_price,
                "object_vol": buy_vol,
                "fees": buy_vol * buy_price * context.serb_ratio,
                "slippage": buy_vol * buy_price * context.slippage
            },
        ignore_index=True)
        # update context.my_capital, and reflect buying action as one record
        if index_code in context.index_pool:
            context.index_map1[index_code] += buy_vol
            # update index volume, which is already in context.index_map1
        else:
            context.index_pool.append(index_code)
            context.index_map1[index_code] = buy_vol
            context.index_map2[index_code] = 0
            # update index, which is not in the context variable
        return 0
    # Code Below is the sell order case.
    else:
        if index_code not in context.index_pool:
            context.output_message("Transaction-'%s' sell '%d' '%s' failed!" % (context.now, amount, index_code))
            context.output_message(" Not holding this index at all!")
            return 1
        sell_vol = -amount
        if context.index_map1[index_code] < sell_vol:
            context.output_message("Transaction-'%s' sell '%.2f' '%s' failed!" % (context.now, sell_vol, index_code))
            context.output_message(" Short sale is not allowed. Not enough indices for selling!")
            context.output_message("However, close position operation will be made!")
            sell_vol = context.index_map1[index_code]
        sell_price = float(context.object_all[(context.object_all["datetime"] == context.now * 1000000) & (context.object_all["object"] == index_code)]["close"])
        context.cur_capital -= sell_price * sell_vol * (context.sers_ratio + context.slippage)
        # update context.cur_capital
        context.cur_money_lock -= sell_price * sell_vol
        # update context.cur_money_lock
        context.cur_money_rest += sell_price * sell_vol * (1 - context.sers_ratio - context.slippage)
        # update context.cur_money_lock
        context.index_map1[index_code] -= sell_vol
        # update context.index_map1, i.e., holding volume
        context.my_capital = context.my_capital.append(
            {
                "date": context.now,
                "code": index_code,
                "money_lock": sell_price * sell_vol,
                "deal_action": "sell",
                "deal_price": sell_price,
                "object_vol": sell_vol,
                "fees": sell_vol * sell_price * context.sers_ratio,
                "slippage": sell_vol * sell_price * context.slippage
            },
        ignore_index=True)
        # update context.my_capital, and reflect selling action as a record
        if context.index_map1[index_code] == 0:
            context.index_pool.remove(index_code)
            del context.index_map1[index_code]
            del context.index_map2[index_code]
        # delete index with closed position from context
        return 0


def index_order_percent(context, index_code, percent):
    # Indices Transaction Function, sell or buy a certain amount of indices.
    # For buying, the amount is a certain percentage of current cash.
    # For selling, the amount is a certain percentage of current position.

    if (percent == 0) or (percent > 1) or (percent < -1):
        raise Exception("Invaild input: percent in fuction - index_order_percent().")
    elif (percent > 0) and (percent <= 1):
        buy_price = float(context.object_all[(context.object_all["datetime"] == context.now * 1000000) & (context.object_all["object"] == index_code)]["close"])
        amount = int(context.cur_money_rest * percent / buy_price / (1 + context.serb_ratio + context.slippage))
        index_order_shares(context, index_code, amount)
    else:
        if index_code not in context.index_pool:
            context.output_message("Transaction-'%s' sell '%f' percent '%s' failed!" % (context.now, percent, index_code))
            context.output_message(" Not holding this index at all!")
            return 1
        else: 
            amount = int(context.index_map1[index_code] * percent)
            index_order_shares(context, index_code, amount)
    return 0  


def index_order_value(context, index_code, value):
    # Indices Transaction Function, sell or buy a certain cash of indices.

    if value == 0:
        raise Exception("Invaild input: value in fuction - index_order_value().")
    elif value > 0:
        buy_price = float(context.object_all[(context.object_all["datetime"] == context.now * 1000000) & (context.object_all["object"] == index_code)]["close"])
        amount = int(value / buy_price  / (1 + context.serb_ratio + context.slippage))
        index_order_shares(context, index_code, amount)
    else:
        sell_price = float(context.object_all[(context.object_all["datetime"] == context.now * 1000000) & (context.object_all["object"] == index_code)]["close"])        
        amount = int(value / sell_price / (1 + context.sers_ratio + context.slippage))
        index_order_shares(context, index_code, amount)
    return 0  


def stock_order_shares(context, stock_code, amount):
    # Stock Transaction Function, sell or buy a certain amount of stocks.

    amount = int(amount)
    # Code Below is the case that stock is suspended.
    if context.now in list(context.suspended_days[context.suspended_days["stock_code"] == stock_code]["suspended_date"]):
        context.output_message("'%s' '%s' suspended! Cannot trade this day!" % (context.now, stock_code))
        return 1
    # Code Below is the case that order is denied, due to too few amount.
    if amount < 100 and amount >= 0:
        context.output_message("Transaction-'%s' buy '%d' '%s' failed!" % (context.now, amount, stock_code))
        context.output_message(" Not enough amount for even one transaction!")
        return 1
    # Code Below is the buy order case.
    elif amount >= 100:
        buy_price = float(context.object_all[(context.object_all["datetime"] == context.now * 1000000) & (context.object_all["object"] == stock_code)]["close"])
        buy_vol, buy_rest = divmod(amount, 100)
        buy_vol *= 100
        if context.cur_money_rest < buy_price * buy_vol * (1 + context.serb_ratio + context.slippage):
            context.output_message("Transaction-'%s' buy '%d' '%s' failed!" % (context.now, buy_vol, stock_code))
            context.output_message(" Not enough money for this transaction!")
            context.output_message("However, open position operation will be made!")
            if context.cur_money_rest < buy_price * 100 * (1 + context.serb_ratio + context.slippage):
                context.output_message("Transaction-'%s' buy '100' '%s' failed!" % (context.now, stock_code))
                context.output_message(" Not enough money for even one transaction!")
                return 1
            else:
                amount = int(context.cur_money_rest / buy_price / (1 + context.serb_ratio + context.slippage))
                buy_vol, buy_rest = divmod(amount, 100)
                buy_vol *= 100
        context.cur_capital -= buy_vol * buy_price * (context.serb_ratio + context.slippage)
        # update context.cur_capital
        context.cur_money_lock += buy_vol * buy_price
        # update context.cur_money_lock
        context.cur_money_rest -= buy_vol * buy_price * (1 + context.serb_ratio + context.slippage)
        # update context.cur_money_lock
        context.my_capital = context.my_capital.append(
            {
                "date": context.now,
                "code": stock_code,
                "money_lock": buy_vol * buy_price,
                "deal_action": "buy",
                "deal_price": buy_price,
                "object_vol": buy_vol,
                "fees": buy_vol * buy_price * context.serb_ratio,
                "slippage": buy_vol * buy_price * context.slippage
            },
        ignore_index=True)
        # update context.my_capital, and reflect buying action as one record
        if stock_code in context.stock_pool:
            context.stock_map1[stock_code] += buy_vol
            # update stock volume, which is already in context.stock_map1
        else:
            context.stock_pool.append(stock_code)
            context.stock_map1[stock_code] = buy_vol
            context.stock_map2[stock_code] = 0
            # update stock, which is not in the context variable
        return 0
    # Code Below is the sell order case.
    else:
        if stock_code not in context.stock_pool:
            context.output_message("Transaction-'%s' sell '%d' '%s' failed!" % (context.now, amount, stock_code))
            context.output_message(" Not holding this stock at all!")
            return 1
        sell_vol = -amount
        if context.stock_map1[stock_code] < sell_vol:
            context.output_message("Transaction-'%s' sell '%.2f' '%s' failed!" % (context.now, sell_vol, stock_code))
            context.output_message(" Short sale is not allowed. Not enough stocks for selling!")
            context.output_message("However, close position operation will be made!")
            sell_vol = context.stock_map1[stock_code]
        sell_price = float(context.object_all[(context.object_all["datetime"] == context.now * 1000000) & (context.object_all["object"] == stock_code)]["close"])
        context.cur_capital -= sell_price * sell_vol * (context.sers_ratio + context.slippage)
        # update context.cur_capital
        context.cur_money_lock -= sell_price * sell_vol
        # update context.cur_money_lock
        context.cur_money_rest += sell_price * sell_vol * (1 - context.sers_ratio - context.slippage)
        # update context.cur_money_lock
        context.stock_map1[stock_code] -= sell_vol
        # update context.stock_map1, i.e., holding volume
        context.my_capital = context.my_capital.append(
            {
                "date": context.now,
                "code": stock_code,
                "money_lock": sell_price * sell_vol,
                "deal_action": "sell",
                "deal_price": sell_price,
                "object_vol": sell_vol,
                "fees": sell_vol * sell_price * context.sers_ratio,
                "slippage": sell_vol * sell_price * context.slippage
            },
        ignore_index=True)
        # update context.my_capital, and reflect selling action as a record
        if context.stock_map1[stock_code] == 0:
            context.stock_pool.remove(stock_code)
            del context.stock_map1[stock_code]
            del context.stock_map2[stock_code]
        # delete stock with closed position from context
        return 0
        

def stock_order_percent(context, stock_code, percent):
    # Stock Transaction Function, sell or buy a certain amount of stocks.
    # For buying, the amount is a certain percentage of current cash.
    # For selling, the amount is a certain percentage of current position.

    if (percent == 0) or (percent > 1) or (percent < -1):
        raise Exception("Invaild input: percent in fuction - stock_order_percent().")
    elif (percent > 0) and (percent <= 1):  
        buy_price = float(context.object_all[(context.object_all["datetime"] == context.now * 1000000) & (context.object_all["object"] == stock_code)]["close"])
        amount = int(context.cur_money_rest * percent / buy_price / (1 + context.serb_ratio + context.slippage))
        stock_order_shares(context, stock_code, amount)
    else:
        if stock_code not in context.stock_pool:
            context.output_message("Transaction-'%s' sell '%f' percent '%s' failed!" % (context.now, percent, stock_code))
            context.output_message(" Not holding this stock at all!")
            return 1
        else: 
            amount = int(context.stock_map1[stock_code] * percent)
            stock_order_shares(context, stock_code, amount)
    return 0  
    

def stock_order_value(context, stock_code, value):
    # Stock Transaction Function, sell or buy a certain cash of stocks.

    if value == 0:
        raise Exception("Invaild input: value in fuction - stock_order_value().")
    elif value > 0:
        buy_price = float(context.object_all[(context.object_all["datetime"] == context.now * 1000000) & (context.object_all["object"] == stock_code)]["close"])
        amount = int(value / buy_price / (1 + context.serb_ratio + context.slippage))
        stock_order_shares(context, stock_code, amount)
    else:
        sell_price = float(context.object_all[(context.object_all["datetime"] == context.now * 1000000) & (context.object_all["object"] == stock_code)]["close"])
        amount = int(value / sell_price / (1 + context.sers_ratio + context.slippage))
        stock_order_shares(context, stock_code, amount)
    return 0  


def if_dividend(context, stock_code):
    if context.now in list(context.dividends[context.dividends["stock_code"] == stock_code]["ex_dividend_date"]):
        return 1
    else:
        return 0


def if_split(context, stock_code):
    if context.now in list(context.split_factor[context.split_factor["stock_code"] == stock_code]["ex_date"] / 1000000):
        return 1
    else:
        return 0
    
    
def if_suspend(context, stock_code):
    if context.now in list(context.suspended_days[context.suspended_days["stock_code"] == stock_code]["suspended_date"]):
        return 1
    else:
        return 0


def get_index_data(context, index_code, request_vol = 0, field = ["close"]):
    if request_vol < 0:
        raise Exception("Invaild input: request_vol in fuction - get_index_data(). Number cannot be negative!")
    if "datetime" not in field:
        field.append("datetime")
    temp_data = context.object_all[(context.object_all["object"] == index_code) & (context.object_all["datetime"] <= context.now * 1000000)][field]
    if request_vol > int(temp_data[field[0]].count()):
        raise Exception("Invaild input: request_vol in fuction - get_index_data(). Number of requested data is out of bound!")
    if request_vol == 0:
        return temp_data
    else:
        return temp_data[-request_vol:]


def get_stock_data(context, stock_code, request_vol = 0, field = ["close"], if_skip_suspend = True, if_ex = False, if_dynamic_former = False):
    if request_vol < 0:
        raise Exception("Invaild input: request_vol in fuction - get_stock_data(). Number cannot be negative!")
    if if_ex == False and if_dynamic_former == True:
        raise Exception("Invaild input: if_ex or if_dynamic_former in fuction - get_stock_data(). They are contradictory!")
    if "datetime" not in field:
        field.append("datetime")
    temp_data = context.object_all[(context.object_all["object"] == stock_code) & (context.object_all["datetime"] <= context.now * 1000000)][field]
    if if_skip_suspend:
        for x in list(context.suspended_days[context.suspended_days["stock_code"] == stock_code]["suspended_date"]):
            temp_data.drop(temp_data[temp_data["datetime"] == x * 1000000].index, axis=0, inplace=True)
    if request_vol > int(temp_data[field[0]].count()):
        raise Exception("Invaild input: request_vol in fuction - get_stock_data(). Number of requested data is out of bound!")
    if request_vol > 0:
        temp_data = temp_data[-request_vol:]
    if not if_ex:
        return temp_data
    else:
        temp_ex_cum_factor = context.ex_cum_factor[(context.ex_cum_factor["stock_code"] == stock_code) & (context.ex_cum_factor["start_date"] <= context.now * 1000000)]
        ex_date_min = list(temp_ex_cum_factor["start_date"])
        ex_date_max = ex_date_min[:]
        ex_date_max.remove(0)
        ex_date_max.append(100000000000000)
        temp_data["ex_cum_factor"] = 1
        for i in range(len(ex_date_min)):
            temp_data.loc[temp_data[(temp_data["datetime"] >= ex_date_min[i]) & (temp_data["datetime"] < ex_date_max[i])].index, "ex_cum_factor"] = float(temp_ex_cum_factor[temp_ex_cum_factor["start_date"] == ex_date_min[i]]["ex_cum_factor"])
        for x in field:
            if x in ["open", "close", "high", "low", "limit_up", "limit_down"]:
                if not if_dynamic_former:
                    temp_data[x] = temp_data[x] * temp_data["ex_cum_factor"]
                else:
                    temp_data[x] = temp_data[x] * temp_data["ex_cum_factor"] / float(temp_data.iloc[-1]["ex_cum_factor"])
        return temp_data