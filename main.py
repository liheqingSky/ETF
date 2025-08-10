from utils.data import get_index_data
from utils.csv import load_data_from_csv, save_data_to_csv
from utils.config import index_map

if __name__ == '__main__':
    for symbol, name in index_map.items():
        # data = get_index_data(symbol)
        # save_data_to_csv(data, filename=f"{symbol}_{name}_详细数据.csv")

        data = load_data_from_csv(filename=f"{symbol}_{name}_详细数据.csv")

        # print(data)
        break
