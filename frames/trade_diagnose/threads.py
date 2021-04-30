# _*_ coding:utf-8 _*_
# @File  : threads.py
# @Time  : 2021-03-26 10:13
# @Author: zizle

import os
import random
import time
import string
import datetime
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal
from settings import logger
from utils.constant import CH_VARIETY
from utils.characters import split_number_en

pd.set_option('display.max_columns', 50)  # 设置显示50列
pd.set_option('display.max_rows', 100)   # 设置显示100行


# 处理原始数据
class HandleSourceThread(QThread):
    handle_finished = pyqtSignal(dict)

    error_break = pyqtSignal(str)

    def __init__(self, bill_type, files, *args, **kwargs):
        # bill_type为1,2,3,4分别是日逐日盯市、日逐笔对冲、月逐日盯市、月逐笔对冲
        # hands_t是每个品种的一手对应吨数
        super(HandleSourceThread, self).__init__(*args, **kwargs)
        self.bill_type = bill_type
        self.files = files
        self.hands_t = {
            'A': 10, 'C': 10, 'TA': 5, 'MA': 10
        }  # TODO 此数据的做网络请求得到

    def generate_date(self):
        date = []
        s = datetime.datetime.strptime('2020.09.30', '%Y.%m.%d')
        e = datetime.datetime.strptime('2021.03.20', '%Y.%m.%d')
        while s < e:
            date.append(s.strftime('%Y-%m-%d'))
            s += datetime.timedelta(days=1)

        return date

    def read_account(self, account_df):  # 读取账户资金情况
        # 资金账户字典
        account_dict = {
            'exchange_date': None,  # 交易日期
            'pre_rights': None,  # 上日结存
            'rights': None,  # 客户权益
            'sum_in_out': None,  # 当日存取合计
            'profit': None,  # 当日盈亏
            'charge': None,  # 当日手续费
            'leave': None,  # 当日结存
            'bail': None,  # 保证金占用
            'enabled_money': None,  # 可用资金
            'risk': None,  # 风险度
        }
        row_count, col_count = account_df.shape
        finish = False
        for row in range(row_count):
            for col in range(col_count):
                unit_text = str(account_df.iat[row, col]).strip()
                if unit_text == '交易日期':
                    exchange_date = str(account_df.iat[row, col + 2]).strip()
                    account_dict['exchange_date'] = exchange_date
                    break  # 下一行
                elif unit_text == '上日结存':
                    account_dict['pre_rights'] = str(account_df.iat[row, col + 2]).strip()
                elif unit_text == '客户权益':
                    account_dict['rights'] = str(account_df.iat[row, col + 2]).strip()
                elif unit_text == '当日存取合计':
                    account_dict['sum_in_out'] = str(account_df.iat[row, col + 2]).strip()
                elif unit_text == '当日盈亏':
                    account_dict['profit'] = str(account_df.iat[row, col + 2]).strip()
                elif unit_text == '当日手续费':
                    account_dict['charge'] = str(account_df.iat[row, col + 2]).strip()
                elif unit_text == '当日结存':
                    account_dict['leave'] = str(account_df.iat[row, col + 2]).strip()
                elif unit_text == '保证金占用':
                    account_dict['bail'] = str(account_df.iat[row, col + 2]).strip()
                elif unit_text == '可用资金':
                    account_dict['enabled_money'] = str(account_df.iat[row, col + 2]).strip()
                elif unit_text == '风险度':
                    account_dict['risk'] = str(account_df.iat[row, col + 2]).strip()
                elif unit_text == '追加保证金':
                    finish = True
            if finish:
                break
        return account_dict.copy()

    def read_exchange_detail(self, trade_df):
        ex_date = None  # 成交日期
        # trade_dict = {
        #     'contract': None,  # 合约
        #     'ex_number': None,  # 成交序号
        #     'sale_text': None,  # 买/卖
        #     'ex_price': None,  # 成交价
        #     'hands': None,  # 手数
        #     'ex_money': None,  # 成交额
        #     'open_text': None,  # 开/平
        #     'ex_profit': None  # 平仓盈亏
        # }
        row_count, col_count = trade_df.shape
        t_start_row, t_end_row = None, None
        enter_col = True
        for row in range(row_count):
            for col in range(col_count):
                unit_text = str(trade_df.iat[row, col]).strip()
                if unit_text == '合计':
                    t_end_row = row  # 不-1,因为截取时不包含
                if not enter_col:
                    break  # 下一行
                if unit_text == '交易日期':
                    ex_date = str(trade_df.iat[row, col + 2]).strip()
                    break  # 下一行
                elif unit_text == '成交明细':
                    # 得到成交明细表的起始行
                    t_start_row = row + 2
                    enter_col = False

        trade_df = trade_df[t_start_row:t_end_row]
        # [合约,成交序号,成交时间,买/卖,投机/套保,成交价,手数,成交额,开/平,手续费,平层盈亏,实际成交日期]
        trade_df.columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        # 截取需要的数据
        trade_df = trade_df[['A', 'B', 'D', 'F', 'G', 'H', 'I', 'K']]
        trade_df.columns = ['contract', 'ex_number', 'sale_text', 'ex_price', 'hands', 'ex_money', 'open_text',
                            'ex_profit']
        # 加入日期列
        trade_df['ex_date'] = [ex_date for _ in range(trade_df.shape[0])]
        return trade_df.to_dict(orient='records')

    def read_close_detail(self, close_df):  # 读取平仓明细表
        # df = pd.DataFrame(trades)
        # df = df[df['open_text'].str.contains('平')]
        # # 改一下列名，不再修改后面的程序
        # # ['contract', 'ex_number', 'sale_text', 'ex_price', 'hands', 'ex_money', 'open_text', 'ex_profit', 'ex_date']
        # df.columns = ['contract', 'ex_number', 'sale_text', 'ex_price', 'hands', 'ex_money', 'open_text', 'close_profit', 'close_date']
        # return df.to_dict(orient='records')

        close_date = None  # 交易日期
        # close_dict = {
        #     'contract': None,  # 合约
        #     'ex_number': None,  # 成交序号
        #     'sale_text': None,  # 买/卖
        #     'ex_price': None,  # 成交价
        #     'open_price': None,  # 开仓价
        #     'hands': None,  # 手数
        #     'close_profit': None,  # 平仓盈亏
        #     'old_exnum': None # 原成交序号
        # }
        row_count, col_count = close_df.shape
        t_start_row, t_end_row = None, None
        enter_col = True
        for row in range(row_count):
            for col in range(col_count):
                unit_text = str(close_df.iat[row, col]).strip()
                if unit_text == '合计':
                    t_end_row = row  # 不-1,因为截取时不包含
                if not enter_col:
                    break  # 下一行
                if unit_text == '交易日期':
                    close_date = str(close_df.iat[row, col + 2]).strip()
                    break  # 下一行
                elif unit_text == '平仓明细':
                    # 得到成交明细表的起始行
                    t_start_row = row + 2
                    enter_col = False

        close_df = close_df[t_start_row:t_end_row]
        # [合约,成交序号,买/卖,成交价,开仓价,手数,昨结算价,平仓盈亏,原成交序号,实际成交日期]
        close_df.columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        # 截取需要的数据
        close_df = close_df[['A', 'B', 'C', 'D', 'E', 'F', 'H', 'I']]
        close_df.columns = ['contract', 'ex_number', 'sale_text', 'ex_price', 'open_price', 'hands', 'close_profit', 'old_exnum']
        # 加入日期列
        close_df['close_date'] = [close_date for _ in range(close_df.shape[0])]
        return close_df.to_dict(orient='records')

    @staticmethod
    def calculate_close_profit(is_long, open_p, close_p, close_h, ext):
        # open_p:开仓价,close_p平仓价,close_h:平仓手
        if is_long:  # 做多
            return round((float(close_p) - float(open_p)) * float(close_h) * ext, 2)
        else:
            return round((float(open_p) - float(close_p)) * float(close_h) * ext, 2)

    def handle_targer_data(self, account, exchange, close_position):
        # 参数 资金账户数据列表,成交数据列表,平仓数据列表
        # 处理出目标数据列表  资金账户表,成交明细表
        account_df = pd.DataFrame(account)
        exchange_df = pd.DataFrame(exchange)
        close_df = pd.DataFrame(close_position)
        print('资金明细表:---------------------------------')
        print(account_df)
        # account_df.to_excel('资金明细表.xlsx', encoding='utf_8_sig', index=False)
        print('成交明细表:-------------------------------------')
        print(exchange_df)
        # exchange_df.to_excel('成交明细表.xlsx', encoding='utf_8_sig', index=False)
        print('平仓明细表:--------------------------------------')
        print(close_df)
        # 以平仓明细表完善成交明细表，使用原成交号合并数据，以增加【平仓价，平仓日期】
        exchange_df['ex_series_num'] = exchange_df['ex_number'].apply(lambda x: int(x))
        close_df['ex_series_num'] = close_df['old_exnum'].apply(lambda x: int(x))
        close_df.rename(columns={'ex_price': 'close_price', 'hands': 'close_hands'}, inplace=True)
        # 合并
        exchange_df = pd.merge(exchange_df, close_df[['close_price', 'close_hands', 'close_date', 'ex_series_num']], on=['ex_series_num'], how='left')

        # 取成交明细表中的开仓记录
        exchange_df = exchange_df[exchange_df['open_text'].str.contains('开')]

        # 取成交明细表需要的列[合约,开仓日期,买/卖,开仓价,开仓手数,平仓日期,平仓价,平仓手数,成交金额,平仓盈亏]
        exchange_df = exchange_df[['contract', 'ex_date', 'sale_text', 'ex_price', 'hands', 'close_date', 'close_price', 'ex_money','close_hands']]
        exchange_df.rename(columns={'ex_date': 'open_date', 'ex_price': 'open_price', 'hands': 'open_hands'}, inplace=True)
        exchange_df['is_long'] = exchange_df['sale_text'].apply(lambda x: 1 if '买' in x else 0)
        exchange_df['variety_en'] = exchange_df['contract'].apply(lambda x: split_number_en(x)[0])
        exchange_df['variety_ext'] = exchange_df['variety_en'].apply(lambda x: self.hands_t.get(x, 0))
        # 计算每笔收益
        exchange_df['close_profit'] = exchange_df.apply(lambda x: self.calculate_close_profit(x['is_long'], x['open_price'], x['close_price'], x['close_hands'], x['variety_ext']), axis=1)

        print('合并后交易明细表（含成交明细数据）:=============================')
        print(exchange_df)
        print('交易详情清洗数据前行数:', exchange_df.shape[0])
        exchange_df.dropna(subset=['close_date'], inplace=True)
        print('交易详情清洗数据后行数:', exchange_df.shape[0])

        return account_df.to_dict(orient='records'), exchange_df.to_dict(orient='records')

    def run(self):
        if self.bill_type != 1:
            self.error_break.emit('暂不支持此账单类型分析!')
            return
        if len(self.files) < 1:
            self.error_break.emit('没有检测到账单文件!')
            return
        account = []  # 账户资金数据
        trade = []  # 成交明细
        close_position = []  # 平仓明细
        # 根据文件列表,做以下数据提取,一个文件就是一天的数据
        for filename in self.files:
            if filename.startswith('~$'):
                continue
            # 打开文件
            try:
                excel_file = pd.ExcelFile(filename)
            except Exception as e:
                logger.error(f'用户打开文件错误:{e}')
                self.error_break.emit(f'打开文件{filename}错误!')
                break
            # 1 读取账户资金情况
            account_df = excel_file.parse(sheet_name='客户交易结算日报')
            account_dict = self.read_account(account_df)
            account.append(account_dict)
            # 2 读取成交明细
            trade_df = excel_file.parse(sheet_name='成交明细')
            trade += self.read_exchange_detail(trade_df)
            # 3 读取平仓明细表
            close_df = excel_file.parse(sheet_name='平仓明细')
            close_position += self.read_close_detail(close_df)
            # close_position += self.read_close_detail(trade)

        # 处理表关系,传出数据
        account, exchange = self.handle_targer_data(account, trade, close_position)
        self.handle_finished.emit({
            'account': account,
            'trade_detail': exchange
        })


