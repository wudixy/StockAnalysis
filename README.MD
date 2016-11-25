#StockAnalysis
本程序用于中国A股市场股票组合的投资收益

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