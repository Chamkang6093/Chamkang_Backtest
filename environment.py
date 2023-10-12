import numpy as np
import pandas as pd
import datetime as dt
import h5py


class Environment(object):
    # Environment Class, which stores some global variables / DataFrames changing or not with time going.

    def output_message(self, text):
        print(text)
        if self.if_log_info:
            with open(self.address_output + "/log_info.txt", "a") as f:
                f.write(text + "\n")

    def __init__(self,
                 benchmark = "000300.XSHG",
                 serb_ratio = 0.0008,
                 sers_ratio = 0.0018,
                 slippage = 0,
                 ini_capital = 100000000,
                 ini_stock_pool = ["600519.XSHG","603288.XSHG","600276.XSHG","600436.XSHG"],
                 ini_index_pool = [],
                 ini_start_time = 20190101,
                 ini_end_time = 20200630,
                 if_ini_stock = True,
                 if_ini_index = True,
                 if_log_info = True,
                 risk_free_ratio = 0.027,
                 address = "D:/Workspace",
                 address_output = "D:/Workspace/Output"):
    # Initialization Function

    # *1. Code Below designates the parameters.

        self.benchmark = benchmark
        self.serb_ratio = serb_ratio
        self.sers_ratio = sers_ratio
        self.slippage = slippage
        self.ini_capital = ini_capital
        self.ini_stock_pool = ini_stock_pool
        self.ini_index_pool = ini_index_pool
        self.ini_start_time = ini_start_time
        self.ini_end_time = ini_end_time
        self.if_ini_stock = if_ini_stock
        self.if_ini_index = if_ini_index
        self.if_log_info = if_log_info
        self.risk_free_ratio = risk_free_ratio
        self.address = address
        self.address_output = address_output
        # Code Above initializes all of the important global constant variables, which are designated by users.

        self.my_object = pd.DataFrame([], columns=["date", "code", "type", "hold_vol", "hold_days"])
        dtypes = {"date": "str", "code": "str", "type": "str", "hold_vol": "<i8", "hold_days": "<i8"}
        for x in self.my_object.columns:
            self.my_object[x] = self.my_object[x].astype(dtypes[x])
        if self.if_ini_stock:
        ############# IF THERE ARE HOLDING STOCKS, PLEASE TYPE THE PARAMETERS IN THE FORMAT BELOW #############
        # WARNING: THE SAME STOCK CANNOT POSSESS MORE THAN ONE RECORD
        # EXAMPLE:
            self.my_object = self.my_object.append(
                {"date": "Initial","code": "600031.XSHG","type":"STOCK","hold_vol": 100000,"hold_days": 0},
            ignore_index=True)
        ############# IF THERE ARE HOLDING STOCKS, PLEASE TYPE THE PARAMETERS IN THE FORMAT ABOVE #############
            self.ini_stock_pool.extend(list(self.my_object[self.my_object["type"] == "STOCK"]["code"]))
            self.output_message("Warning: Existing initial stocks!")
        if self.if_ini_index:
        ############# IF THERE ARE HOLDING INDICES, PLEASE TYPE THE PARAMETERS IN THE FORMAT BELOW #############
        # WARNING: THE SAME INDEX CANNOT POSSESS MORE THAN ONE RECORD
        # EXAMPLE:
            self.my_object = self.my_object.append(
                {"date": "Initial","code": "000906.XSHG","type":"INDEX","hold_vol": 50000,"hold_days": 2},
            ignore_index=True)
        ############# IF THERE ARE HOLDING INDICES, PLEASE TYPE THE PARAMETERS IN THE FORMAT ABOVE #############
            self.ini_index_pool.extend(list(self.my_object[self.my_object["type"] == "INDEX"]["code"]))
            self.output_message("Warning: Existing initial indices!")
        # Code Above initializes my_object and some other parameters.

        self.output_message("Complete - Parameters Definition !")
    # *1. Code Above designates the parameters.
    # *2. Code Below checks some of the designated parameters.
    #     And automatically generates some environment variables that do not need to specify by users.

        self.object_all = None
        self.f1 = h5py.File(self.address + "/stocks.h5", "r")
        for stock in self.ini_stock_pool:
            if stock in list(self.f1.keys()):
                stock_temp = pd.DataFrame(self.f1[stock][:])
                stock_temp["object"] = stock
            else:
                if self.if_ini_stock:
                    raise Exception("Invaild input: ini_stock_pool or my_object!")
                else:
                    raise Exception("Invaild input: ini_stock_pool!")
            if type(self.object_all) == type(None):
                self.object_all = stock_temp
            else:
                self.object_all = self.object_all.append(stock_temp)
        self.f2 = h5py.File(self.address + "/indexes.h5", "r")
        for index in self.ini_index_pool:
            if index in list(self.f2.keys()):
                index_temp = pd.DataFrame(self.f2[index][:])
                index_temp["object"] = index
            else:
                if self.if_ini_index:
                    raise Exception("Invaild input: ini_index_pool or my_object!")
                else:
                    raise Exception("Invaild input: ini_index_pool!")
            if type(self.object_all) == type(None):
                self.object_all = index_temp
            else:
                self.object_all = self.object_all.append(index_temp)
        # Code Above verifies the completness of data and correctness of initial capital.

        if self.benchmark in self.ini_stock_pool:
            self.output_message("Benchmark chosen is a stock!")
        elif self.benchmark in self.ini_index_pool:
            self.output_message("Benchmark chosen is an index!")
        else:
            if self.benchmark in list(self.f1.keys()):
                benchmark_temp = pd.DataFrame(self.f1[self.benchmark][:])
                benchmark_temp["object"] = self.benchmark
                self.output_message(" Benchmark chosen is a stock.")
            elif benchmark in list(self.f2.keys()):
                benchmark_temp = pd.DataFrame(self.f2[self.benchmark][:])
                benchmark_temp["object"] = self.benchmark
                self.output_message(" Benchmark chosen is an index.")
            else:
                raise Exception("Invaild input: benchmark!")
            if type(self.object_all) == type(None):
                self.object_all = benchmark_temp
            else:
                self.object_all = self.object_all.append(benchmark_temp)   
        # Code Above verifies the completness of data and correctness of benchmark.

        self.trading_dates = np.load(address + "/trading_dates.npy")
        max_date = int(self.object_all.datetime.max() / 1000000)
        min_date = int(self.object_all[self.object_all.index == 0].datetime.max() / 1000000)
        if self.ini_end_time > max_date:
            raise Exception("Invaild input: ini_end_time!")
        if self.ini_start_time < min_date:
            raise Exception("Invaild input: ini_start_time!")
        if self.ini_end_time not in self.trading_dates:
            self.ini_end_time = self.trading_dates[self.trading_dates < self.ini_end_time].max()
        if self.ini_start_time not in self.trading_dates:
            self.ini_start_time = self.trading_dates[self.trading_dates > self.ini_start_time].min()
        if self.ini_end_time < self.ini_start_time:
            raise Exception("Invaild input: ini_start_time and(or) ini_end_time!")        
        self.date_list = ["Initial"]
        self.date_list.extend(list(self.trading_dates[(self.trading_dates <= self.ini_end_time) & (self.trading_dates >= self.ini_start_time)]))
        self.date_list.append("End")
        self.date_iter = 1
        self.now = self.date_list[self.date_iter]
        # Code Above verifies the correctness of input dates and generates (trading) date lists.
        
        self.output_message("Complete - Parameters Check !")
