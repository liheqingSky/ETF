import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime, timedelta

def get_index_data(symbol="sz399989", period_year=10):
    end_date = datetime.now().date()
    start_date = (datetime.now() - timedelta(days= period_year * 365)).date()  # 大约10年前
    df = ak.stock_zh_index_daily(symbol=symbol)
    if df.empty:
        print(f"Error fetching data for {symbol} by stock_zh_index_daily")
        return df

    df['date'] = pd.to_datetime(df['date']).dt.date  # 将'date'列转换为日期类型
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    return df