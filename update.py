import numpy as np
import pandas as pd
import datetime as dt


def update_daily_before(context):
    # Update Function, which should be called prior to the beginning of each trading dates.

    for stock in context.stock_pool:
        if context.now in list(context.split_factor[context.split_factor["stock_code"] == stock]["ex_date"] / 1000000):
            temp_split_factor = context.split_factor[(context.split_factor["stock_code"] == stock) & (context.split_factor["ex_date"] == context.now * 1000000)]
            context.stock_map1[stock] = int(context.stock_map1[stock] * float(temp_split_factor["split_factor"]))
            context.output_message("'%s' '%s' has split with the factor of '%f'." % (context.now, stock, float(temp_split_factor["split_factor"])))
        # Stock Dividends Adjustment
        if context.now in list(context.dividends[context.dividends["stock_code"] == stock]["ex_dividend_date"]):
            temp_dividends = context.dividends[(context.dividends["stock_code"] == stock) & (context.dividends["ex_dividend_date"] == context.now)]
            context.cur_money_rest += context.stock_map1[stock] / float(temp_dividends["round_lot"]) * float(temp_dividends["dividend_cash_before_tax"])
            context.output_message("'%s' '%s' has got dividends with the factor of (%f per %f)." 
                % (context.now, stock, float(temp_dividends["dividend_cash_before_tax"]), float(temp_dividends["round_lot"])))
        # Stock Split Adjustment
    new_lock_money = 0.0
    for stock in context.stock_pool:
        stock_vol = context.stock_map1[stock]
        cur_close_price = float(context.object_all[(context.object_all["datetime"] == context.now * 1000000) & (context.object_all["object"] == stock)]["close"])
        cur_lock_money = cur_close_price * stock_vol
        new_lock_money += cur_lock_money
    for index in context.index_pool:
        index_vol = context.index_map1[index]
        cur_close_price = float(context.object_all[(context.object_all["datetime"] == context.now * 1000000) & (context.object_all["object"] == index)]["close"])
        cur_lock_money = cur_close_price * index_vol
        new_lock_money += cur_lock_money
    context.cur_money_lock = new_lock_money
    context.cur_capital = context.cur_money_rest + context.cur_money_lock
    return 0


def update_daily_after(context):
    # Update Function, which should be called after the end of each trading dates.

    context.my_capital = context.my_capital.append(
        {"date": context.now, "code": "CASH", "money_rest": context.cur_money_rest},
    ignore_index=True)
    # Code Above updates my_capital - CASH.

    stock_money_lock = 0.0
    for stock in context.stock_pool:
        cur_close_price = float(context.object_all[(context.object_all["datetime"] == context.now * 1000000) & (context.object_all["object"] == stock)]["close"])
        context.my_object = context.my_object.append(
            {"date": context.now, "code": stock, "type": "STOCK", "hold_vol": context.stock_map1[stock], "hold_days": context.stock_map2[stock]},
        ignore_index=True)
        # Update my_object - individual STOCK.
        context.my_capital = context.my_capital.append(
            {"date": context.now, "code": stock, "money_lock": cur_close_price * context.stock_map1[stock], "deal_action": "hold", "object_vol": context.stock_map1[stock]},
        ignore_index=True)
        stock_money_lock += cur_close_price * context.stock_map1[stock]
        # Update my_capital - individual STOCK.
    context.my_capital = context.my_capital.append(
        {"date": context.now, "code": "STOCK", "money_lock": stock_money_lock},
    ignore_index=True)
    # Code Above updates STOCK info.

    index_money_lock = 0.0
    for index in context.index_pool:
        cur_close_price = float(context.object_all[(context.object_all["datetime"] == context.now * 1000000) & (context.object_all["object"] == index)]["close"])
        context.my_object = context.my_object.append(
            {"date": context.now, "code": index, "type": "INDEX", "hold_vol": context.index_map1[index], "hold_days": context.index_map2[index]},
        ignore_index=True)
        # 以上是部分my_object的更新操作(循环内)
        context.my_capital = context.my_capital.append(
            {"date": context.now, "code": index, "money_lock": cur_close_price * context.index_map1[index], "deal_action": "hold", "object_vol": context.index_map1[index]},
        ignore_index=True)
        index_money_lock += cur_close_price * context.index_map1[index]
        # 以上是部分my_capital的更新操作(循环内)
    context.my_capital = context.my_capital.append(
        {"date": context.now, "code": "INDEX", "money_lock": index_money_lock},
    ignore_index=True)
    # Code Above updates INDEX info.

    context.my_capital = context.my_capital.append(
        {"date": context.now,"code": "ALL","capital": context.cur_capital,"money_lock": (stock_money_lock + index_money_lock),"money_rest": context.cur_money_rest},
    ignore_index=True)
    # Code Above updates my_capital - ALL.
    
    context.date_iter += 1
    context.now = context.date_list[context.date_iter]
    if context.now != "End":
        for stock in context.stock_pool:
            context.stock_map2[stock] += 1
        for index in context.index_pool:
            context.index_map2[index] += 1
        context.output_message("%s update complete!" % (context.date_list[context.date_iter - 1]))
        return False
    else:
        context.output_message("%s update complete!" % (context.date_list[context.date_iter - 1]))
        context.output_message("%s is the last day, update end!" % (context.date_list[context.date_iter - 1]))
        return True
    # Code Above updates the date info of context.