# *2. Code Above checks some of the designated parameters.
#     And automatically generates some environment variables that do not need to specify by users.
#  3. Code Below copies some stock data to local environment.

        self.dividends = pd.DataFrame(
            [], columns=["book_closure_date","announcement_date","dividend_cash_before_tax","ex_dividend_date","payable_date","round_lot"]
        )
        dtypes={
            "book_closure_date": "<i8",
            "announcement_date": "<i8",
            "dividend_cash_before_tax": "<f8",
            "ex_dividend_date": "<i8",
            "payable_date": "<i8",
            "round_lot": "<f8"
        }
        for x in self.dividends.columns:
            self.dividends[x] = self.dividends[x].astype(dtypes[x])
        self.f3 = h5py.File(self.address + "/dividends.h5", "r")
        for stock in self.ini_stock_pool:
            stock_temp = pd.DataFrame(self.f3[stock][:])
            stock_temp["stock_code"] = stock
            if type(self.dividends) == type(None):
                self.dividends = stock_temp
            else:
                self.dividends = self.dividends.append(stock_temp)
        # stock dividends data
        self.split_factor = pd.DataFrame([],columns=["ex_date","split_factor"])
        dtypes={"ex_date":"<i8","split_factor":"<f8"}
        for x in self.split_factor.columns:
            self.split_factor[x] = self.split_factor[x].astype(dtypes[x])
        self.f4 = h5py.File(self.address + "/split_factor.h5", "r")
        for stock in self.ini_stock_pool:
            stock_temp = pd.DataFrame(self.f4[stock][:])
            stock_temp["stock_code"] = stock
            if type(self.split_factor) == type(None):
                self.split_factor = stock_temp
            else:
                self.split_factor = self.split_factor.append(stock_temp)
        # stock split and bonus factor data
        self.suspended_days = pd.DataFrame([],columns=["suspended_date"])
        dtypes={"suspended_date":"<i8"}
        for x in self.suspended_days.columns:
            self.suspended_days[x] = self.suspended_days[x].astype(dtypes[x])
        self.f5 = h5py.File(self.address + "/suspended_days.h5", "r")
        for stock in self.ini_stock_pool:
            stock_temp = pd.DataFrame(self.f5[stock][:])
            stock_temp["stock_code"] = stock
            if type(self.suspended_days) == type(None):
                self.suspended_days = stock_temp
            else:
                self.suspended_days = self.suspended_days.append(stock_temp)
        self.suspended_days["suspended_date"] = self.suspended_days[0]
        self.suspended_days.drop([0], axis=1, inplace=True)
        # stock suspended days data
        self.ex_cum_factor = pd.DataFrame([],columns=["start_date","ex_cum_factor"])
        dtypes={"start_date":"<i8","ex_cum_factor":"<f8"}
        for x in self.ex_cum_factor.columns:
            self.ex_cum_factor[x] = self.ex_cum_factor[x].astype(dtypes[x])
        self.f6 = h5py.File(self.address + "/ex_cum_factor.h5", "r")    
        for stock in self.ini_stock_pool:
            stock_temp = pd.DataFrame(self.f6[stock][:])
            stock_temp["stock_code"] = stock
            if type(self.ex_cum_factor) == type(None):
                self.ex_cum_factor = stock_temp
            else:
                self.ex_cum_factor = self.ex_cum_factor.append(stock_temp)
        if (self.benchmark not in self.ini_stock_pool) and (self.benchmark in list(self.f1.keys())):
            benchmark_temp = pd.DataFrame(self.f6[self.benchmark][:])
            benchmark_temp["stock_code"] = self.benchmark
            if type(self.ex_cum_factor) == type(None):
                self.ex_cum_factor = benchmark_temp
            else:
                self.ex_cum_factor = self.ex_cum_factor.append(benchmark_temp)
