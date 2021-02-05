# _*_ coding:utf-8 _*_
# @File  : constant.py
# @Time  : 2020-08-21 12:50
# @Author: zizle

REPORT_TYPE = {1: '收盘日评', 2: '周度报告', 3: '月度报告', 4: '年度报告', 5: '分析文章', 6: '调研报告',
               7: '技术解盘', 8: '投资方案', 9: '套保方案', 0: '其他'}
# 所有品种对应的中文名
VARIETY_ZH = {
    'A': '黄大豆1号',
    'B': '黄大豆2号',
    'BC': '铜(BC)',
    'C': '玉米',
    'CS': '玉米淀粉',
    'EB': '苯乙烯',
    'EG': '乙二醇',
    'I': '铁矿石',
    'J': '焦炭',
    'JD': '鸡蛋',
    'JM': '焦煤',
    'L': '聚乙烯',
    'LH': '生猪',
    'M': '豆粕',
    'P': '棕榈油',
    'PF': '短纤',
    'PG': '液化石油气',
    'PP': '聚丙烯',
    'RR': '粳米',
    'V': '聚氯乙烯',
    'Y': '豆油',
    'IC': '中证500股指',
    'IF': '沪深300股指',
    'IH': '上证50股指',
    'T': '10年期国债',
    'TF': '5年期国债',
    'TS': '2年期国债期',
    'AP': '苹果',
    'CF': '棉花',
    'CJ': '红枣',
    'CY': '棉纱',
    'FG': '玻璃',
    'JR': '粳稻',
    'LR': '晚籼',
    'MA': '甲醇',
    'OI': '菜油',
    'PM': '普麦',
    'RI': '早籼',
    'RM': '菜粕',
    'RS': '菜籽',
    'SA': '纯碱',
    'SF': '硅铁',
    'SM': '锰硅',
    'SR': '白糖',
    'TA': '精对苯二甲酸',
    'UR': '尿素',
    'WH': '强麦',
    'ZC': '动力煤',
    'AG': '白银',
    'AL': '铝',
    'AU': '黄金',
    'BU': '沥青',
    'CU': '铜',
    'FU': '燃料油',
    'HC': '热轧卷板',
    'LU': '低硫燃料油',
    'NI': '镍',
    'NR': '20号胶',
    'PB': '铅',
    'RB': '螺纹钢',
    'RU': '天然橡胶',
    'SC': '原油',
    'SN': '锡',
    'SP': '纸浆',
    'SS': '不锈钢',
    'WR': '线材',
    'ZN': '锌',
}

# 中文对应品种交易代码(使用场景:提取现货数据;提取每日仓单)
VARIETY_EN = {
    'IF': 'IF',
    'IC': 'IC',
    'IH': 'IH',
    '生猪': 'LH',
    '沪深300': 'IF',
    '中证500': 'IC',
    '上证50': 'IH',
    '铜(CU)': 'CU',
    '铜': 'CU',
    '铜(BC)': 'BC',
    '短纤': 'PF',
    '铝': 'AL',
    '铅': 'PB',
    '花生': 'PK',
    '锌': 'ZN',
    '锡': 'SN',
    '镍': 'NI',
    '铁矿石': 'I',
    '热轧卷板': 'HC',
    '热卷': 'HC',
    '螺纹钢': 'RB',
    '螺纹': 'RB',
    '螺纹钢仓库': 'RB',
    '螺纹钢厂库': 'RB',
    '线材': 'WR',
    '不锈钢': 'SS',
    '不锈钢仓库': 'SS',
    '硅铁': 'SF',
    '硅锰': 'SM',
    '锰硅': 'SM',
    '焦煤': 'JM',
    '焦炭': 'J',
    '动力煤': 'ZC',
    '郑煤': 'ZC',
    '黄金': 'AU',
    '白银': 'AG',
    '大豆': 'A',
    '豆一': 'A',
    '豆二': 'B',
    '胶合板': 'BB',
    '豆粕': 'M',
    '豆油': 'Y',
    '棕榈油': 'P',
    '粳米': 'RR',
    '白糖': 'SR',
    '棉花': 'CF',
    '棉纱': 'CY',
    '苹果': 'AP',
    '红枣': 'CJ',
    '聚丙烯': 'PP',
    '聚氯乙烯': 'V',
    '聚乙烯': 'L',
    '鸡蛋': 'JD',
    '菜粕': 'RM',
    '菜籽粕': 'RM',
    '菜油': 'OI',
    '菜籽油': 'OI',
    '玉米': 'C',
    '淀粉': 'CS',
    'LLDPE': 'L',
    'PP': 'PP',
    'PVC': 'V',
    '苯乙烯': 'EB',
    '低硫燃料油仓库': 'LU',
    '低硫燃料油厂库': 'LU',
    '全乳胶': 'RU',
    '天然橡胶': 'RU',
    '橡胶': 'RU',
    '20号胶': 'NR',
    'STR20': 'NR',
    '甲醇': 'MA',
    '尿素': 'UR',
    '玻璃': 'FG',
    '纯碱': 'SA',
    '乙二醇': 'EG',
    'PTA': 'TA',
    '纸浆': 'SP',
    '纸浆仓库': 'SP',
    '纸浆厂库': 'SP',
    '沥青': 'BU',
    '沥青仓库': 'BU',
    '沥青厂库': 'BU',
    '石油沥青仓库': 'BU',
    '石油沥青厂库': 'BU',
    '纤维板': 'FB',
    '液化气': 'PG',
    'LPG': 'PG',
    '燃料油': 'FU',
    '液化石油气': 'PG',
    '原油': 'SC',
    '玉米淀粉': 'CS',
    '中质含硫原油': 'SC',
}

