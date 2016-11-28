#StockAnalysis
本程序用于中国A股市场股票组合的投资收益

##更新说明
### V1.0.1
更新时间2016年11月28日，更新内容：
1. 优化历史数据下载，增添伪装和超时处理
2. 为适应从其他地方下载的基础数据（例如通达信34数据导出），初始化数据至内存数据库时，修改文件匹配判断，现判断每行数据是否符合：
    - 必须有数据
    - 必须可以通过逗号解析为list
    - list长度至少为6
    - 正常数据格式为:
```Date,Open,High,Low,Close,Volume```

##使用指南

###准备配置文件
先准备一个类似如下的配置文件，假设存储至和Stockanalysis同级目录下的MOD1.JSON
- MODEL，此股票组合的名称
- STARTDT,从哪天开始计算
- CODELIST,股票代码列表，注：代码需要使用字符串格式
```
{
  "MODEL":"m1",
  "MODEL_DES" :"均线离散度<1.5",
  "STARTDT":"2016-11-14",
  "STARTDT_DES":"起始日期",
  "CODELIST":["300452", "300295", "300248", "600466", "601009",
            "601988", "000613", "000701", "300051", "300157",
            "300278", "002166", "600327", "600122"]
}
```

###使用
1. 执行StockAnalysis.exe
2. 输入配置文件 ，例如MOD1.JSON，成功后会出现
```
Initialization Sucessed!
Please input option:
['-download', '-initanaly', '-analyze', '-export', '-help']
or input [quit] to exit
```
3. 下载数据，输入-download，如果之前下载过数据，则此步骤省略
4. 数据下载完成后，输入 -initanaly
5. -analyze
6. 如果需要保存数据，可以执行-export，数据将被导出至同级目录下，格式是sqlite3
7. 