#  3. Code Above copies some stock data to local environment.
#  4. Code Below initializes another very important global variable other than my_object, which records transaction infomation.

        self.my_capital = pd.DataFrame(
            [], columns=["date", "code", "capital", "money_lock", "money_rest", "deal_action", "deal_price", "object_vol", "fees", "slippage"]
        )
        dtypes={
            "date": "<i8",
            "code": "str",
            "capital": "<f8",
            "money_lock": "<f8",
            "money_rest": "<f8",
            "deal_action": "str",
            "deal_price": "<f8",
            "object_vol": "<i8",
            "fees": "<f8",
            "slippage": "<f8"
        }
        for x in self.my_capital.columns:
            self.my_capital[x] = self.my_capital[x].astype(dtypes[x])

        # Code Below initializes my_capital and my_object.
        self.my_capital = self.my_capital.append(
            {"date": "Initial", "code": "CASH", "money_rest": self.ini_capital},
        ignore_index=True)
        # STOCKS
        stock_acc = 0.0
        for stock in self.ini_stock_pool:
            if not self.if_ini_stock:
                self.my_object = self.my_object.append(
                     {"date": "Initial", "code": stock, "type": "STOCK", "hold_vol": 0, "hold_days": 0},
                ignore_index=True)
                # Code Above initializes my_object - STOCK (case without holding stocks).
            else:
                if stock in list(self.my_object["code"]):
                    hold_vol = int(self.my_object[self.my_object["code"] == stock]["hold_vol"])          
                    open_price = float(self.object_all[(self.object_all["datetime"] == self.ini_start_time * 1000000) & (self.object_all["object"] == stock)]["open"])
                    temp_stock_acc = hold_vol * open_price
                    stock_acc += temp_stock_acc
                    self.my_capital = self.my_capital.append(
                        {"date": "Initial", "code": stock, "money_lock": temp_stock_acc, "deal_action": "hold", "deal_price": open_price, "object_vol": hold_vol},
                    ignore_index=True)
                    # Code Above initializes my_capital - individual STOCK (case with holding stocks).
                else:
                    self.my_object = self.my_object.append(
                         {"date": "Initial", "code": stock, "type": "STOCK", "hold_vol": 0, "hold_days": 0},
                    ignore_index=True)
                    # Code Above initializes my_object - STOCK (case without holding stocks).
        self.my_capital = self.my_capital.append(
            {"date": "Initial", "code": "STOCK", "money_lock": stock_acc},
        ignore_index=True)
        # INDICES
        index_acc = 0.0
        for index in self.ini_index_pool:
            if not self.if_ini_index:
                self.my_object = self.my_object.append(
                     {"date": "Initial", "code": index, "type": "INDEX", "hold_vol": 0, "hold_days": 0},
                ignore_index=True)
                # Code Above initializes my_object - INDEX (case without holding indices).
            else:
                if index in list(self.my_object["code"]):
                    hold_vol = int(self.my_object[self.my_object["code"] == index]["hold_vol"])          
                    open_price = float(self.object_all[(self.object_all["datetime"] == self.ini_start_time * 1000000) & (self.object_all["object"] == index)]["open"])
                    temp_index_acc = hold_vol * open_price
                    index_acc += temp_index_acc
                    self.my_capital = self.my_capital.append(
                        {"date": "Initial", "code": index, "money_lock": temp_index_acc, "deal_action": "hold", "deal_price": open_price, "object_vol": hold_vol},
                    ignore_index=True)
                    # Code Above initializes my_capital - individual INDEX (case with holding indices).
                else:
                    self.my_object = self.my_object.append(
                         {"date": "Initial","code": index,"type": "INDEX", "hold_vol": 0, "hold_days": 0},
                    ignore_index=True)
                    # Code Above initializes my_object - INDEX (case with holding indices).
        self.my_capital = self.my_capital.append(
            {"date": "Initial", "code": "INDEX", "money_lock": index_acc},
        ignore_index=True)
        # ALL
        self.my_capital = self.my_capital.append(
            {"date": "Initial","code": "ALL","capital": (self.ini_capital + stock_acc + index_acc), "money_lock": (stock_acc + index_acc), "money_rest": self.ini_capital},
        ignore_index=True)
