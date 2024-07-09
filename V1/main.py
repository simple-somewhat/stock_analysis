# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import tushare as ts
import json
import pandas as pd
import math


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def fill_stock():
    f = open("response.json", encoding='utf-8')
    return json.load(f)


def pd_learn():
    obj = pd.Series([4.5, 7.3, 1.1], index=[0, 2, 4])
    print(obj.reindex(range(6)))
    print(obj.reindex(range(6), method='ffill'))
    pass


def is_double_equal(list_double, target_double):
    for item in list_double:
        if math.isclose(item, target_double, rel_tol=0.0001):
            return True
    return False


def chose_stock_by_recent_price(pd_stocks):
    max_close = max(pd_stocks["close"])
    min_close = min(pd_stocks["close"])
    max_volume = max(pd_stocks["volume"])
    min_volume = min(pd_stocks["volume"])
    if not (max_close-min_close)/min_close > 0.15:
        return False
    close_diff = pd_stocks["close"].diff(periods=-1)
    close_diff[-1] = 0
    close_original = pd_stocks["close"].shift(periods=-1, fill_value=100000)
    # 这里不需要对最后一个做特殊处理，NaN/NaN 还是会填充NaN
    pct_change = close_diff/close_original
    max_pct_change = max(pct_change)
    if max_pct_change < 0:
        return False
    if not (is_double_equal(pct_change[0:4], max_pct_change)):
        return False
    if (pct_change < 0).sum() > 9:
        return False
    if not (math.isclose(max_pct_change, 0.1, rel_tol=0.001) is False or max_pct_change in pct_change[0:4]):
        return False
    if not (max_volume/min_volume > 3):
        return False
    return True


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    print(ts.__version__)
    # first_stock_data = pd.DataFrame(ts.get_hist_data('600955', start='2021-01-05', end='2022-01-27'))
    # print(first_stock_data[:20]["close"])
    #print(max(first_stock_data[:20]["close"]))
    #print(first_stock_data.columns)
    #print(first_stock_data[0:20][first_stock_data["close"] > 45])
    # print(ts.get_hist_data('600955', start='2021-01-05', end='2022-01-27')[:15])
    # chose_stock_by_recent_price(ts.get_hist_data('600955', start='2021-01-05', end='2022-01-27')[:20])

    #pd_learn()
    #print(first_stock_data.index)
    #print(first_stock_data.columns)
    # list_chosed_stocks = []
    # stock_all = fill_stock()
    # for stock in stock_all["data"]:
    #     if chose_stock_by_recent_price(ts.get_hist_data(stock["secu_code"], start='2021-10-05', end='2022-01-27')[:20]):
    #         list_chosed_stocks.append(stock["secu_code"])
    # print(list_chosed_stocks)
    print(ts.get_stock_basics())
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
