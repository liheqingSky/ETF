import datetime

import matplotlib.pyplot as plt

from Logger import log
from loadExecl import Trade
from tools import data_format


# 自动标记切片: 将函数或格式字符串传递给 autopct 以标记切片。
# radius 半径，最外围的圆半径越大，如果半径小于内部的圆，该圆圈将无法展示
# 色片:将颜色列表传递给颜色以设置每个切片的颜色。 colors=['olivedrab', 'rosybrown', 'gray', 'saddlebrown']
# 交换标签和自动文本位置: 使用标签距离和 pct距离参数分别定位标签和自动 autopct 文本
# 标签距离和 pct距离是半径的比率;因此他们在饼图中心和饼图边缘之间变化饼图，并且可以设置为大于将文本放在饼图外部
# explode：数组，表示各个扇形之间的间隔，默认值为0。
# labels：列表，各个扇形的标签，默认值为 None。
# colors：数组，表示各个扇形的颜色，默认值为 None。
# autopct：设置饼图内各个扇形百分比显示格式，%d%% 整数百分比，%0.1f 一位小数， %0.1f%% 一位小数百分比， %0.2f%% 两位小数百分比。
# pctdistance：类似于 labeldistance，指定 autopct 的位置刻度，默认值为 0.6。
# labeldistance：标签标记的绘制位置，相对于半径的比例，默认值为 1.1，如 <1则绘制在饼图内侧。


