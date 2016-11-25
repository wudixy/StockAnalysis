#-*- coding: utf-8 -*-

import urllib
import sys
import os
import json
import sqlite3
import platform
import string
import StringIO

sysstr = platform.system()
if(sysstr == "Windows"):
    file_Separator = '\\'
elif(sysstr == "Linux"):
    file_Separator = '/'


class stockAnalysis:

    __base_url = 'http://table.finance.yahoo.com'
    __scriptPath = os.path.split(os.path.realpath(__file__))[0]
    tconfig = {}

    def __init__(self):
        self.__memconn = sqlite3.connect(":memory:")
        self.__memconn.isolation_level = None
        self.__memconn.row_factory = sqlite3.Row
        self.__memcur = self.__memconn.cursor()

    def __del__(self):
        self.__memconn.close()

    def readConfig(self, fname):
        """read config file,and get repostory db file,init log"""
        if os.path.exists(fname):
            f = open(fname)
            js = f.read()
            try:
                self.tconfig = json.loads(js)
                self.__basepath = self.__scriptPath + file_Separator + self.tconfig['MODEL']
                self.__datapath = self.__basepath + file_Separator + 'BASEDT'
                if not os.path.exists(self.__basepath):
                    os.mkdir(self.__basepath)
                if not os.path.exists(self.__datapath):
                    os.mkdir(self.__datapath)
                sql = "create table %s_model (Code TEXT(10),Date TEXT(10),Open Real(6,2),High Real(6,2),Low Real(6,2),\
                       Close Real(6,2),Volume Real)" % self.tconfig['MODEL']
                self.__memcur.execute(sql)
                sql = "CREATE TABLE ANALYZE_BASE(Code TEXT,st REAL,ed REAL,sy REAL)"
                self.__memcur.execute(sql)

                self.__memconn.commit()
                return True
            except Exception, e:
                print str(e)
                return False
            finally:
                f.close()
        else:
            print 'config file:%s not found' % (fname)
            return False

    def __getUrl(self, code):
        hz = ''
        if str(code)[:1] in ('3', '0'):
            hz = '.sz'
        else:
            hz = '.ss'
        url = self.__base_url + '/table.csv?s=' + str(code) + hz
        fname = str(code) + '.txt'
        return {'url': url, 'filename': fname}

    def downHistory2File(self, code):
        dinfo = self.__getUrl(code)
        fname = self.__datapath + file_Separator + dinfo['filename']
        urllib.urlretrieve(dinfo['url'], fname)

    def downAllHisDt(self):
        i = 0
        for cd in self.tconfig['CODELIST']:
            i = i + 1
            if cd is None:
                continue
            print 'download history data-' + str(i) + ':' + str(cd)[:6]
            self.downHistory2File(cd[:6])

    def writeDT2MemDB(self, code):
        fname = self.__datapath + file_Separator + str(code) + '.txt'

        f = open(fname)
        line = f.readline()
        if line[:4] != 'Date':
            return 0
        line = f.readline()
        ct = 0
        while line:
            ld = line.split(',')
            if not ld:
                continue
            sql = "insert into %s_model(Code,Date,Open,High,Low,Close,Volume) \
                   values('%s','%s',%.2f,%.2f,%.2f,%.2f,%.2f)" % \
                (self.tconfig['MODEL'], str(code), ld[0][:10], string.atof(ld[1]), string.atof(ld[2]),
                 string.atof(ld[3]), string.atof(ld[4]), string.atof(ld[5]))
            self.__memcur.execute(sql)
            ct = ct + 1
            line = f.readline()
        f.close()
        self.__memconn.commit()
        return ct

    def writeAllDT2MemDB(self):
        ct = 0
        for cd in self.tconfig['CODELIST']:
            fname = self.__datapath + file_Separator + str(cd) + '.txt'
            if os.path.exists(fname):
                ct = ct + self.writeDT2MemDB(cd)
            else:
                continue
        print 'insert %d data' % (ct,)

    def analysis_base(self):
        sql = "delete from  ANALYZE_BASE;\
               insert into ANALYZE_BASE \
               select a.code,a.Close st,b.Close ed, (b.Close - a.Close)/a.close sy \
               from %s_model a \
               left join %s_model b \
               on a.Code=b.Code \
               and b.date=(select max(date) from %s_model) \
               where a.Date = '%s';" % (self.tconfig['MODEL'], self.tconfig['MODEL'],
                                        self.tconfig['MODEL'], self.tconfig['STARTDT'])

        self.__memcur.executescript(sql)
        self.__memconn.commit()

    def getCompositeIncome(self):
        sql = "select (sum(ed)-sum(st))/sum(st) from ANALYZE_BASE"
        self.__memcur.execute(sql)
        res = self.__memcur.fetchone()
        if res:
            res = res[0]
        else:
            res = 0
        return res

    def getTopN(self):
        sql = "select a.code,a.st,a.ed,a.sy from ANALYZE_BASE a\
               order by a.sy desc"
        self.__memcur.execute(sql)
        format_head = '|{code:^8s}|{start:^7s}|{end:^7s}|{sy:^7s}|'
        formatstr = '|{code:<8s}|{start:<7.2f}|{end:<7.2f}|{sy:<7.4f}|'
        # os.system("cls")
        print "{name:-^34s}".format(name='')
        print format_head.format(code='CODE', start='START', end='END', sy='SY')

        res = self.__memcur.fetchall()
        for a in res:
            print "{name:-^34s}".format(name='')
            print formatstr.format(code=a[0], start=a[1], end=a[2], sy=a[3])

    def export2Sqlite(self):
        fname = self.__basepath + file_Separator + self.tconfig['MODEL'] + '.db'
        if os.path.exists(fname):
            flag = raw_input('%s is exists,input [y] to overwrite,other to return\n' % (fname,))
            if flag == 'y':
                try:
                    os.remove(fname)
                except Exception, e:
                    tp = sys.getfilesystemencoding()
                    print str(e).decode('utf-8').encode(tp)
                    return False
            else:
                return False
        # 生成内存数据库脚本
        str_buffer = StringIO.StringIO()
        # con.itrdump() dump all sqls
        for line in self.__memconn.iterdump():
            str_buffer.write('%s\n' % line)
        # 打开文件数据库
        con_file = sqlite3.connect(fname)
        cur_file = con_file.cursor()
        # 执行内存数据库脚本
        cur_file.executescript(str_buffer.getvalue())
        # 关闭文件数据库
        cur_file.close()

    def getCurData(self, code):
        urllist = 'list='
        if str(code)[:1] in ('3', '0'):
            hz = 'sz'
        else:
            hz = 'sh'
        urllist = urllist + hz + str(code) + ','

        f = urllib.urlopen("http://hq.sinajs.cn/" + urllist)
        s = f.read()

        s = s.replace('sz', "")
        s = s.replace('sh', "")
        s = s.replace('var hq_str_', "{'code':")
        s = s.replace('=', ",'info':")
        s = s.replace(';', "}")
        # s = s.split(';')
        s = eval(s)
        return s


