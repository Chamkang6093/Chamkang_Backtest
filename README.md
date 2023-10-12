# Backtest System

## Description
* Established whole structure of a low-frequency backtest system for simulating executing algorithmic trading strategies, when dividends, splitting, rights exiting and transaction slippage, fees are considered.

## Instructions
1.  Before running the code, a directory at the designated path ("address" in the code) should be created.
2.  Then, import backtest-related data to this directory, which can be directly downloaded to local environment via rqalpha Lib at initialization stage (at August 2020), including:
    * stock daily prices data
    * stock dividends data
    * stock split factor data
    * stock cumulative adjustment factor data
    * stock supendend days data
    * trading dates data
    * indices daily prices data
3.  Finally, creating another directory at the designated path ("address_output" in the code) to store backtest results.
4.  The functionalities of each files are as follows:
    * main.py - Overall structure of this backtest system.
    * environment.py - Class stores global variables.
    * update.py - Functions update environment prior to or after each days.
    * compute.py - Calculation of results and plotting curves.
    * user.py - Functions that connecting the environment and the users. Mainly includes the buying and selling functions.
    * strategy.py - Write own code to simulate strategies.
5.  Write your own strategy in strategy.py in accordance with the format. You can also modify user.py if neccessary.
6.  Run main.py to execute your strategy.

## Notes
1.  Generally, this backtest system does not support short-selling, please avoid using to prevent from error.
2.  This backtest system does not support futures and options, please avoid using to prevent from error.
3.  When it comes to developing strategies, the following key words are reserved, please avoid using to prevent from error.
    * context.benchmark 
    * context.serb_ratio 
    * context.sers_ratio
    * context.slippage
    * context.ini_capital 
    * context.ini_stock_pool
    * context.ini_index_pool 
    * context.ini_start_time
    * context.ini_end_time 
    * context.if_ini_stock
    * context.if_ini_index
    * context.if_log_info
    * context.risk_free_ratio 
    * context.address 
    * context.address_output
    * context.my_object
    * context.my_capital
    * context.object_all
    * context.cur_capital
    * context.cur_money_lock
    * context.cur_money_rest
    * context.stock_pool
    * context.stock_map1
    * context.stock_map2
    * context.index_pool
    * context.index_map1
    * context.index_map2
    * context.f1
    * context.f2
    * context.f3
    * context.f4
    * context.f5
    * context.f6
    * context.dividends
    * context.split_factor
    * context.suspended_days
    * context.ex_cum_factor

## Main Reference
* <a style='color: black;' href='https://github.com/ricequant/rqalpha' target='_blank'>https://github.com/ricequant/rqalpha</a>