HORIZONTAL_SCROLL_STYLE = "QScrollBar:horizontal{background:transparent;height:10px;margin:0px;}" \
            "QScrollBar:horizontal:hover{background:rgba(0,0,0,30);border-radius:5px}" \
            "QScrollBar::handle:horizontal{background:rgba(0,0,0,50);height:10px;border-radius:5px;border:none}" \
            "QScrollBar::handle:horizontal:hover{background:rgba(0,0,0,100)}" \
            "QScrollBar::add-page:horizontal{height:10px;background:transparent;}" \
            "QScrollBar::sub-page:horizontal{height:10px;background:transparent;}" \
            "QScrollBar::sub-line:horizontal{width:0px}" \
            "QScrollBar::add-line:horizontal{width:0px}"

VERTICAL_SCROLL_STYLE = "QScrollBar:vertical{background: transparent; width:10px;margin: 0px;}" \
            "QScrollBar:vertical:hover{background:rgba(0,0,0,30);border-radius:5px}" \
            "QScrollBar::handle:vertical{background: rgba(0,0,0,50);width:10px;min-height:50px;border-radius:5px;border:none}" \
            "QScrollBar::handle:vertical:hover{background:rgba(0,0,0,100)}" \
            "QScrollBar::add-page:vertical{width:10px;background:transparent;}" \
            "QScrollBar::sub-page:vertical{width:10px;background:transparent;}" \
            "QScrollBar::sub-line:vertical{height:0px}" \
            "QScrollBar::add-line:vertical{height:0px}"

HORIZONTAL_HEADER_STYLE = "QHeaderView::section{background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1," \
            "stop:0 #49aa54, stop: 0.48 #49cc54,stop: 0.52 #49cc54, stop:1 #49aa54);" \
            "border:1px solid rgb(201,202,202);border-left:none;" \
            "min-height:25px;min-width:40px;font-weight:bold;font-size:13px};"

BLUE_STYLE_HORIZONTAL_STYLE = "QHeaderView::section{background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1," \
            "stop:0 #66bbd5, stop: 0.48 #66bbd5,stop: 0.52 #66bbd5, stop:1 #66bbd5);" \
            "border:1px solid rgb(60,60,60);border-left:none;" \
            "min-height:25px;min-width:40px;font-weight:bold};"

HORIZONTAL_STYLE_NO_GRID = "QHeaderView::section{background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1," \
            "stop:0 #66bbd5, stop: 0.48 #66bbd5,stop: 0.52 #66bbd5, stop:1 #66bbd5);" \
            "border:1px solid rgb(60,60,60);border-left:none;border-right:none;" \
            "min-height:25px;min-width:40px;font-weight:bold};"
