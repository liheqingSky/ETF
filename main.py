import os
import pandas as pd

from utils.data import get_index_data
from utils.csv import load_data_from_csv, save_data_to_csv
from utils.config import index_map
from utils.analyzer import ETFAnalyzer


if __name__ == '__main__':
    # Directory to save CSV files
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)

    # Fetch, save, and analyze data for each index
    for symbol, name in index_map.items():
        filename = os.path.join(data_dir, f"{symbol}_{name}_详细数据.csv")

        # Check if file already exists
        if os.path.exists(filename):
            print(f"Loading existing data for {name} ({symbol})...")
            df = load_data_from_csv(filename)
        else:
            print(f"Fetching data for {name} ({symbol})...")
            df = get_index_data(symbol)
            if not df.empty:
                save_data_to_csv(df, filename)

        if df.empty:
            print(f"No data for {name} ({symbol})...")
            continue

        # analyzer = ETFAnalyzer(df)
        #
        # # Plot price with signals
        # analyzer.plot_price_with_signals(pd.Timestamp('2020-01-01'), pd.Timestamp('2023-01-01'))
        #
        # # Plot high and low points
        # analyzer.plot_high_low_points(pd.Timestamp('2020-01-01'), pd.Timestamp('2023-01-01'))

        # print(df)
        # break


        # analyzer = ETFAnalyzer(df)
        #
        # # Plot price with signals
        # analyzer.plot_price_with_signals(pd.Timestamp('2020-01-01'), pd.Timestamp('2023-01-01'))
        #
        # # Plot high and low points
        # analyzer.plot_high_low_points(pd.Timestamp('2020-01-01'), pd.Timestamp('2023-01-01'))