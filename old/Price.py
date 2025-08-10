from Logger import log
from loadExecl import Trade


class StockBuy():
    def __init__(self, code, filename=r'C:\Users\hi\Documents\merge.xlsx'):
        self._trade = Trade(filename)
        self._respect_price = 0
        self._code = code
        self._stock_info = self._trade.get_stock_info(code)

    def set_respect_price(self, respect_price):
        self._respect_price = respect_price

    # ETF份额最小单位100
    def calculate_etf_shares(self, investment_amount, price, transaction_cost=0):
        shares = int((investment_amount - transaction_cost) / price / 100) * 100
        log.debug("share:{:.3f}".format(shares))
        return shares

    # ETF价格精确到小数点后三位
    def calculate_etf_price(self, price, rate):
        next_price = round(price * (1 + rate), 3)
        log.debug("next_price:{}".format(next_price))
        return next_price

    def calculate_average_price(self, old_quantity, old_average_price, additional_quantity, additional_price):
        average_price = (old_quantity * old_average_price + additional_quantity * additional_price) / (
                old_quantity + additional_quantity)
        return average_price

    # 金字塔加仓, 首次加仓价格，下次加仓下跌幅度，初始金额，加仓比例，操作次数
    def pyramid(self, price, rate, initial_investment, increment_rate, levels):
        current_price = price
        current_investment = initial_investment
        total_investment = 0
        total_num = 0
        remain_investment = 0
        for i in range(1, levels + 1):
            if i > 1:
                current_price = self.calculate_etf_price(current_price, rate)
                current_investment = current_investment * (1 + increment_rate)

            current_num = self.calculate_etf_shares(current_investment, current_price)
            current_investment = current_num * current_price  # 修正边界值
            total_investment += current_investment
            total_num += current_num
            remain_investment = current_investment + remain_investment * (1 + rate)
            investment_rate = remain_investment / total_investment
            log.info(
                "Level {}: price:{:.3f} money:({:.3f}, {:.3f} {:.3f}) rate:{:.3%} shares:({:.3f}, {:.3f})".format(i,
                                                                                                                  current_price,
                                                                                                                  current_investment,
                                                                                                                  total_investment,
                                                                                                                  remain_investment,
                                                                                                                  investment_rate,
                                                                                                                  current_num,
                                                                                                                  total_num))

    def pyramid_up(self, price, rate, initial_investment, increment_rate, levels):
        self.pyramid(price, rate, initial_investment, increment_rate, levels)

    # 致敬时控制亏损幅度在指定范围时，需要的钱
    def get_respect_money(self, respect_price, respect_rate):
        total_num = self._stock_info['证券数量']
        total_money = total_num * self._stock_info['摊簿成本价']
        remain_money = total_num * respect_price
        log.debug(
            "total_num:{:.3f} total_money: {:.3f} remain_money: {:.3f} ".format(total_num, total_money, remain_money))

        need_money = (remain_money - total_money - total_money * respect_rate) / respect_rate
        log.info("respect {:.3%} need_moeny:{:.3f}".format(respect_rate, need_money))

        act_buy_num = self.calculate_etf_shares(need_money, respect_price)
        act_buy_money = act_buy_num * respect_price

        act_rate = (remain_money + act_buy_money) / (total_money + act_buy_money)
        log.info(
            "act buy respect {:.3%} act_buy_num:{:.3f} need_moeny:{:.3f} rate:{:.3%}".format(respect_rate, act_buy_num,
                                                                                             act_buy_money, act_rate))
        return


if __name__ == '__main__':
    instance = StockBuy('512170')
    instance.get_respect_money(0.40, -0.15)
