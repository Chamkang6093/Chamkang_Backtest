# Low-Frequency Backtest System Construction

## Description
* Established whole structure of a low-frequency backtest system for simulating executing algorithmic trading strategies, when dividends, splitting, rights exiting and transaction slippage, fees are considered.
* Tested the functionality of this system by using a simple sector rotation strategy.

## Instructions
1.  Before running the code, a directory at the designated path ("address" in the code) should be created.
2.  Import backtest-related data to this directory, which can be directly downloaded to local environment via rqalpha Lib at initialization stage (at August 2020), including:
    * stocks.h5 - stock daily prices data
    * dividends.h5 - stock dividends data
    * split_factor.h5 - stock split factor data
    * ex_cum_factor.h5 - stock cumulative adjustment factor data
    * suspended_days.h5 - stock supendend days data
    * trading_dates.npy - trading dates data
    * indexes.h5 - indices daily prices data
3.  Create another directory at the designated path ("address_output" in the code) to store backtest results.
4.  Write your own strategy in strategy.py in accordance with the format. You can also modify user.py if neccessary.
5.  Run main.py to execute your strategy.

## Notes
1.  Generally, this backtest system does not support short-selling, please avoid using to prevent from error.
2.  This backtest system does not support futures and options, please avoid using to prevent from error.
3.  The functionalities of each file are as follows:
    * main.py - Overall structure of this backtest system.
    * environment.py - The class storing global variables.
    * update.py - The functions updating environment prior to or after each days.
    * compute.py - The function calculating results and plotting curves.
    * user.py - The functions connecting the environment and the users, which are mainly the buying and selling functions.
    * strategy.py - The functions with own code to simulate strategies.
4.  When it comes to developing strategies, the following key words are reserved, please avoid using to prevent from error.
    * context.address
    * context.address_output
    * context.benchmark
    * context.cur_capital
    * context.cur_money_lock
    * context.cur_money_rest
    * context.dividends
    * context.ex_cum_factor
    * context.f1
    * context.f2
    * context.f3
    * context.f4
    * context.f5
    * context.f6
    * context.if_ini_index
    * context.if_ini_stock
    * context.if_log_info
    * context.index_map1
    * context.index_map2
    * context.index_pool
    * context.ini_capital
    * context.ini_end_time
    * context.ini_index_pool
    * context.ini_start_time
    * context.ini_stock_pool
    * context.my_capital
    * context.my_object
    * context.object_all      
    * context.risk_free_ratio
    * context.serb_ratio
    * context.sers_ratio
    * context.slippage
    * context.split_factor
    * context.stock_map1
    * context.stock_map2
    * context.stock_pool
    * context.suspended_days

## Main Reference
* <a href='https://github.com/ricequant/rqalpha' target='_blank'>https://github.com/ricequant/rqalpha</a>
