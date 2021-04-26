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

        # 取成交明细表需要的列[合约,开仓日期,买/卖,开仓价,开仓手数,平仓日期,平仓价,平仓手数,平仓盈亏]
        exchange_df = exchange_df[['contract', 'ex_date', 'sale_text', 'ex_price', 'hands', 'close_date', 'close_price', 'close_hands']]
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

    def run(self):
        #  转为DataFrame
        account_df = pd.DataFrame(self.account_data)  # 资金明细表
        trade_detail = pd.DataFrame(self.trade_detail)  # 交易明细表
        # 处理目标数据
        return



        # 提取出平仓明细表
        close_df = exchange_df[exchange_df['open_text'].str.contains('平')]
        close_df['ex_profit'] = close_df['ex_profit'].astype(float)
        close_df['hands'] = close_df['hands'].astype(float)
        # 计算交易胜率 平仓利润为+ / 总笔数
        win_rate = close_df[close_df['ex_profit'] > 0].shape[0] / close_df.shape[0]
        # 计算盈亏比
        profit_loss_rate = close_df[close_df['ex_profit'] > 0]['ex_profit'].sum() / close_df[close_df['ex_profit'] < 0]['ex_profit'].sum()

        # 排序资金明细表
        account_df.sort_values(by=['exchange_date'], inplace=True)
        # 当日存取转为float计算净出入金
        account_df['sum_in_out'] = account_df['sum_in_out'].astype(float)
        account_df['pre_rights'] = account_df['pre_rights'].astype(float)
        account_df['rights'] = account_df['rights'].astype(float)
        account_df['bail'] = account_df['bail'].astype(float)
        account_df['profit'] = account_df['profit'].astype(float)
        account_df['charge'] = account_df['charge'].astype(float)
        # 计算当日净值=(当日权益 - 当日存取)/上日权益
        account_df['net_value'] = (account_df['rights'] - account_df['sum_in_out']) / account_df['pre_rights']
        # 计算日收益率
        account_df['daily_profit_rate'] = account_df['net_value'] - 1
        # 当日累计净值=前日累计净值*当日净值
        account_df['daily_net_value'] = account_df['net_value'].cumprod()
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

        # 计算累计净利润 净利润 = 当日盈亏 - 手续费
        account_df['net_profit'] = account_df['profit'] - account_df['charge']
        # 历史最大本金
        history_maxp = (account_df['rights'] - account_df['sum_in_out']).max()
        cum_net_profit = account_df.at[account_df.shape[0] - 1, 'daily_net_value']
        # 计算手续费/净利润
        charge_dv_profit = account_df['charge'].sum() / account_df['net_profit'].sum()
        # 计算仓位比例(风险度=保证金/当日权益)
        account_df['risk_rate'] = account_df['bail'] / account_df['rights']

        base_data = {
            'start_date': account_df.at[0, 'exchange_date'],
            'end_date': account_df.at[account_df.shape[0] - 1, 'exchange_date'],
            'initial_equity': account_df.at[0, 'rights'],  # 期初权益
            'ending_equity': account_df.at[account_df.shape[0] - 1, 'rights'],  # 期末权益
            'net_income': account_df['sum_in_out'].sum(),  # 累计净入金
            'max_huiche_date': max_huiche,  # 最大回撤时点
            'max_huiche_range': f'{max_huiche} ~ {min_huiche}',  # 最大回撤区间
            'accumulated_net': round(cum_net_profit, 3),  # 累计净利润
            'maxrrate': '{}%'.format(round(account_df['retracement'].max() * 100, 2)),  # 最大回撤率
            'accumulated_profit': round(account_df['profit'].sum(), 2),
            'average_daily': round(account_df['daily_profit_rate'].mean(), 4),  # 日收益率均值
            'exchange_cost': round(account_df['charge'].sum(), 2),  # 交易费用
            'historical_maxp': round(history_maxp, 2),  # 历史最大本金
            'max_daily_profit': '{}%'.format(round(account_df['daily_profit_rate'].max() * 100, 2)),  # 历史最高收益率
            'min_daily_profit': '{}%'.format(round(account_df['daily_profit_rate'].min() * 100, 2)),  # 历史最低收益率
            'expected_annual_rate': round(account_df['daily_profit_rate'].mean() * 250, 4),  # 预计年化收益率,
            'total_days': account_df.shape[0],
            'profit_days': account_df[account_df['profit'] > 0].shape[0],
            'loss_days': account_df[account_df['profit'] <= 0].shape[0],
            'wining_rate': round(win_rate, 4),
            'profit_loss_rate': round(-profit_loss_rate, 4),
            'net_profit': round(charge_dv_profit, 4),  # 手续费/净利润，
            'zdckbl': round(account_df['risk_rate'].max() * 100, 2),  # 最大持仓仓位比例
            'pjckbl': round(account_df['risk_rate'].mean() * 100, 2),  # 平均持仓仓位比例
            'kcts': account_df[account_df['profit'] == 0].shape[0],  # 空仓天数(当日盈亏为0的天数)
            'place': ''
        }  # 基础数据
        time.sleep(1)
        # 组织诊断分析的数据
        # 获利的数据
        yldf = close_df[close_df['ex_profit'] > 0]  # 盈利的交易
        ksdf = close_df[close_df['ex_profit'] <= 0]  # 亏损的交易
        drksdf = account_df[account_df['profit'] <= 0]  # 单日亏损的交易
        yl_list, ks_list = [], []
        yl_c, ks_c = 0, 0
        for _, row in close_df.iterrows():
            p = row['ex_profit']
            if p > 0:
                yl_c += 1
                yl_list.append(yl_c)
                ks_c = 0
            if p <= 0:
                ks_c += 1
                ks_list.append(ks_c)
                yl_c = 0
        doctor_data = {
            'jyk': round(account_df['net_profit'].sum(), 2),  # 净盈亏
            'jybs': close_df.shape[0],  # 交易笔数
            'ylbs': yldf.shape[0],  # 盈利笔数
            'ksbs': ksdf.shape[0],  # 亏损笔数
            'zghl': yldf['ex_profit'].max(),  # 单笔最高获利
            'pjhl': yldf['ex_profit'].sum() / yldf.shape[0],  # 平均获利 = 获利和 ÷ 获利笔数
            'zgks': ksdf['ex_profit'].min(),   # 单笔最高亏损
            'pjks': ksdf['ex_profit'].sum() / ksdf.shape[0],  # 平均亏损 = 亏损的笔数 ÷ 亏损笔数
            'drzgks': drksdf['profit'].min(),  # 单日最高亏损
            'drpjks': round(drksdf['profit'].sum() / drksdf.shape[0], 2),  # 单日平均亏损
            'lxyl': max(yl_list),  # 连续盈利笔数
            'lxks': max(ks_list)  # 连续亏损笔数
        }
        print(doctor_data)
        base_data.update(doctor_data)  # 合并
        self.handle_finished.emit(base_data)


