from datetime import datetime, timedelta

import akshare as ak
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter


# 常见A股宽基指数和行业指数列表及其中文简称
index_map = {
    'sh000001': '上证综指',
    'sz399001': '深证成指',
    'sz399006': '创业板指',
    'sz399005': '中小板指',
    'sh000688': '科创板50',
    'sh000993': '信息技术',
    'sz399986':'金融（银行）',
    'sz399998':'能源（煤炭）',
    'sh000858':'科技（人工智能）',
    'sh000990':'消费（家电）',
    'sz399994': '新能源车',
    'sh000932': '中证主要消费指数',  # 必选消费：以食品饮料为主（含白酒40%以上），乳品、调味品等，周期性弱。
    'sz399997': '中证白酒指数',  # 必选消费：聚焦白酒行业，成分股如贵州茅台、五粮液等，波动性较强。
    'sz399989': '中证医疗指数',  # 医疗保健：覆盖医疗器械（53%）、医疗服务（40%）等细分领域，成分股包括药明康德、迈瑞医疗、爱尔眼科等龙头，行业集中度高[2,7,9](@ref)。
    'sz930707': '中证畜牧养殖指数',
    # 农林牧渔：聚焦畜禽饲料、养殖及动物保健，前十大权重股含海大集团（11.3%）、牧原股份（10.07%）、温氏股份（10.12%），反映养殖产业链整体表现[11,12](@ref)。
    'sz931151': '光伏产业指数',
    # 电力设备：覆盖硅料、硅片、组件全产业链，权重股包括隆基绿能（16.15%）、通威股份（11.23%）、晶科能源（5.51%），反映光伏产业技术升级趋势[14,16](@ref)。
    'sh000991': '中证全指医药卫生指数', # 医药卫生：全市场医药股覆盖，包含化学制药（恒瑞医药10.95%）、医疗器械（迈瑞医疗5.58%）、生物制品（药明康德8.58%）等细分领域[6,19](@ref)。
    'sz930653': '中证食品饮料指数',  # 必选消费：覆盖食品饮料行业，与中证消费高度重合。
    'sh000989': '中证全指可选消费指数',  # 可选消费：家电、汽车为核心，周期性较强，受经济政策影响大。
    'sh000995': '中证耐用消费品指数',  # 可选消费：覆盖白色家电、小家电等耐用消费品。
    'sh000961': '中证消费80指数',  # 大消费综合：涵盖食品饮料、家电、汽车、医药等，行业分布均衡。
    'sz931148': '中证家电龙头指数',  # 其他细分：聚焦家电龙头企业。
    'sz930633': '中证旅游主题指数',  # 旅游类：覆盖旅游住宿、景点运营、旅游零售等，如中国中免、上海机场。
    'sz931833': '中证沪深港旅游休闲指数',  # 旅游类：跨市场指数，包含百胜中国、海底捞等旅游休闲企业。
    'sz930707': '中证畜牧指数',  # 畜牧养殖类：覆盖畜禽养殖、饲料加工、疫苗兽药等，如牧原股份、温氏股份。
    'sz931146': '中证新能源车指数',  # 其他细分：覆盖新能源汽车产业链。
    'sh000980': '中证传媒指数',  # 其他细分：涵盖传媒、广告、影视等行业。
    # 医药类
    'sz399982': '国证医药指数',      # 医药类：聚焦深市医药企业，成分股如片仔癀、云南白药，行业集中度高。
    'sz931143': '中证细分医药主题指数',  # 医药类：专注医药细分领域（如创新药、仿制药），成分股如复星医药、智飞生物。
    'sz399981': '中证创新医疗指数',  # 医疗类：聚焦创新医疗服务（如基因检测、精准医疗），成分股如华大基因、安图生物。
    'sh000945': '中证医疗保健指数',  # 医疗类：涵盖医疗设备、医疗服务、健康管理等，成分股如乐普医疗、爱尔眼科。
    'sz399983': '国证生物医药指数',  # 医药类：覆盖生物医药全产业链，成分股如药明康德、泰格医药。
}


def get_index_data(index_code):
    end_date = datetime.now().date()
    start_date = (datetime.now() - timedelta(days=10 * 365)).date()  # 大约10年前

    try:
        df = ak.stock_zh_index_daily(symbol=index_code)
        if df.empty:
            print(f"Error fetching data for {index_code} by stock_zh_index_daily")
        df['date'] = pd.to_datetime(df['date']).dt.date  # 将'date'列转换为日期类型
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        return df
    except Exception as e:
        print(f"Error fetching data for {index_code}: {e}")
        return pd.DataFrame()


