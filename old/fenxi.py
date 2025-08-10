import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from datetime import datetime, timedelta

# 1. 获取指数历史数据（以上证指数为例）
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

# 2. 计算技术指标
    # 计算技术指标并生成信号
def calculate_indicators_with_signals(df):
    # 均线
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA_Signal'] = np.where(df['MA5'] > df['MA20'], 1, -1)

    # MACD
    short_ema = df['close'].ewm(span=12, adjust=False).mean()
    long_ema = df['close'].ewm(span=26, adjust=False).mean()
    df['DIF'] = short_ema - long_ema
    df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
    df['MACD'] = 2 * (df['DIF'] - df['DEA'])
    df['MACD_Signal'] = np.where(df['DIF'] > df['DEA'], 1, -1)

    # RSI
    delta = df['close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['RSI_Signal'] = np.where(df['RSI'] > 70, -1, np.where(df['RSI'] < 30, 1, 0))

    # KDJ
    low_min = df['low'].rolling(window=9).min()
    high_max = df['high'].rolling(window=9).max()
    rsv = (df['close'] - low_min) / (high_max - low_min) * 100
    df['K'] = rsv.ewm(alpha=1 / 3, adjust=False).mean()
    df['D'] = df['K'].ewm(alpha=1 / 3, adjust=False).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']
    df['KDJ_Signal'] = np.where(df['K'] > df['D'], 1, -1)

    # 布林带
    df['BOLL'] = df['close'].rolling(window=20).mean()
    df['BOLL_UP'] = df['BOLL'] + 2 * df['close'].rolling(window=20).std()
    df['BOLL_DN'] = df['BOLL'] - 2 * df['close'].rolling(window=20).std()

    # 信号整合
    df['Strong_Buy'] = np.where(
        (df['MA_Signal'] == 1) &
        (df['MACD_Signal'] == 1) &
        (df['RSI_Signal'] == 1) &
        (df['KDJ_Signal'] == 1),
        True, False
    )
    df['Strong_Sell'] = np.where(
        (df['MA_Signal'] == -1) &
        (df['MACD_Signal'] == -1) &
        (df['RSI_Signal'] == -1) &
        (df['KDJ_Signal'] == -1),
        True, False
    )

    return df

# 可视化并标注信号
def plot_with_signals(df):
    fig, axes = plt.subplots(6, 1, figsize=(14, 20), sharex=True)
    fig.suptitle("Index Technical Analysis with Signals", fontsize=16)

    # 1. 价格与均线
    axes[0].plot(df.index, df['close'], label='Close Price', color='black')
    axes[0].plot(df.index, df['MA5'], label='MA5', color='blue')
    axes[0].plot(df.index, df['MA20'], label='MA20', color='green')
    axes[0].set_title("Price and Moving Averages")
    axes[0].legend()

    # 标注信号
    for idx, row in df.iterrows():
        if row['Strong_Buy']:
            axes[0].text(idx, row['close'] * 1.001, 'Strong Buy', color='green', fontsize=8, ha='center')
        elif row['Strong_Sell']:
            axes[0].text(idx, row['close'] * 0.999, 'Strong Sell', color='red', fontsize=8, ha='center')

    # 2. MACD
    axes[1].plot(df.index, df['DIF'], label='DIF', color='blue')
    axes[1].plot(df.index, df['DEA'], label='DEA', color='red')
    axes[1].bar(df.index, df['MACD'], label='MACD', color='gray')
    axes[1].set_title("MACD")
    axes[1].legend()

    # 标注信号
    for idx, row in df.iterrows():
        if row['MACD_Signal'] == 1:
            axes[1].text(idx, row['DIF'] * 1.05, 'MACD Buy', color='green', fontsize=8, ha='center')
        elif row['MACD_Signal'] == -1:
            axes[1].text(idx, row['DIF'] * 0.95, 'MACD Sell', color='red', fontsize=8, ha='center')

    # 3. RSI
    axes[2].plot(df.index, df['RSI'], label='RSI', color='purple')
    axes[2].axhline(70, color='red', linestyle='--')
    axes[2].axhline(30, color='green', linestyle='--')
    axes[2].set_title("RSI")
    axes[2].legend()

    # 标注信号
    for idx, row in df.iterrows():
        if row['RSI_Signal'] == 1:
            axes[2].text(idx, row['RSI'] * 0.95, 'RSI Buy', color='green', fontsize=8, ha='center')
        elif row['RSI_Signal'] == -1:
            axes[2].text(idx, row['RSI'] * 1.05, 'RSI Sell', color='red', fontsize=8, ha='center')

    # 4. KDJ
    axes[3].plot(df.index, df['K'], label='%K', color='blue')
    axes[3].plot(df.index, df['D'], label='%D', color='red')
    axes[3].plot(df.index, df['J'], label='%J', color='green')
    axes[3].axhline(80, color='red', linestyle='--')
    axes[3].axhline(20, color='green', linestyle='--')
    axes[3].set_title("KDJ")
    axes[3].legend()

    # 标注信号
    for idx, row in df.iterrows():
        if row['KDJ_Signal'] == 1:
            axes[3].text(idx, row['K'] * 0.95, 'KDJ Buy', color='green', fontsize=8, ha='center')
        elif row['KDJ_Signal'] == -1:
            axes[3].text(idx, row['K'] * 1.05, 'KDJ Sell', color='red', fontsize=8, ha='center')

    # 5. 布林带
    axes[4].plot(df.index, df['close'], label='Close Price', color='black')
    axes[4].plot(df.index, df['BOLL'], label='BOLL', color='blue')
    axes[4].plot(df.index, df['BOLL_UP'], label='BOLL_UP', color='red')
    axes[4].plot(df.index, df['BOLL_DN'], label='BOLL_DN', color='green')
    axes[4].set_title("Bollinger Bands")
    axes[4].legend()

    # 6. 成交量
    axes[5].bar(df.index, df['volume'], label='Volume', color='gray')
    axes[5].set_title("Trading Volume")
    axes[5].legend()

    # 格式化日期
    date_form = DateFormatter("%m-%d")
    axes[-1].xaxis.set_major_formatter(date_form)
    plt.tight_layout()
    # plt.show()
    plt.savefig(
        fname=f"趋势分析.jpg",  # 必须参数
        dpi=300,
        bbox_inches="tight"
    )

# 4. 主程序
if __name__ == "__main__":
    # 获取数据
    df = get_index_data()
    print("原始数据样例：")
    print(df.head())

    # 计算指标
    df = calculate_indicators_with_signals(df)
    print("\n指标计算样例：")
    print(df[['close', 'MA5', 'MA20', 'DIF', 'DEA', 'MACD', 'RSI', 'BOLL', 'K', 'D', 'J', 'volume']].tail())

    # 绘制图表
    plot_with_signals(df)