# 处理累计收益率数据
class HandProfitThread(QThread):
    handle_finished = pyqtSignal(list)

    def __init__(self, source, *args, **kwargs):
        super(HandProfitThread, self).__init__(*args, **kwargs)
        self.source = source

    def run(self):
        # 根据传入的source处理出累计收益数据
        account_df = pd.DataFrame(self.source)
        account_df['sum_in_out'] = account_df['sum_in_out'].astype(float)
        account_df['pre_rights'] = account_df['pre_rights'].astype(float)
        account_df['rights'] = account_df['rights'].astype(float)
        account_df['charge'] = account_df['charge'].astype(float)
        # 计算当日净值=(当日权益 - 当日存取)/上日权益
        account_df['net_value'] = (account_df['rights'] - account_df['sum_in_out']) / account_df['pre_rights']
        # # 计算日收益率
        # account_df['daily_profit_rate'] = account_df['net_value'] - 1
        # 当日累计净值=前日累计净值*当日净值
        account_df['daily_net_value'] = account_df['net_value'].cumprod()

        t = account_df[['exchange_date', 'net_value', 'daily_net_value']]
        t.columns = ['exchange_date', 'profit_rate', 'cum_sum']

        t['profit_rate'] = t['profit_rate'].apply(lambda x: round(x, 2))
        t['cum_sum'] = t['cum_sum'].apply(lambda x: round(x, 2))
        del account_df
        self.handle_finished.emit(t.to_dict(orient='records'))


