import akshare as ak
import pandas as pd
from datetime import datetime, timedelta


def fetch_indices(market):
    try:
        if market == 'A':
            # 获取A股指数的实时数据
            indices = ak.stock_zh_index_spot_em()
            # 筛选出宽基指数
            wide_base_indices = indices[indices['板块'].str.contains('综合指数|主要指数', na=False)]
            return wide_base_indices[['代码', '名称']]
        elif market == 'HK':
            # 获取香港股票指数数据
            indices = ak.stock_hk_index_spot_sina()
            return indices[['代码', '名称']]
        elif market == 'US':
            # 获取美国股票指数数据
            indices = ak.us_stock_indexes()
            return indices[['代码', '名称']]
        else:
            raise ValueError("Unsupported market")
    except Exception as e:
        print(f"Error fetching {market} indices: {e}")
        return pd.DataFrame()


def fetch_index_data(code, market, period='daily'):
    try:
        start_date = (datetime.now() - timedelta(days=3650)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')

        if market == 'A':
            data = ak.index_zh_a_hist(symbol=code, period=period, start_date=start_date, end_date=end_date)
        elif market == 'HK':
            data = ak.stock_hk_index_daily_em(symbol=code, start_date=start_date, end_date=end_date)
        elif market == 'US':
            data = ak.us_stock_indexes_daily(symbol=code, start_date=start_date, end_date=end_date)
        else:
            raise ValueError("Unsupported market")

        data['日期'] = pd.to_datetime(data['日期'])
        data.set_index('日期', inplace=True)
        return data
    except Exception as e:
        print(f"Error fetching index data for {code}: {e}")
        return pd.DataFrame()


def analyze_index_data(indices_df, market):
    analysis_results = []
    for code in indices_df['代码']:
        data = fetch_index_data(code, market)
        if data.empty:
            continue

        recent_data = data[(data.index >= (datetime.now() - timedelta(days=3650)))]
        if recent_data.empty:
            continue

        min_value = recent_data['收盘'].min()
        max_value = recent_data['收盘'].max()
        current_value = recent_data['收盘'].iloc[-1]

        min_date = recent_data.loc[recent_data['收盘'] == min_value].index[0]
        max_date = recent_data.loc[recent_data['收盘'] == max_value].index[0]

        fall_from_max = ((current_value - max_value) / max_value) * 100
        rise_from_min = ((current_value - min_value) / min_value) * 100
        rise_to_max = ((max_value - current_value) / current_value) * 100

        analysis_results.append({
            '代号': code,
            '名称': indices_df[indices_df['代码'] == code]['名称'].values[0],
            '最近十年最低值': min_value,
            '最近十年最高值': max_value,
            '当前点位': current_value,
            '最低点日期': min_date.strftime('%Y-%m-%d'),
            '最高点日期': max_date.strftime('%Y-%m-%d'),
            '最高点到最低点的时间 (天)': (min_date - max_date).days,
            '当前最低值到最高值的跌幅 (%)': fall_from_max,
            '最低值到目前的涨幅 (%)': rise_from_min,
            '当前点位离最高位还有多少涨幅 (%)': rise_to_max
        })

    return pd.DataFrame(analysis_results)


def save_to_excel(a_indices, a_analysis, hk_indices, hk_analysis, us_indices, us_analysis):
    try:
        # 保存为Excel文件，文件名包含今天的日期
        today = datetime.now().strftime('%Y%m%d')
        excel_filename = f"indices_analysis_{today}.xlsx"
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            a_indices.to_excel(writer, sheet_name='A股指数', index=False)
            a_analysis.to_excel(writer, sheet_name='A股分析', index=False)
            hk_indices.to_excel(writer, sheet_name='H股指数', index=False)
            hk_analysis.to_excel(writer, sheet_name='H股分析', index=False)
            us_indices.to_excel(writer, sheet_name='美股指数', index=False)
            us_analysis.to_excel(writer, sheet_name='美股分析', index=False)

            for sheet_name in ['A股指数', 'A股分析', 'H股指数', 'H股分析', '美股指数', '美股分析']:
                worksheet = writer.sheets[sheet_name]
                for column_cells in worksheet.columns:
                    length = max(len(str(cell.value)) for cell in column_cells)
                    worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2

        print(f"\nResults saved to {excel_filename}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")


def main():
    # 获取A股宽基指数
    a_indices = fetch_indices('A')

    # # 获取H股指数
    # hk_indices = fetch_indices('HK')
    #
    # # 获取美股指数
    # us_indices = fetch_indices('US')
    #
    # # 分析A股指数
    # a_analysis = analyze_index_data(a_indices, 'A')
    #
    # # 分析H股指数
    # hk_analysis = analyze_index_data(hk_indices, 'HK')
    #
    # # 分析美股指数
    # us_analysis = analyze_index_data(us_indices, 'US')

    # 打印表格
    print("A股指数:")
    print(a_indices)
    print("\nH股指数:")
    print(hk_indices)
    print("\n美股指数:")
    print(us_indices)
    print("\nA股分析:")
    print(a_analysis)
    print("\nH股分析:")
    print(hk_analysis)
    print("\n美股分析:")
    print(us_analysis)

    # 保存为Excel文件
    save_to_excel(a_indices, a_analysis, hk_indices, hk_analysis, us_indices, us_analysis)


if __name__ == "__main__":
    main()



