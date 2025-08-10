import akshare as ak

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


from tools import data_format
from Logger import log

class zhishu():
    def __init__(self):
        pass

    def save(self, data, name):
        data.to_csv(name+".csv", encoding='utf-8-sig')

    # 单次返回所有指数的实时行情数据
    def gupiao_all_zhishu(self):
        data = ak.stock_zh_index_spot()
        self.save(data, 'stock_zh_index_spot_df')
        return data

    # 单次返回指定指数的所有历史行情数据
    def gupiao_zhishu(self, symbol):
        data = ak.stock_zh_index_daily(symbol)
        self.save(data, 'stock_zh_index_daily')
        return data

    def etf(self):
        etf = ak.fund_etf_category_sina(symbol="ETF基金")
        etf.to_csv("sina_etf_list.csv", encoding='utf-8-sig')

    def cni(self):
        index_all_cni_df = ak.index_all_cni()
        index_all_cni_df.to_csv("all_cni_list.csv", encoding='utf-8-sig')

class Draw():
    def __init__(self):
        self.stock_zh_index_spot_df = ak.stock_zh_index_spot()
        self.stock_zh_index_spot_df.to_csv("A股指数大全.csv", encoding='utf-8-sig')

        self.stock_hk_index_daily_df = ak.stock_hk_index_spot_em()
        self.stock_hk_index_daily_df.to_csv("港股指数大全.csv", encoding='utf-8-sig')

        self.end_key = ''

    def get_zh_name(self, symbol):
        index = 0
        for _symbol in self.stock_zh_index_spot_df['代码']:
            if symbol == _symbol:
                break
            index+=1
        name = self.stock_zh_index_spot_df['名称'][index]
        log.debug('symbol: {} ---> name:{}'.format(symbol, name))
        return name

    def get_hk_name(self, symbol):
        index = 0
        for _symbol in self.stock_hk_index_daily_df['代码']:
            if symbol == _symbol:
                break
            index+=1
        name = self.stock_hk_index_daily_df['名称'][index]
        log.debug('symbol: {} ---> name:{}'.format(symbol, name))
        return name

    def get_zh_symbol(self, name):
        index = 0
        for _name in self.stock_zh_index_spot_df['名称']:
            if name == _name:
                break
            index+=1
        symbol = self.stock_zh_index_spot_df['代码'][index]
        log.debug('name: {} ---> symbol:{}'.format(name, symbol))
        return symbol

    def get_hk_symbol(self, name):
        index = 0
        for _name in self.stock_hk_index_daily_df['名称']:
            if name == _name:
                break
            index+=1
        symbol = self.stock_hk_index_daily_df['代码'][index]
        log.debug('name: {} ---> symbol:{}'.format(name, symbol))
        return symbol

    def draw(self, name, type=""):
        symbol = ""
        if type == "hk":
            symbol = str(self.get_hk_symbol(name))
            data = ak.stock_hk_index_daily_em(symbol)
            log.debug(data)
            self.end_key = 'latest'
        else:
            symbol = str(self.get_zh_symbol(name))
            data = ak.stock_zh_index_daily(symbol)
            self.end_key = 'close'


        fig = px.line(data, x="date", y=self.end_key, title=name)
        fig.add_trace(go.Scatter(x=[data['date'].iloc[-1]],
                                 y=[data[self.end_key].iloc[-1]],
                                 text=[data['date'].iloc[-1]],
                                 mode='markers+text',
                                 marker=dict(color='red', size=10),
                                 textfont=dict(color='green', size=10),
                                 textposition='top left',
                                 showlegend=False))
        fig.add_trace(go.Scatter(x=[data['date'].iloc[-1]],
                                 y=[data[self.end_key].iloc[-1]],
                                 text=[data[self.end_key].iloc[-1]],
                                 mode='markers+text',
                                 marker=dict(color='red', size=10),
                                 textfont=dict(color='green', size=10),
                                 textposition='bottom center',
                                 showlegend=False))

        max_value, max_date, min_value, min_date, cur_value, cur_date, loss_rate, cur_rise_rate, cur_loss_rate = self.get_loss_rate(data)
        return
        # text = "最高点: {} 日期：{}".format(max_value, max_date)
        # fig.add_annotation(text=text, showarrow=False)
        fig.show()
        # fig.write_image(name+".jpg")
        pio.write_image(fig, name+".jpg", scale=5, width=800, height=800)

    def get_date_list(self, date):
        year, month, day = str(date).split('-')
        return (year, month, day)

    def get_loss_rate(self, data):
        max_value = data['high'].max()
        max_row_index = data['high'].idxmax()
        max_date = data['date'][max_row_index]

        # 从最近一次熊市2018来统计
        year, month, day = str(max_date).split('-')
        index = 0
        if int(year) < 2018:
            new_high_data = data['date'][max_row_index:]
            for line in new_high_data:
                if self.get_date_list(line)[0] >= '2018':
                    break
                index+=1

            new_index = max_row_index + index
            max_value = data['high'][new_index:].max()
            max_row_index = data['high'][new_index:].idxmax()
            max_date = data['date'][new_index:][max_row_index]

        min_values_list = data['low'][max_row_index:]
        min_value = min_values_list.min()
        min_row_index = min_values_list.idxmin()
        min_date = data['date'][max_row_index:][min_row_index]

        cur_value = data[self.end_key].iloc[-1]
        cur_date = data['date'].iloc[-1]
        log.debug("max: {} date:{} min: {} date:{} cur:{} date:{}".format(max_value, max_date, min_value, min_date, cur_value, cur_date))

        loss_rate = data_format((min_value - max_value) / max_value * 100)
        cur_loss_rate = data_format((cur_value - max_value) / max_value * 100)
        cur_rise_rate = data_format((cur_value - min_value) / min_value * 100)
        log.debug("从最高点已下跌比例: {}% 从最低点已反弹比例：{}% 当前距离最高点下跌比例：{}%".format(loss_rate, cur_rise_rate, cur_loss_rate))

        return (max_value, max_date, min_value, min_date, cur_value, cur_date, loss_rate, cur_rise_rate, cur_loss_rate)


if __name__ == '__main__':
    instance = Draw()

    list = ['中证医疗', '中证医药', '国证军工', '红利指数', '全指价值', '全指成长', '中证500', '中证消费', '中证信息', '中证金融']
    for _list in list:
        instance.draw(_list, "")

    hk_list = ['恒生指数', '恒生科技指数', '恒生医疗保健指数']
    for _list in hk_list:
        instance.draw(_list, "hk")