# 处理累计净利润
class HandNetProfitsThread(QThread):

    handle_finished = pyqtSignal(list)

    def __init__(self, source, *args, **kwargs):
        super(HandNetProfitsThread, self).__init__(*args, **kwargs)
        self.source = source

    def run(self):
        # 根据传入的source处理出累计收益数据
        df = pd.DataFrame(self.source)
        time.sleep(1)
        # 计算每日的净利润
        df['profit'] = df['profit'].apply(lambda x: float(x.replace(',', '')))
        df['charge'] = df['charge'].apply(lambda x: float(x.replace(',', '')))
        df['net_profit'] = df['profit'] - df['charge']
        t = df[['exchange_date', 'net_profit']]
        t['net_profit_cumsum'] = df['net_profit'].cumsum()
        t['net_profit_cumsum'] = t['net_profit_cumsum'].apply(lambda x: round(x, 2))
        del df
        self.handle_finished.emit(t.to_dict(orient='records'))


# 使用成交明细表统计累计品种盈亏数据
class HandleSumVarietyProfitThread(QThread):
    handle_finished = pyqtSignal(list)

    def __init__(self, source, *args, **kwargs):
        super(HandleSumVarietyProfitThread, self).__init__(*args, **kwargs)
        self.source = source

    def run(self):
        # 根据传入的source处理出累计品种盈亏数据(分品种计算各盈利金额，亏损金额，盈利手数，亏损手数)
        df = pd.DataFrame(self.source)
        time.sleep(1)
        # 选取平仓的数据
        df = df[df['open_text'].str.contains('平')]
        # 交易收益转为float
        df['ex_profit'] = df['ex_profit'].astype(float)
        df['hands'] = df['hands'].astype(float)
        # 解析出品种英文代码
        df['variety_en'] = df['contract'].apply(lambda x: split_number_en(x)[0])
        # 品种分组计算目标数据
        varieties = list(df.groupby(by=['variety_en']).groups.keys())
        result = []
        for v_name in varieties:
            variety_dict = {
                'variety_en': v_name,
                'variety_text': CH_VARIETY.get(v_name, v_name),
                'yingli': 0,
                'kuisun': 0,
                'yingli_count': 0,
                'kuisun_count': 0
            }
            cur_vdf = df[df['variety_en'] == v_name]
            # 统计这个品种的盈利和亏损
            variety_dict['yingli'] = cur_vdf[cur_vdf['ex_profit'] >= 0]['ex_profit'].sum()
            variety_dict['yingli_count'] = cur_vdf[cur_vdf['ex_profit'] >= 0]['hands'].sum()
            variety_dict['kuisun'] = cur_vdf[cur_vdf['ex_profit'] < 0]['ex_profit'].sum()
            variety_dict['kuisun_count'] = cur_vdf[cur_vdf['ex_profit'] < 0]['hands'].sum()
            result.append(variety_dict)
        result.sort(key=lambda x: x['yingli'], reverse=True)
        self.handle_finished.emit(result)


# 处理风险度
class RiskThread(QThread):

    handle_finished = pyqtSignal(list)

    def __init__(self, source, *args, **kwargs):
        super(RiskThread, self).__init__(*args, **kwargs)
        self.source = source

    def run(self):
        # 根据传入的source处理出累计收益数据
        df = pd.DataFrame(self.source)
        # 返回每日的风险度
        # df['risk_percent'] = df['bail'] / df['rights']
        t = df[['exchange_date', 'risk']]
        t['risk'] = t['risk'].apply(lambda x: float(x.replace('%', '').replace(',','')))
        del df
        self.handle_finished.emit(t.to_dict(orient='records'))