# 处理基本数据
class HandleBaseThread(QThread):
    handle_finished = pyqtSignal(dict)

    def __init__(self, account, trade_detail, *args, **kwargs):
        super(HandleBaseThread, self).__init__(*args, **kwargs)
        self.account_data = account
        self.trade_detail = trade_detail

    @staticmethod
    def float_column_number(df, keys):  # 将给定的df的keys列转为Float
        for key in keys:
            df[key] = df[key].apply(lambda x: float(x))
        return df

    def run(self):
        #  转为DataFrame
        # [  日期,        上日结存,   客户权益,存取合计,   当日盈亏,当日手续费,当日结存, 保证金占用,可用资金,      风险度]
        # [exchange_date,pre_rights,rights,sum_in_out,profit,charge,   leave,   bail,    enabled_money,risk]
        account_df = pd.DataFrame(self.account_data)  # 资金明细表
        # [合约contract   开仓日open_date  买/卖sale_text  开仓价open_price  开仓手数open_hands  平仓日close_date]
        # [平仓价close_price  平仓手数close_hands  多头?is_long  品种variety_en  品种1手吨数variety_ext  平仓收益close_profit]
        trade_detail = pd.DataFrame(self.trade_detail)  # 交易明细表
        # 排序
        account_df.sort_values(by=['exchange_date'], inplace=True)
        trade_detail.sort_values(by=['open_date'], inplace=True)
        # 重新设置index
        account_df.reset_index(inplace=True)
        trade_detail.reset_index(inplace=True)
        del account_df['index']
        del trade_detail['index']
        # 处理目标数据
        account_df = self.float_column_number(account_df, ['profit', 'charge', 'sum_in_out', 'pre_rights', 'rights', 'bail'])
        trade_detail = self.float_column_number(trade_detail, ['close_profit', 'close_hands', 'ex_money'])
        ksrq = account_df.at[0, 'exchange_date']  # 开始日期
        jsrq = account_df.at[account_df.shape[0] - 1, 'exchange_date']  # 结束日期
        # 计算区间总天数
        qjts = account_df.shape[0]  # 交易天数
        # 盈利天数(取资金表中当日盈亏大于0的)
        ylts = account_df[account_df['profit'] > 0].shape[0]  # 盈利天数
        ksts = account_df.shape[0] - ylts  # 亏损天数
        # 交易胜率 平仓利润为+ / 总笔数
        zhuanqian_bishu = trade_detail[trade_detail['close_profit'] > 0]['close_hands'].sum()
        jysl = zhuanqian_bishu / trade_detail['close_hands'].sum()
        # 累计净值
        # 计算当日净值=(当日权益 - 当日存取)/上日权益
        account_df['net_value'] = (account_df['rights'] - account_df['sum_in_out']) / account_df['pre_rights']
        # 当日累计净值=前日累计净值*当日净值
        account_df['daily_net_value'] = account_df['net_value'].cumprod()
        # 计算日收益率
        account_df['daily_profit_rate'] = account_df['net_value'] - 1
        # 交易费用
        jyfy = round(account_df["charge"].sum(), 2)
        # 平仓赚钱和
        p_zhuan = trade_detail[trade_detail['close_profit'] > 0]['close_profit'].sum()
        # 平仓亏钱和
        p_kui = trade_detail[trade_detail['close_profit'] < 0]['close_profit'].sum()
        # 累计净利润(平仓盈亏和 - 交易费用)
        ljjlr = round(p_zhuan + p_kui - jyfy, 2)
        # 计算最高回撤率=(最高累计净值-当日的累计净值)/最高累计净值，取最大者
        max_cumprod = account_df['daily_net_value'].max()
        account_df['retracement'] = (max_cumprod - account_df['daily_net_value']) / max_cumprod  # 计算每日的回撤率
        # 取最大回撤时点(回撤率最小时),回撤区间(回撤率最小-最大时的区间)
        max_huiche = account_df[account_df['retracement'] == account_df['retracement'].min()].copy()
        min_huiche = account_df[account_df['retracement'] == account_df['retracement'].max()].copy()
        max_huiche.reset_index(inplace=True)
        min_huiche.reset_index(inplace=True)
        max_huiche = max_huiche.at[0, 'exchange_date']
        min_huiche = min_huiche.at[0, 'exchange_date']
        # 仓位比例（保证金 / 权益）
        account_df['risk_rate'] = account_df['bail'] / account_df['rights']
        ### 交易品种统计
        # 盈利前五品种(品种分组盈利求和)、亏损前五品种(品种分组亏损求和)，交易手数排名前五(品种分组手数求和)，交易金额排名前五(品种分组金额求和)
        # 取盈利的数据
        p_yingli = trade_detail[trade_detail['close_profit'] > 0]
        p_kuisun = trade_detail[trade_detail['close_profit'] < 0]
        group_sum1 = p_yingli.groupby(by=['variety_en'], as_index=False)['close_profit'].agg({'sum_close_profit': 'sum'})
        group_sum2 = p_kuisun.groupby(by=['variety_en'], as_index=False)['close_profit'].agg({'sum_close_profit': 'sum'})
        # 排序取结果
        group_sum1.sort_values(by=['sum_close_profit'], ascending=False, inplace=True)  # 正数倒序
        group_sum2.sort_values(by=['sum_close_profit'], inplace=True)  # 负数升序
        group_sum1['variety_text'] = group_sum1['variety_en'].apply(lambda x: CH_VARIETY.get(x, x))
        group_sum2['variety_text'] = group_sum2['variety_en'].apply(lambda x: CH_VARIETY.get(x, x))
        ylqwpz = group_sum1.head(5)['variety_text'].to_list()  # 盈利前五品种
        ksqwpz = group_sum2.head(5)['variety_text'].to_list()
        # 交易手数排名
        group_sum = trade_detail.groupby(by=['variety_en'], as_index=False)['close_hands'].agg({'sum_hands': 'sum'})
        group_sum.sort_values(by=['sum_hands'], ascending=False, inplace=True)
        group_sum['variety_text'] = group_sum1['variety_en'].apply(lambda x: CH_VARIETY.get(x, x))
        shqwpz = group_sum.head(5)['variety_text'].to_list()
        # 交易金额排名
        group_sum = trade_detail.groupby(by=['variety_en'], as_index=False)['ex_money'].agg({'sum_ex_money': 'sum'})
        group_sum.sort_values(by=['sum_ex_money'], ascending=False, inplace=True)
        group_sum['variety_text'] = group_sum1['variety_en'].apply(lambda x: CH_VARIETY.get(x, x))
        jeqwpz = group_sum.head(5)['variety_text'].to_list()
        # 夏普比例 = (年化收益率 - 无风险利率(2%)) / 收益率标准差
        yjnhsyl = account_df["daily_profit_rate"].mean() * 250  # 预计年化收益率
        # print('日收益率标准方差:', account_df['daily_profit_rate'].std())
        xpbl = (yjnhsyl - 0.02) / account_df['daily_profit_rate'].std()
        # 卡玛比率 = (年化收益率 - 无风险利率(2%)) / 最大回撤率
        # print('最大回撤率：', account_df['retracement'].max())
        kmbl = (yjnhsyl - 0.02) / account_df['retracement'].max()


        base_data = dict()
        base_data['ksrq'] = ksrq  # 开始日期
        base_data['jsrq'] = jsrq  # 结束日期
        base_data['qcqy'] = account_df.at[0, 'rights']  # 期初权益
        base_data['qmqy'] = account_df.at[account_df.shape[0] - 1, 'rights']  # 期末权益
        base_data['qjts'] = qjts  # 区间天数
        base_data['ylts'] = ylts   # 盈利天数
        base_data['ksts'] = ksts  # 亏损天数
        base_data['jysl'] = f'{round(jysl * 100, 2)}%'  # 交易胜率
        base_data['ljjrj'] = f'{round(account_df["sum_in_out"].sum(), 2)}'  # 累计净入金
        base_data['ljjz'] = f'{round(account_df.at[account_df.shape[0] - 1, "daily_net_value"], 4)}'  # 累计净值
        base_data['jyfy'] = jyfy  # 交易费用
        base_data['ljjlr'] = ljjlr  # 累计净利润
        base_data['ykb'] = f'{round(-p_zhuan * 100 / p_kui, 2)}%'  # 盈亏比（平仓中收益>0和 / 平仓汇<0和）
        base_data['fjlrb'] = f'{round(jyfy * 100 / ljjlr, 2)}%'  # 费用、净利润比
        base_data['zdhcsd'] = max_huiche  # 最大回撤时点
        base_data['zdhcqj'] = f'{max_huiche} ~ {min_huiche}'  # 最大回撤区间
        base_data['zdrsyl'] = f'{round(account_df["daily_profit_rate"].max() * 100, 2)}%'  # 最大日收益率
        base_data['zxrsyl'] = f'{round(account_df["daily_profit_rate"].min() * 100, 2)}%'  # 最小日收益率
        base_data['pjrsyl'] = f'{round(account_df["daily_profit_rate"].mean() * 100, 2)}%'  # 平均日收益率
        base_data['yjnhsyl'] = f'{round( yjnhsyl * 100, 2)}%'  # 预计年化收益率
        base_data['zdcwbl'] = f'{round(account_df["risk_rate"].max() * 100, 2)}%'  # 最大仓位比率(风险度)
        base_data['zxcwbl'] = f'{round(account_df["risk_rate"].min() * 100, 2)}%'  # 最小仓位比率(风险度)
        base_data['pjcwbl'] = f'{round(account_df["risk_rate"].mean() * 100, 2)}%'  # 平均仓位比率(风险度)
        base_data['kcts'] = f'{account_df[account_df["bail"] == 0].shape[0]}'  # 空仓天数
        base_data['ylqwpz'] = ','.join(ylqwpz)  # 从所有平仓盈利的交易中取盈利和前五的品种
        base_data['ksqwpz'] = ','.join(ksqwpz)  # 从所有平仓亏损的交易中去亏损和前五的品种
        base_data['shqwpz'] = ','.join(shqwpz)  # 平仓手数排名
        base_data['jeqwpz'] = ','.join(jeqwpz)  # 平仓成交金额排名
        base_data['xpbl'] = f'{round(xpbl, 2)}'  # 夏普比率
        base_data['kmbl'] = f'{round(kmbl, 2)}'  # 卡玛比率
        self.handle_finished.emit(base_data)