def analyze_index(df, index_code, plot=False):
    """
    分析指数的历史数据，包括最高点前后的最低点及可视化支持。

    参数:
        df (DataFrame): 包含 'date' 和 'close' 列的指数历史数据
        index_code (str): 指数代码（如 'sh000991'）
        plot (bool): 是否绘制趋势图，默认 False

    返回:
        dict: 包含分析结果的字典
    """
    if df.empty:
        return None

    # 数据预处理
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # 获取全局最高点
    max_value = df['close'].max()
    max_rows = df[df['close'] == max_value]
    max_date = max_rows.iloc[0]['date']  # 若多个最高点，取第一个

    # 分割数据：最高点前、最高点后
    df_before_max = df[df['date'] < max_date]
    df_after_max = df[df['date'] > max_date]

    # 获取最低点前（最高点前的最低点）
    min_before_value = df_before_max['close'].min() if not df_before_max.empty else None
    min_before_date = df_before_max[df_before_max['close'] == min_before_value]['date'].iloc[
        0] if min_before_value is not None else None

    # 获取最低点后（最高点后的最低点）
    min_after_value = df_after_max['close'].min() if not df_after_max.empty else None
    min_after_date = df_after_max[df_after_max['close'] == min_after_value]['date'].iloc[
        0] if min_after_value is not None else None

    # 当前点位
    current_value = df['close'].iloc[-1]
    current_date = df['date'].iloc[-1]

    # 计算涨跌幅
    if min_before_value is not None and max_value is not None:
        rise_before_drop = ((max_value - min_before_value) / min_before_value) * 100
    else:
        rise_before_drop = None

    if max_value is not None and min_after_value is not None:
        drop_after_peak = ((max_value - min_after_value) / max_value) * 100
    else:
        drop_after_peak = None

    if min_after_value is not None and current_value is not None:
        rebound_after_min = ((current_value - min_after_value) / min_after_value) * 100
    else:
        rebound_after_min = None

    if max_value is not None and current_value is not None:
        gap_to_peak = ((max_value - current_value) / current_value) * 100
    else:
        gap_to_peak = None

    # 计算时间跨度
    def calc_time_span(start_date, end_date):
        if start_date is None or end_date is None:
            return None
        delta = (end_date - start_date).days
        years = delta // 365
        months = (delta % 365) // 30
        return f"{years}年{months}个月"

    time_before = calc_time_span(min_before_date, max_date) if min_before_date else None
    time_after = calc_time_span(max_date, min_after_date) if min_after_date else None
    time_since_min = calc_time_span(min_after_date, current_date) if min_after_date else None

    # 可视化支持
    if plot:
        plt.figure(figsize=(12, 6))
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.plot(df['date'], df['close'], label='指数趋势', color='gray')

        # 标注关键点
        if max_date:
            plt.scatter(max_date, max_value, color='red', label='最高点')
            plt.text(max_date, max_value * 1.02, '最高点', color='red', fontsize=9, ha='center')
        if min_before_date:
            plt.scatter(min_before_date, min_before_value, color='green', label='最高点前最低')
            plt.text(min_before_date, min_before_value * 0.98, '前最低', color='green', fontsize=9, ha='center')
        if min_after_date:
            plt.scatter(min_after_date, min_after_value, color='blue', label='最高点后最低')
            plt.text(min_after_date, min_after_value * 0.98, '后最低', color='blue', fontsize=9, ha='center')
        if current_date:
            plt.scatter(current_date, current_value, color='orange', label='当前点位')
            plt.text(current_date, current_value * 1.02, '当前', color='orange', fontsize=9, ha='center')

        if drop_after_peak:
            plt.scatter(current_date, drop_after_peak, color='orange', label='极限跌幅')
            plt.text(current_date, current_value * 1.02, '当前', color='orange', fontsize=9, ha='center')

        plt.title(f"{index_map.get(index_code, index_code)} 趋势分析")
        plt.xlabel("日期")
        plt.ylabel("收盘价")
        plt.legend()
        plt.grid(True)
        plt.gcf().autofmt_xdate()  # 自动旋转日期标签

        plt.savefig(
            fname=f"{index_map[index_code]}趋势分析.jpg",  # 必须参数
            dpi=300,
            bbox_inches="tight"
        )
        # plt.show()

    # 返回结果
    result = {
        '代号': index_code,
        '名称': index_map.get(index_code, '未知指数'),
        '最高点': round(max_value, 2) if max_value is not None else None,
        '最高点日期': max_date.strftime('%Y-%m-%d') if max_date else None,
        '最高点前最低点': round(min_before_value, 2) if min_before_value is not None else None,
        '最高点前最低点日期': min_before_date.strftime('%Y-%m-%d') if min_before_date else None,
        '最高点前涨跌幅': round(rise_before_drop, 2) if rise_before_drop is not None else None,
        '最高点前涨跌时间': time_before,
        '最高点后最低点': round(min_after_value, 2) if min_after_value is not None else None,
        '最高点后最低点日期': min_after_date.strftime('%Y-%m-%d') if min_after_date else None,
        '最高点后跌幅': round(drop_after_peak, 2) if drop_after_peak is not None else None,
        '最高点后下跌时间': time_after,
        '当前点位': round(current_value, 2) if current_value is not None else None,
        '当前点位日期': current_date.strftime('%Y-%m-%d') if current_date else None,
        '当前涨幅': round(rebound_after_min, 2) if rebound_after_min is not None else None,
        '当前上涨时间': time_since_min,
        '当前到最高点涨幅缺口': round(gap_to_peak, 2) if gap_to_peak is not None else None
    }

    return result

if __name__ == "__main__":
    results = []
    for index in index_map.keys():
        data = get_index_data(index)
        analysis = analyze_index(data, index, True)
        if analysis:
            results.append(analysis)

    # 创建DataFrame
    df_results = pd.DataFrame(results)

    # 打印表格
    # print(df_results[['名称', '最高点', '最高点日期', '最低点', '最低点日期',
    #                   '从最高点跌到最低点时间', '极限跌幅', '当前涨幅', '极限恢复涨幅']])
    #
    #

    # 保存为Excel文件，文件名包含今天的日期
    today = datetime.now().strftime('%Y%m%d')
    excel_filename = f"index_analysis_{today}.xlsx"
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        df_results.to_excel(writer, sheet_name='Index Analysis', index=False)
        worksheet = writer.sheets['Index Analysis']
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2

    print(f"\nResults saved to {excel_filename}")
