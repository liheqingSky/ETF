import akshare as ak

# 获取申万一级行业列表（含代码）
# sw_industry = ak.sw_index_spot()
# print(sw_industry[['指数代码', '指数名称']].head())
#
# # 获取证监会行业分类
# csrc_industry = ak.stock_industry_category_cninfo()
# print(csrc_industry.groupby('行业分类名称')['股票代码'].count())

# valid_codes = ak.stock_zh_index_spot_em("深证系列指数").index.tolist()
# print("sz930707" in valid_codes)  # 输出 False

# df = ak.stock_industry_spot(symbol="农林牧渔")
# print(df.head())

# df = ak.stock_board_industry_spot_em("农林牧渔")
# print(df)
# industry_code = "801010"  # 农林牧渔（畜牧养殖所属行业）
# df[["行业名称", "行业代码", "最新价", "涨跌幅"]].query("行业代码 == @industry_code")