# 处理交易分析 - 手数金额数据
class HandlePriceHandsThread(QThread):
    handle_finished = pyqtSignal(dict)

    def __init__(self, trade_detail, *args, **kwargs):
        super(HandlePriceHandsThread, self).__init__(*args, **kwargs)
        self.trade_detail = trade_detail

    def run(self):
        trade_df = pd.DataFrame(self.trade_detail)
        # 交易手数分布(分品种统计交易手数)
        group_sum = trade_df.groupby(by=['variety_en'], as_index=False)['close_hands'].agg({'sum_hands': 'sum'})
        group_sum['variety_text'] = group_sum['variety_en'].apply(lambda x: CH_VARIETY.get(x, x))
        jyshfb = group_sum.to_dict(orient='records')  # 交易手数分布
        # 交易金额分布
        group_sum = trade_df.groupby(by=['variety_en'], as_index=False)['ex_money'].agg({'sum_ex_money': 'sum'})
        group_sum['variety_text'] = group_sum['variety_en'].apply(lambda x: CH_VARIETY.get(x, x))
        jyjefb = group_sum.to_dict(orient='records')  # 交易金额分布
        data = {
            'jyshfb': jyshfb,
            'jyjefb': jyjefb
        }
        self.handle_finished.emit(data)


# 处理交易分析 - 日内隔夜交易分析
class HandlePassNightThread(QThread):
    handle_finished = pyqtSignal(dict)

    def __init__(self, trade_detail, *args, **kwargs):
        super(HandlePassNightThread, self).__init__(*args, **kwargs)
        self.trade_detail = trade_detail

    def run(self):
        trade_df = pd.DataFrame(self.trade_detail)
        trade_df['ex_money'] = trade_df['ex_money'].astype(float)
        # 日内隔夜交易分析
        # 取日内交易数据
        rinei_df = trade_df[trade_df['open_date'] == trade_df['close_date']]
        # 取隔夜交易数据
        geye_df = trade_df[trade_df['open_date'] != trade_df['close_date']]
        # 日内隔夜交易金额占比
        rngyjezb = {'rinei': round(rinei_df['ex_money'].sum(), 2), 'geye': round(geye_df['ex_money'].sum(), 2)}
        # 日内品种交易金额占比
        group_sum = rinei_df.groupby(by=['variety_en'], as_index=False)['ex_money'].agg({'sum_ex_money': 'sum'})
        group_sum['variety_text'] = group_sum['variety_en'].apply(lambda x: CH_VARIETY.get(x, x))
        rnpzjyzb = group_sum.to_dict(orient='records')  # 日内品种交易金额占比
        # 隔夜品种交易金额占比
        group_sum = geye_df.groupby(by=['variety_en'], as_index=False)['ex_money'].agg({'sum_ex_money': 'sum'})
        group_sum['variety_text'] = group_sum['variety_en'].apply(lambda x: CH_VARIETY.get(x, x))
        gepzjyzb = group_sum.to_dict(orient='records')  # 隔夜品种交易金额占比
        data = {
            'rngyjezb': rngyjezb,  # 日内隔夜金额占比
            'rnpzjyzb': rnpzjyzb,  # 日内品种交易占比,
            'gypzjyzb': gepzjyzb   # 隔夜品种交易占比
        }
        self.handle_finished.emit(data)