#  4. Code Above initializes another very important global variable other than my_object, which records transaction infomation.
#  5. Code Below initializes other important variables changing with time going.

        self.cur_capital = float(self.my_capital[self.my_capital["code"]=="ALL"].capital)
        self.cur_money_lock = float(self.my_capital[self.my_capital["code"]=="ALL"].money_lock)
        self.cur_money_rest = float(self.my_capital[self.my_capital["code"]=="ALL"].money_rest)
        # Code Above initializes three attributes of capital using my_capital.

        if not if_ini_stock:
            self.stock_pool = []  # current holding stocks pool
            self.stock_map1 = {}  # current holding volume corresponding to stocks pool
            self.stock_map2 = {}  # current holding time corresponding to stocks pool (measured by trading dates)
        else:
            self.stock_pool = list(self.my_object[(self.my_object["hold_vol"] != 0) & (self.my_object["type"] == "STOCK")]["code"])
            self.stock_map1 = {x: int(self.my_object[self.my_object["code"] == x]["hold_vol"]) for x in self.stock_pool}
            self.stock_map2 = {x: int(self.my_object[self.my_object["code"] == x]["hold_days"]) + 1 for x in self.stock_pool}
        # Code Above initializes three attributes of stocks using my_object.

        if not if_ini_index:
            self.index_pool = []
            self.index_map1 = {}
            self.index_map2 = {}
        else:
            self.index_pool = list(self.my_object[(self.my_object["hold_vol"] != 0) & (self.my_object["type"] == "INDEX")]["code"])
            self.index_map1 = {x: int(self.my_object[self.my_object["code"] == x]["hold_vol"]) for x in self.index_pool}
            self.index_map2 = {x: int(self.my_object[self.my_object["code"] == x]["hold_days"]) + 1 for x in self.index_pool}
        # Code Above initializes three attributes of indices using my_object.

        self.output_message("Complete - Initialization !")
#  5. Code Above initializes other important variables changing with time going.