# 统计交易品种
class VarietyPercentThread(QThread):

    handle_finished = pyqtSignal(list)

    def __init__(self, source, *args, **kwargs):
        super(VarietyPercentThread, self).__init__(*args, **kwargs)
        self.source = source

    def run(self):
        # 根据传入的source处理出交易品种饼图需要的数据，各品种交易额占总交易额的比例
        df = pd.DataFrame(self.source)
        time.sleep(1)
        # 分组品种，计算交易额,交易手数
        # 交易收益转为float
        df['ex_money'] = df['ex_money'].astype(float)
        df['hands'] = df['hands'].astype(float)
        # 解析出品种英文代码
        df['variety_en'] = df['contract'].apply(lambda x: split_number_en(x)[0])
        # 品种分组计算目标数据
        varieties = list(df.groupby(by=['variety_en']).groups.keys())
        result = []
        for v_name in varieties:
            variety_dict = {
                'variety_en': v_name,
                'variety_text': CH_VARIETY.get(v_name, v_name),
                'ex_money': 0,
                'hands': 0
            }
            cur_vdf = df[df['variety_en'] == v_name]
            # 统计这个品种
            variety_dict['ex_money'] = cur_vdf['ex_money'].sum()
            variety_dict['hands'] = cur_vdf['hands'].sum()
            result.append(variety_dict)
        result.sort(key=lambda x: x['ex_money'], reverse=True)

        # df['turnover'] = df['turnover'].astype(float)
        # t = df.groupby(by=['variety'])['turnover'].sum()
        # del df
        # t = pd.DataFrame({'variety': t.index, 'value': t.values})
        # sum_value = t['value'].sum()
        # t['percent'] = t['value'] / sum_value
        # print(t)
        self.handle_finished.emit(result)


# 统计多空盈亏(成交明细表=>平仓明细表=>统计多空)
class ShortMoretThread(QThread):

    handle_finished = pyqtSignal(dict)

    def __init__(self, source, *args, **kwargs):
        super(ShortMoretThread, self).__init__(*args, **kwargs)
        self.source = source

    def run(self):
        # 根据传入的source处理出交易的多单和空单分别的盈利亏损占总额的比例
        df = pd.DataFrame(self.source)
        time.sleep(1)
        # 平 卖 就是做多的单，平 买 就是做空的单
        # 选取平仓的数据
        df = df[df['open_text'].str.contains('平')]
        df['hands'] = df['hands'].astype(float)
        df['ex_profit'] = df['ex_profit'].astype(float)
        duo_df = df[df['sale_text'].str.contains('卖')]  # 做多的单
        kong_df = df[df['sale_text'].str.contains('买')]  # 做空的单
        duo_yingli = duo_df[duo_df['ex_profit'] >= 0]['ex_profit'].sum()
        duo_yingli_count = duo_df[duo_df['ex_profit'] >= 0]['hands'].sum()
        duo_kuisun = duo_df[duo_df['ex_profit'] < 0]['ex_profit'].sum()
        duo_kuisun_count = duo_df[duo_df['ex_profit'] < 0]['hands'].sum()
        kong_yingli = kong_df[kong_df['ex_profit'] >= 0]['ex_profit'].sum()
        kong_yingli_count = kong_df[kong_df['ex_profit'] >= 0]['hands'].sum()
        kong_kuisun = kong_df[kong_df['ex_profit'] < 0]['ex_profit'].sum()
        kong_kuisun_count = kong_df[kong_df['ex_profit'] < 0]['hands'].sum()
        # print('多单盈利', duo_yingli)
        # print('多单亏损', duo_kuisun)
        # print('空单盈利', kong_yingli)
        # print('空单亏损', kong_kuisun)

        # 盈亏分布
        duo_list = duo_df.to_dict(orient='records')
        kong_list = kong_df.to_dict(orient='records')
        duo, kong = [], []
        for index, item in enumerate(duo_list):
            duo.append([index, item['ex_profit']])
        for index, item in enumerate(kong_list):
            kong.append([index, item['ex_profit']])

        # for index, item in enumerate(range(1100)):
        #     duo.append([index, random.randint(-3000, 5000)])
        # for index, item in enumerate(range(1000)):
        #     kong.append([index, random.randint(-2000, 2000)])

        result = [
            {'valueName': '多单盈利', 'value': duo_yingli, 'handName': '多单盈利手数', 'hands': duo_yingli_count},
            {'valueName': '多单亏损', 'value': duo_kuisun, 'handName': '多单亏损手数', 'hands': duo_kuisun_count},
            {'valueName': '空单盈利', 'value': kong_yingli, 'handName': '空单盈利手数', 'hands': kong_yingli_count},
            {'valueName': '空单亏损', 'value': kong_kuisun, 'handName': '空单亏损手数', 'hands': kong_kuisun_count}
        ]
        d = {
            'pieData': result,
            'scatterSale': kong,  # 空单盈亏分布
            'scatterBuy': duo  # 多单盈亏分布
        }
        self.handle_finished.emit(d)