class HandleExChargeThread(QThread):
    handle_finished = pyqtSignal(dict)

    def __init__(self, account, *args, **kwargs):
        super(HandleExChargeThread, self).__init__(*args, **kwargs)
        self.account = account

    def run(self):
        account_df = pd.DataFrame(self.account)
        account_df['charge'] = account_df['charge'].astype(float)
        data = {
            'jyfy': account_df[['exchange_date', 'charge']].to_dict(orient='records')
        }
        self.handle_finished.emit(data)


class HandleNetValueThread(QThread):
    handle_finished = pyqtSignal(dict)

    def __init__(self, account, *args, **kwargs):
        super(HandleNetValueThread, self).__init__(*args, **kwargs)
        self.account = account

    def run(self):
        account_df = pd.DataFrame(self.account)
        for key in ['rights', 'sum_in_out', 'pre_rights', 'profit']:
            account_df[key] = account_df[key].astype(float)
        # 计算当日净值=(当日权益 - 当日存取)/上日权益
        account_df['net_value'] = (account_df['rights'] - account_df['sum_in_out']) / account_df['pre_rights']
        # 当日累计净值=前日累计净值*当日净值
        account_df['daily_net_value'] = account_df['net_value'].cumprod()
        data = {
            'jzsj': account_df[['exchange_date', 'daily_net_value', 'profit']].to_dict(orient='record')  # 净值数据
        }
        self.handle_finished.emit(data)


