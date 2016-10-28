#! /usr/bin/python
# -*- coding: utf8 -*-
import sys
from datetime import date, timedelta, datetime
from pytz import timezone
from elasticsearch import Elasticsearch 
import codecs
period=1
if len(sys.argv) > 1:
    period=int(sys.argv[1])


today=date.today()
enddate=today.strftime('%Y:%m:%d')
endtime=enddate + ' 09:00:00' # local time
startdate=(today - timedelta(days=period)).strftime('%Y:%m:%d')
starttime=startdate + ' 09:00:00'

outfilename='DLP-' + today.strftime('%Y-%m-%d') + '.csv'
outfullpath='/usr/local/reports/' + outfilename
tabheader = u"\nУтечки данных с " + startdate + u" по " + enddate + u"\n\n"
colheader = u"Время;Пользователь;Источник;Внешний IP;Внешний хост;Фильтр;Имя файла;URL\n"
myquery = {"query":{\
    "bool":{\
        "must":{"match_all":{}},\
        "filter":[{"term":{"subtype":"dlp"}},{"range":{"@timestamp":{"gte":starttime, "lte":endtime, "format":"yyyy:MM:dd HH:mm:ss", "time_zone": "+03:00"}}}]\
    }\
    },\
"sort":{"@timestamp":{"order":"asc"}},\
"size":"10000"\
}

es = Elasticsearch()
res = es.search(index="fortigate-*",body=myquery)
with codecs.open(outfullpath, 'a', encoding="utf8") as out:
    out.write(tabheader)
    out.write(colheader)
    for hit in res['hits']['hits']:
        timestr = hit["_source"]["@timestamp"].replace("T"," ").split(".")[0]
        timeUTC = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
        timeUTC = timeUTC.replace(tzinfo=timezone('UTC'))
        timeLocal = timeUTC.astimezone(timezone('Europe/Moscow'))
        str = timeLocal.strftime("%Y-%m-%d %H:%M:%S")
        try:
            str += u";" + hit["_source"]["user"]
        except:
            str += u";-"
        try:
            str += u";" + hit["_source"]["src_ip"]
        except:
            str += u";-"
        try:
            str += u";" + hit["_source"]["dst_ip"]
        except:
            str += u";-"
        try:
            str += u";" + hit["_source"]["hostname"]
        except:
            str += u";-"
        try:
            str += u";" + hit["_source"]["filtertype"]
        except:
            str += u";-"
        try:
            str += u";" + hit["_source"]["filename"]
        except:
            str += u";-"
        try:
            str += u";" + hit["_source"]["url"]
        except:
            str += u";-"
        str += u"\n"
        out.write(str)
out.close

