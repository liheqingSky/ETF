import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class ETFAnalyzer:
    def __init__(self, data, short_window=50, long_window=200):
        """
        Initialize the ETFAnalyzer with a DataFrame containing historical price data.
        The DataFrame should have at least two columns: 'Date' and 'Close'.
        """
        self.short_window = short_window
        self.long_window = long_window

        self.data = data
        self.data['Date'] = pd.to_datetime(self.data['date']).dt.date  # 将'date'列转换为日期类型
        self.data.set_index('Date', inplace=True)
        self.data.drop(columns=['date'], inplace=True)

    def calculate_moving_averages(self):
        """
        Calculate short-term and long-term moving averages.
        """
        self.data[f'SMA_{self.short_window}'] = self.data['close'].rolling(window=self.short_window).mean()
        self.data[f'SMA_{self.long_window}'] = self.data['close'].rolling(window=self.long_window).mean()

    def analyze_trend(self):
        """
        Analyze the trend based on moving averages.
        """
        if f'SMA_50' not in self.data.columns or f'SMA_200' not in self.data.columns:
            self.calculate_moving_averages()

        signals = pd.DataFrame(index=self.data.index)
        signals['signal'] = 0.0
        signals['signal'][self.short_window:] = np.where(
            self.data[f'SMA_50'][self.short_window:] > self.data[f'SMA_200'][self.short_window:], 1.0, 0.0
        )
        signals['positions'] = signals['signal'].diff()
        return signals

    def plot_price_with_signals(self, start_date=None, end_date=None):
        """
        Plot the closing prices along with buy/sell signals over a specified period.
        """
        if start_date is None:
            start_date = self.data.index.min()
        if end_date is None:
            end_date = self.data.index.max()

        sliced_data = self.data.loc[start_date:end_date]
        signals = self.analyze_trend().loc[start_date:end_date]

        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(sliced_data['close'], label='Close Price')
        ax.plot(sliced_data[f'SMA_50'], label=f'{self.short_window}-Day SMA')
        ax.plot(sliced_data[f'SMA_200'], label=f'{self.long_window}-Day SMA')

        # Plot buy signals
        ax.plot(signals.loc[signals.positions == 1].index,
                sliced_data[f'SMA_50'][signals.positions == 1],
                '^', markersize=10, color='g', lw=0, label='Buy Signal')

        # Plot sell signals
        ax.plot(signals.loc[signals.positions == -1].index,
                sliced_data[f'SMA_50'][signals.positions == -1],
                'v', markersize=10, color='r', lw=0, label='Sell Signal')

        ax.legend(loc='best')
        plt.title(f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")} Prices & Signals')
        plt.show()

    def find_high_low_points(self, start_date=None, end_date=None):
        """
        Find high and low points within a specified date range and calculate relevant statistics.
        """
        if start_date is None:
            start_date = self.data.index.min()
        if end_date is None:
            end_date = self.data.index.max()

        sliced_data = self.data.loc[start_date:end_date]
        max_point = sliced_data['close'].idxmax()
        min_before_max = sliced_data.loc[:max_point]['close'].idxmin()
        min_after_max = sliced_data.loc[max_point:]['close'].idxmin()

        stats = {
            'Max Point': max_point,
            'Price at Max Point': sliced_data.loc[max_point]['close'],
            'Min Before Max Point': min_before_max,
            'Price at Min Before Max Point': sliced_data.loc[min_before_max]['close'],
            'Time from Min to Max (years)': (max_point - min_before_max).days / 365,
            'Gain from Min to Max (%)': ((sliced_data.loc[max_point]['close'] - sliced_data.loc[min_before_max][
                'close']) / sliced_data.loc[min_before_max]['close']) * 100,
            'Min After Max Point': min_after_max,
            'Price at Min After Max Point': sliced_data.loc[min_after_max]['close'],
            'Time from Max to Min (years)': (min_after_max - max_point).days / 365,
            'Loss from Max to Min (%)': ((sliced_data.loc[min_after_max]['close'] - sliced_data.loc[max_point][
                'close']) / sliced_data.loc[max_point]['close']) * 100,
            'Current Price': sliced_data.iloc[-1]['close'],
            'Current Gain/Loss from Max (%)': ((sliced_data.iloc[-1]['close'] - sliced_data.loc[max_point]['close']) /
                                               sliced_data.loc[max_point]['close']) * 100,
        }
        return stats

    def plot_high_low_points(self, start_date=None, end_date=None):
        """
        Plot high and low points within a specified date range and annotate relevant statistics.
        """
        if start_date is None:
            start_date = self.data.index.min()
        if end_date is None:
            end_date = self.data.index.max()

        sliced_data = self.data.loc[start_date:end_date]
        stats = self.find_high_low_points(start_date, end_date)

        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(sliced_data['close'], label='Close Price')

        # Highlight max point
        ax.scatter(stats['Max Point'], stats['Price at Max Point'], c='red', s=100, zorder=5, label='Max Point')
        ax.annotate(f"Max: ${stats['Price at Max Point']:.2f}\n{stats['Max Point'].strftime('%Y-%m-%d')}",
                    xy=(stats['Max Point'], stats['Price at Max Point']),
                    xytext=(stats['Max Point'], stats['Price at Max Point'] + 5),
                    arrowprops=dict(facecolor='black', shrink=0.05))

        # Highlight min before max point
        ax.scatter(stats['Min Before Max Point'], stats['Price at Min Before Max Point'], c='green', s=100, zorder=5,
                   label='Min Before Max')
        ax.annotate(
            f"Min Before Max: ${stats['Price at Min Before Max Point']:.2f}\n{stats['Min Before Max Point'].strftime('%Y-%m-%d')}\n"
            f"Time to Max: {stats['Time from Min to Max (years)']:.2f} years\n"
            f"Gain: {stats['Gain from Min to Max (%)']:.2f}%",
            xy=(stats['Min Before Max Point'], stats['Price at Min Before Max Point']),
            xytext=(stats['Min Before Max Point'], stats['Price at Min Before Max Point'] - 10),
            arrowprops=dict(facecolor='black', shrink=0.05))

        # Highlight min after max point
        ax.scatter(stats['Min After Max Point'], stats['Price at Min After Max Point'], c='blue', s=100, zorder=5,
                   label='Min After Max')
        ax.annotate(
            f"Min After Max: ${stats['Price at Min After Max Point']:.2f}\n{stats['Min After Max Point'].strftime('%Y-%m-%d')}\n"
            f"Time to Min: {stats['Time from Max to Min (years)']:.2f} years\n"
            f"Loss: {stats['Loss from Max to Min (%)']:.2f}%",
            xy=(stats['Min After Max Point'], stats['Price at Min After Max Point']),
            xytext=(stats['Min After Max Point'], stats['Price at Min After Max Point'] - 10),
            arrowprops=dict(facecolor='black', shrink=0.05))

        # Annotate current price
        ax.axhline(y=sliced_data.iloc[-1]['close'], color='gray', linestyle='--', label='Current Price')
        ax.annotate(f"Current Price: ${sliced_data.iloc[-1]['close']:.2f}\n"
                    f"Current Gain/Loss from Max: {stats['Current Gain/Loss from Max (%)']:.2f}%",
                    xy=(sliced_data.index[-1], sliced_data.iloc[-1]['close']),
                    xytext=(sliced_data.index[-1], sliced_data.iloc[-1]['close'] + 5),
                    arrowprops=dict(facecolor='black', shrink=0.05))

        ax.legend(loc='best')
        plt.title(f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")} High & Low Points Analysis')
        plt.show()
#
# def analyze_index(df, index_map, plot=False):
#     """
#     分析指数的历史数据，包括最高点前后的最低点及可视化支持。
#
#     参数:
#         df (DataFrame): 包含 'date' 和 'close' 列的指数历史数据
#         index_code (str): 指数代码（如 'sh000991'）
#         plot (bool): 是否绘制趋势图，默认 False
#
#     返回:
#         dict: 包含分析结果的字典
#     """
#     if df.empty:
#         return None
#
#     index_code = index_map
#
#     # 数据预处理
#     df['date'] = pd.to_datetime(df['date'])
#     df = df.sort_values('date').reset_index(drop=True)
#
#     # 获取全局最高点
#     max_value = df['close'].max()
#     max_rows = df[df['close'] == max_value]
#     max_date = max_rows.iloc[0]['date']  # 若多个最高点，取第一个
#
#     # 分割数据：最高点前、最高点后
#     df_before_max = df[df['date'] < max_date]
#     df_after_max = df[df['date'] > max_date]
#
#     # 获取最低点前（最高点前的最低点）
#     min_before_value = df_before_max['close'].min() if not df_before_max.empty else None
#     min_before_date = df_before_max[df_before_max['close'] == min_before_value]['date'].iloc[
#         0] if min_before_value is not None else None
#
#     # 获取最低点后（最高点后的最低点）
#     min_after_value = df_after_max['close'].min() if not df_after_max.empty else None
#     min_after_date = df_after_max[df_after_max['close'] == min_after_value]['date'].iloc[
#         0] if min_after_value is not None else None
#
#     # 当前点位
#     current_value = df['close'].iloc[-1]
#     current_date = df['date'].iloc[-1]
#
#     # 计算涨跌幅
#     if min_before_value is not None and max_value is not None:
#         rise_before_drop = ((max_value - min_before_value) / min_before_value) * 100
#     else:
#         rise_before_drop = None
#
#     if max_value is not None and min_after_value is not None:
#         drop_after_peak = ((max_value - min_after_value) / max_value) * 100
#     else:
#         drop_after_peak = None
#
#     if min_after_value is not None and current_value is not None:
#         rebound_after_min = ((current_value - min_after_value) / min_after_value) * 100
#     else:
#         rebound_after_min = None
#
#     if max_value is not None and current_value is not None:
#         gap_to_peak = ((max_value - current_value) / current_value) * 100
#     else:
#         gap_to_peak = None
#
#     # 计算时间跨度
#     def calc_time_span(start_date, end_date):
#         if start_date is None or end_date is None:
#             return None
#         delta = (end_date - start_date).days
#         years = delta // 365
#         months = (delta % 365) // 30
#         return f"{years}年{months}个月"
#
#     time_before = calc_time_span(min_before_date, max_date) if min_before_date else None
#     time_after = calc_time_span(max_date, min_after_date) if min_after_date else None
#     time_since_min = calc_time_span(min_after_date, current_date) if min_after_date else None
#
#     # 可视化支持
#     if plot:
#         plt.figure(figsize=(12, 6))
#         plt.rcParams['font.sans-serif'] = ['SimHei']
#         plt.plot(df['date'], df['close'], label='指数趋势', color='gray')
#
#         # 标注关键点
#         if max_date:
#             plt.scatter(max_date, max_value, color='red', label='最高点')
#             plt.text(max_date, max_value * 1.02, '最高点', color='red', fontsize=9, ha='center')
#         if min_before_date:
#             plt.scatter(min_before_date, min_before_value, color='green', label='最高点前最低')
#             plt.text(min_before_date, min_before_value * 0.98, '前最低', color='green', fontsize=9, ha='center')
#         if min_after_date:
#             plt.scatter(min_after_date, min_after_value, color='blue', label='最高点后最低')
#             plt.text(min_after_date, min_after_value * 0.98, '后最低', color='blue', fontsize=9, ha='center')
#         if current_date:
#             plt.scatter(current_date, current_value, color='orange', label='当前点位')
#             plt.text(current_date, current_value * 1.02, '当前', color='orange', fontsize=9, ha='center')
#
#         if drop_after_peak:
#             plt.scatter(current_date, drop_after_peak, color='orange', label='极限跌幅')
#             plt.text(current_date, current_value * 1.02, '当前', color='orange', fontsize=9, ha='center')
#
#         plt.title(f"{index_map.get(index_code, index_code)} 趋势分析")
#         plt.xlabel("日期")
#         plt.ylabel("收盘价")
#         plt.legend()
#         plt.grid(True)
#         plt.gcf().autofmt_xdate()  # 自动旋转日期标签
#
#         plt.savefig(
#             fname=f"{index_map[index_code]}趋势分析.jpg",  # 必须参数
#             dpi=300,
#             bbox_inches="tight"
#         )
#         # plt.show()
#
#     # 返回结果
#     result = {
#         '代号': index_code,
#         '名称': index_map.get(index_code, '未知指数'),
#         '最高点': round(max_value, 2) if max_value is not None else None,
#         '最高点日期': max_date.strftime('%Y-%m-%d') if max_date else None,
#         '最高点前最低点': round(min_before_value, 2) if min_before_value is not None else None,
#         '最高点前最低点日期': min_before_date.strftime('%Y-%m-%d') if min_before_date else None,
#         '最高点前涨跌幅': round(rise_before_drop, 2) if rise_before_drop is not None else None,
#         '最高点前涨跌时间': time_before,
#         '最高点后最低点': round(min_after_value, 2) if min_after_value is not None else None,
#         '最高点后最低点日期': min_after_date.strftime('%Y-%m-%d') if min_after_date else None,
#         '最高点后跌幅': round(drop_after_peak, 2) if drop_after_peak is not None else None,
#         '最高点后下跌时间': time_after,
#         '当前点位': round(current_value, 2) if current_value is not None else None,
#         '当前点位日期': current_date.strftime('%Y-%m-%d') if current_date else None,
#         '当前涨幅': round(rebound_after_min, 2) if rebound_after_min is not None else None,
#         '当前上涨时间': time_since_min,
#         '当前到最高点涨幅缺口': round(gap_to_peak, 2) if gap_to_peak is not None else None
#     }
#
#     return result