class HandleVarietyProfitThread(QThread):
    handle_finished = pyqtSignal(dict)

    def __init__(self, trade_detail, *args, **kwargs):
        super(HandleVarietyProfitThread, self).__init__(*args, **kwargs)
        self.trade_detail = trade_detail

    def run(self):
        data = dict()
        trade_df = pd.DataFrame(self.trade_detail)
        for key in ['close_profit', 'close_hands']:
            trade_df[key] = trade_df[key].astype(float)
        yingli_df = trade_df[trade_df['close_profit'] > 0]  # 取盈利的单
        kuisun_df = trade_df[trade_df['close_profit'] <= 0]   # 取亏损的单
        # 盈利金额、手数品种分布
        yingli_group = yingli_df.groupby(by=['variety_en'], as_index=False)
        yingli_jefb = yingli_group['close_profit'].agg({'sum_close_profit': 'sum'})
        yingli_shfb = yingli_group['close_hands'].agg({'sum_hands': 'sum'})
        # 合并
        group = pd.merge(yingli_jefb, yingli_shfb, on=['variety_en'], how='outer')
        group['variety_text'] = group['variety_en'].apply(lambda x: CH_VARIETY.get(x, x))
        data['yingli'] = group.to_dict(orient='records')  # 盈利品种对应盈利金额和盈利手数

        # 亏损金额、手数品种分布
        kuisun_group = kuisun_df.groupby(by=['variety_en'], as_index=False)
        kuisun_jefb = kuisun_group['close_profit'].agg({'sum_close_profit': 'sum'})
        kuisun_shfb = kuisun_group['close_hands'].agg({'sum_hands': 'sum'})
        # 合并
        group = pd.merge(kuisun_jefb, kuisun_shfb, on=['variety_en'], how='outer')
        group['variety_text'] = group['variety_en'].apply(lambda x: CH_VARIETY.get(x, x))
        data['kuisun'] = group.to_dict(orient='records')  # 亏损品种对应盈利金额和盈利手数
        self.handle_finished.emit(data)


