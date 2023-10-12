import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt


def compute(context):
    # Backtest Result Function, which computes yield curves and other revenue indicators after trading.
    
    # 1. Code Below gets required data to plot yield curves
    benchmark_x = list(context.trading_dates[(context.trading_dates <= context.ini_end_time) & (context.trading_dates >= context.ini_start_time)])
    if context.benchmark in list(context.f2.keys()):
        base = float(context.object_all[(context.object_all["datetime"] == context.ini_start_time * 1000000) & (context.object_all["object"] == context.benchmark)]["open"])
        # Choose the start date open price of index as the benchmark
        benchmark_price = {
            dt.datetime.strptime(str(x), "%Y%m%d").date(): 
            float(context.object_all[(context.object_all["datetime"] == x * 1000000) & (context.object_all["object"] == context.benchmark)]["close"])
            for x in benchmark_x
        }
    elif context.benchmark in list(context.f1.keys()):
        temp_ex_cum_factor = context.ex_cum_factor[context.ex_cum_factor["stock_code"] == context.benchmark]
        base = float(context.object_all[(context.object_all["datetime"] == context.ini_start_time * 1000000) & (context.object_all["object"] == context.benchmark)]["open"])
        base *= float(temp_ex_cum_factor[temp_ex_cum_factor["start_date"] <= context.ini_start_time * 1000000]["ex_cum_factor"].max())
        # Choose the adjusted start date open price of stock as the benchmark
        benchmark_price = {
            dt.datetime.strptime(str(x), "%Y%m%d").date(): 
            float(context.object_all[(context.object_all["datetime"] == x * 1000000) & (context.object_all["object"] == context.benchmark)]["close"]) * float(temp_ex_cum_factor[temp_ex_cum_factor["start_date"] <= x * 1000000]["ex_cum_factor"].max())
            for x in benchmark_x
        }
    benchmark_y = {
        key: ((value / base) - 1)
        for key, value in benchmark_price.items()
    }
    # Get the data to plot benchmark yield curve
    initial = float(context.my_capital[(context.my_capital["code"] == "ALL") & (context.my_capital["date"] == "Initial")]["capital"])
    portfolio_price = {
        dt.datetime.strptime(str(x), "%Y%m%d").date(): 
        float(context.my_capital[(context.my_capital["code"] == "ALL") & (context.my_capital["date"] == x)]["capital"])
        for x in benchmark_x
        }
        # Choose the initial capital (cash and stocks/indices) as the benchmark
    portfolio_y = {
        key: ((value / initial) - 1)
        for key, value in portfolio_price.items()
    }
    # Get the data to plot portofolio yield curve
    profit_ratio = pd.DataFrame([benchmark_y, portfolio_y], index=[context.benchmark, "my_capital"]).T

    # 2. Code Below gets required data to plot annualized yield curves
    benchmark_year_y = {
        key: ((value / base) ** (365 / ((key - dt.datetime.strptime(str(context.ini_start_time), "%Y%m%d").date()).days + 1)) - 1) 
        for key, value in benchmark_price.items()
        }
    portfolio_year_y = {
        key: ((value / initial) ** (365 / ((key - dt.datetime.strptime(str(context.ini_start_time), "%Y%m%d").date()).days + 1)) - 1) 
        for key, value in portfolio_price.items()
        }
    profit_ratio_annualized = pd.DataFrame([benchmark_year_y, portfolio_year_y], index=[context.benchmark, "my_capital"]).T

    # 3. Code Below computes Alpha and Beta of the strategy
    price = pd.DataFrame([benchmark_price, portfolio_price], index=[context.benchmark, "my_capital"]).T
    profit_ratio_dif = price.diff() / price.shift(1)
    profit_ratio_dif.iloc[0] = profit_ratio.iloc[0]
    beta = profit_ratio_dif.cov().iloc[0][1] / profit_ratio_dif.cov().iloc[0][0]
    alpha = (profit_ratio_annualized["my_capital"] - context.risk_free_ratio - beta * (profit_ratio_annualized[context.benchmark] - context.risk_free_ratio)).mean()

    # 4. Code Below computes annualized volitility and Sharpe ratio of the strategy
    volatility = float(np.sqrt(244 * profit_ratio_dif.var()[1]))
    sharpe_ratio = (profit_ratio_annualized["my_capital"].iloc[-1] - context.risk_free_ratio) / volatility

    # 5. Code Below computes Max Drawdown of the strategy
    datetime_list = [dt.datetime.strptime(str(x), "%Y%m%d").date() for x in benchmark_x]
    max_drawdown = 0
    max_drawdown_high = datetime_list[0]
    max_drawdown_low = datetime_list[0]     
    temp_high = (initial, datetime_list[0])
    for x in datetime_list:
        if portfolio_price[x] >= temp_high[0]:
            temp_high = (portfolio_price[x], x)
        else:
            if (temp_high[0] - portfolio_price[x]) / temp_high[0] > max_drawdown:
                max_drawdown = (temp_high[0] - portfolio_price[x]) / temp_high[0]
                max_drawdown_high = temp_high[1]
                max_drawdown_low = x

    # 6. Code Below plots yield curves and annualized yield curves
    plt.rc('figure', figsize = (20, 12))
    profit_ratio.plot() 
    plt.axhline(0, color = 'k')
    if max_drawdown != 0:
        plt.fill_between(profit_ratio.loc[max_drawdown_high:max_drawdown_low].index,  profit_ratio.max().max(),  profit_ratio.min().min(), color='y', alpha=0.5)
    # Yield curves
    plt.rc('figure', figsize = (20, 12))
    profit_ratio_annualized[20:].plot()
    plt.axhline(0, color = 'k')            
    # Annualized yield curves

    # 7. Code Below stores the results
    context.result = {}
    context.result["My_Profit_Ratio"] = float(profit_ratio["my_capital"].iloc[-1])
    context.result["My_Profit_Ratio_Annualized"] = float(profit_ratio_annualized["my_capital"].iloc[-1])
    context.result["Benchmark_Profit_Ratio"] = float(profit_ratio[context.benchmark].iloc[-1])
    context.result["Benchmark_Profit_Ratio_Annualized"] = float(profit_ratio_annualized[context.benchmark].iloc[-1])
    context.result["Alpha"] = alpha
    context.result["Beta"] = beta
    context.result["Volatility"] = volatility
    context.result["Sharpe_Ratio"] = sharpe_ratio
    context.result["Max_Drawdown"] = max_drawdown
    if max_drawdown == 0 :
        context.result["Max_Drawdown_Interval"] = None
    else:
        context.result["Max_Drawdown_Interval_left"] = max_drawdown_high
        context.result["Max_Drawdown_Interval_right"] = max_drawdown_low

    # 8. Code Below outputs the log files
    context.my_capital.to_csv(context.address_output + "/my_capital.csv")
    context.my_object.to_csv(context.address_output + "/my_object.csv")
    context.result = pd.DataFrame([context.result]).T
    context.result = context.result.rename(columns = {0: ""})
    context.result.to_csv(context.address_output + "/results.csv")
    print("\n===================================================")
    print("Results:")
    print(context.result)
    print("===================================================\n")
    context.output_message("Complete - Backtest !")
    return