class Summary():
    def __init__(self, filename):
        account_dict, stocks_info = Trade(filename).get_stocks_info()
        self._account_dict = account_dict
        self._stocks_info = stocks_info

    def get_inner_info(self, stocks_info, account_info):
        inner_dict = {'A股': [],
                      '海外新兴': ['中概互联', '恒生', '香港', '教育'],
                      '海外成熟': ['标普500ETF', '纳指ETF'],
                      '货币': [],
                      '债券': ['债']}

        inner_dict_info = {'A股': 0, '海外新兴': 0, '海外成熟': 0, '货币': 0, '债券': 0}
        for stock_info in stocks_info:
            match_flag = False
            for key, values in inner_dict.items():
                for value in values:
                    if value in stock_info['证券名称']:
                        log.debug("key:{} values:{} stock_info:{} inner:{}".format(key, values, stock_info, inner_dict_info))
                        inner_dict_info[key] += data_format(stock_info['最新市值'])
                        log.debug("key:{} code:{}".format(key, stock_info['证券名称']))
                        match_flag = True
                        break
                if match_flag == True:
                    break

            key = 'A股'
            if match_flag == False:
                log.debug("key:{} code:{}".format(key, stock_info['证券名称']))
                inner_dict_info['A股'] += data_format(stock_info['最新市值'])

        inner_dict_info['货币'] += data_format(account_info['可用'])
        return (list(inner_dict_info.keys()), list(inner_dict_info.values()))

    def get_dict_info(self, dicts, stocks_info, account_info):
        current_dict_info = {}
        for key in dicts.keys():
            current_dict_info[key] = 0.0

        for stock_info in stocks_info:
            match_flag = False
            for key, values in dicts.items():
                # log.debug("key:{} values:{} stock:{}".format(key, values, stock_info))
                for value in values:
                    if value in stock_info['证券名称']:
                        if stock_info['证券名称'] == '恒生医疗ETF' and key == '行业':
                            break
                        if stock_info['证券名称'] == '香港证券ETF' and key == '行业':
                            break

                        current_dict_info[key] += data_format(stock_info['最新市值'])
                        match_flag = True
                        log.debug("key:{} stock:{}".format(key, stock_info))
                        break
                if match_flag == True:
                    break

            if match_flag == True:
                continue

            code = str(stock_info['证券代码'])

            if code[0:3] in ['600', '601', '602', '002']:
                log.error('gupiao {} '.format(stock_info))
                current_dict_info['股票'] += data_format(stock_info['最新市值'])
                continue
            elif len(code) < 6:
                log.error('gupiao {} '.format(stock_info))
                current_dict_info['股票'] += data_format(stock_info['最新市值'])
                continue

            key = '其它'
            log.debug("key:{} code:{} {}".format(key, stock_info['证券名称'], code))
            current_dict_info[key] += data_format(stock_info['最新市值'])

        current_dict_info['货币'] += data_format(account_info['可用'])
        return (list(current_dict_info.keys()), list(current_dict_info.values()))

    def get_middle_info(self, stocks_info, account_info):
        middle_dict = {
            '行业': ['医药', '医疗', '养老', '国防', '芯片', '证券', '券商', '传媒', '光伏', '基建', '旅游', '养殖',
                     '信息'],
            '价值': ['红利'],
            '中小盘': ['创业板', '双创', '科创板', '中证500'],
            '大盘': ['沪深300', '上证50'],
            '股票': [],
            '香港': ['恒生ETF', '香港证券ETF'],
            '海外科技': ['中概互联', '恒生科技', '香港', '教育'],
            '海外医疗': ['恒生医疗'],
            '美国': ['标普500ETF', '纳指ETF'],
            '货币': [],
            '债卷': ['债'],
            '其它': []}
        return self.get_dict_info(middle_dict, stocks_info, account_info)

    def get_outter_info(self, stocks_info, account_info):
        outter_dict = {
            "传媒ETF": 0,
            "证券ETF": 0,
            "芯片ETF": 0,
            "国防ETF": 0,
            "医疗ETF": 0,
            "医药ETF": 0,
            "医药卫生ETF": 0,
            "养老ETF": 0,
            "基建ETF": 0,
            "光伏ETF": 0,
            "养殖ETF": 0,
            "旅游ETF": 0,
            "中证500ETF": 0,
            "信息技术ETF": 0,
            "科创板ETF": 0,
            "创业板ETF广发": 0,
            "双创ETF": 0,
            "沪深300ETF": 0,
            "立讯精密": 0,
            "海康威视": 0,
            "中远海控": 0,
            "大华股份": 0,
            "未名医药": 0,
            "恒生ETF": 0,
            "香港证券ETF": 0,
            "恒生科技指数ETF": 0,
            "中概互联网ETF": 0,
            "中概互联ETF": 0,
            "教育ETF": 0,
            "恒生医疗ETF": 0,
            "标普500ETF": 0,
            "纳指ETF": 0,
            "其它": 0,
        }
        for stock_info in stocks_info:
            if stock_info['证券名称'] == '医疗基金LOF':
                outter_dict['医疗ETF'] += data_format(stock_info['最新市值'])
            elif stock_info['证券名称'] == '券商ETF':
                outter_dict['证券ETF'] += data_format(stock_info['最新市值'])
            else:
                if stock_info['证券名称'] in outter_dict.keys():
                    outter_dict[stock_info['证券名称']] += data_format(stock_info['最新市值'])
                else:
                    outter_dict['其它'] += data_format(stock_info['最新市值'])

        outter_dict['货币'] = data_format(account_info['可用'])

        return (list(outter_dict.keys()), list(outter_dict.values()))

    def classity(self):
        labels = []
        sizes = []

        inner_label, inner_sizes = self.get_inner_info(self._stocks_info, self._account_dict)
        log.debug(inner_label)
        log.debug(inner_sizes)

        middle_label, middle_sizes = self.get_middle_info(self._stocks_info, self._account_dict)
        log.debug(middle_label)
        log.debug(middle_sizes)

        outter_label, outter_sizes = self.get_outter_info(self._stocks_info, self._account_dict)
        log.debug(outter_label)
        log.debug(outter_sizes)

        labels.append(inner_label)
        labels.append(middle_label)
        labels.append(outter_label)

        sizes.append(inner_sizes)
        sizes.append(middle_sizes)
        sizes.append(outter_sizes)
        return (labels, sizes)

    # 嵌套圆圈必须先从外围圆圈画起，在中圈，在内圈，否则会异常
    def pix(self):
        labels, sizes = self.classity()

        # 解决中文乱码问题
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        fig, ax = plt.subplots()

        pct_distance_list = [0.5, 0.7, 0.9]
        label_distance_list = [0.25, 0.6, 0.75]
        # radius_list = [0.5, 1.0, 1.5]
        radius_list = [0.4, 0.9, 1.6]
        for index in list(range(len(labels) - 1, -1, -1)):
            log.debug(index)

            radius = radius_list[index]
            size = sizes[index]
            label = labels[index]
            explode = [0.01] * len(size)
            autopct = '%1.1%%'
            pctdistance = pct_distance_list[index]
            labeldistance = label_distance_list[index]
            # colors = ['lightskyblue'] * len(size)
            wedgeprops = dict(edgecolor='white', linewidth=0.2, alpha=0.5)
            ax.pie(size, explode=explode, labels=label, autopct='%1.1f%%', pctdistance=pctdistance,
                   labeldistance=labeldistance, radius=radius,
                   wedgeprops=wedgeprops)

        ax.set_title("持仓分布汇总", fontsize=14, loc="right", color='red')
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        plt.text(1.5, 1.5, today, fontsize=14, color='red')
        plt.show()


if __name__ == '__main__':
    instance = Summary(r'.\merge.xlsx')
    instance.pix()