class HandleRiskControlThread(QThread):
    handle_finished = pyqtSignal(dict)

    def __init__(self, account, trade_detail, *args, **kwargs):
        super(HandleRiskControlThread, self).__init__(*args, **kwargs)
        self.account = account
        self.trade_detail = trade_detail

    def run(self):
        account_df = pd.DataFrame(self.account)
        trade_df = pd.DataFrame(self.trade_detail)
        for a_key in ['rights', 'bail']:
            account_df[a_key] = account_df[a_key].astype(float)
        for t_key in []:
            trade_df[t_key] = trade_df[t_key].astype(float)
        # 仓位比例（保证金 / 权益）
        account_df['risk_rate'] = account_df['bail'] / account_df['rights']
        # 做多的单
        duo_df = trade_df[trade_df['is_long'] == 1]
        duo_yl = duo_df[duo_df['close_profit'] > 0]['close_profit'].sum()  # 多单盈利
        duo_ks = duo_df[duo_df['close_profit'] <= 0]['close_profit'].sum()  # 多单亏损
        duo_ylsh = duo_df[duo_df['close_profit'] > 0]['close_hands'].sum()
        duo_kssh = duo_df[duo_df['close_profit'] <= 0]['close_hands'].sum()

        # 做空的单
        kong_df = trade_df[trade_df['is_long'] == 0]
        kong_yl = kong_df[kong_df['close_profit'] > 0]['close_profit'].sum()  # 空单盈利
        kong_ks = kong_df[kong_df['close_profit'] <= 0]['close_profit'].sum()  # 空单亏损
        kong_ylsh = kong_df[kong_df['close_profit'] > 0]['close_hands'].sum()  # 空单盈利手数
        kong_kssh = kong_df[kong_df['close_profit'] <= 0]['close_hands'].sum()  # 空单亏损手数
        data = dict()
        # 仓位比率图
        data['cwbl'] = account_df[['exchange_date', 'risk_rate']].to_dict(orient='record')
        # 多空盈亏
        data['duo_kong_yk'] = [
            {'value': round(duo_yl, 2), 'name': '多单盈利'},
            {'value': round(-duo_ks, 2), 'name': '多单亏损'},
            {'value': round(kong_yl, 2), 'name': '空单盈利'},
            {'value': round(-kong_ks, 2), 'name': '空单亏损'},
        ]
        data['duo_kong_sh'] = [
            {'value': int(duo_ylsh), 'name': '多单盈利手数'},
            {'value': int(duo_kssh), 'name': '多单亏损手数'},
            {'value': int(kong_ylsh), 'name': '空单盈利手数'},
            {'value': int(kong_kssh), 'name': '空单亏损手数'},
        ]
        # 日内交易的单
        rinei_df = trade_df[trade_df['open_date'] == trade_df['close_date']]
        rinei_yk = rinei_df['close_profit'].sum()
        # 隔夜交易的单
        geye_df = trade_df[trade_df['open_date'] != trade_df['close_date']]
        geye_yk = geye_df['close_profit'].sum()
        rinei_name = '日内交易盈利'
        if rinei_yk<0:
            rinei_yk = -rinei_yk
            rinei_name = '日内交易亏损'
        geye_name = '隔夜交易盈利'
        if geye_yk < 0:
            geye_yk = -geye_yk
            geye_name = '隔夜交易亏损'

        data['rgyk'] = [
            {'value': round(rinei_yk, 2), 'name': rinei_name},
            {'value': round(geye_yk, 2), 'name': geye_name},
        ]
        self.handle_finished.emit(data)