CMD_LIST = ['-download', '-initanaly', '-analyze', '-export', '-help']


def printhelp():
    print 'user guide\n\
           1. -download data;if already download,you can ignore\n\
           2. -initanaly\n\
           3. -analyze\n\
           4. -export\n'


def main():
    promt = 'Please input configFile:\n'
    parmas = raw_input(promt + '\n')
    if os.path.exists(parmas):
        sa = stockAnalysis()
        sa.readConfig(parmas)
        print 'Initialization Sucessed!'
        promt = 'Please input option:\n%s\nor input [quit] to exit\n' % (CMD_LIST, )
        while True:
            parmas = raw_input(promt + '\n')
            if parmas == 'quit':
                break
            elif parmas == '-download':
                sa.downAllHisDt()
            elif parmas == '-initanaly':
                sa.writeAllDT2MemDB()
            elif parmas == '-export':
                # ename = raw_input('pls input export name,default use MODEL name\n')
                # if not ename:
                    # ename = sa.tconfig['MODEL']
                sa.export2Sqlite()
            elif parmas == '-help':
                printhelp()
            elif parmas == '-analyze':
                sa.analysis_base()
                ci = sa.getCompositeIncome()
                print 'Composite Income is %.4f' % (ci,)
                sa.getTopN()
    else:
        print 'configfile %s is not found' % (parmas,)


if __name__ == '__main__':
    main()
