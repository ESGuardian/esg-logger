#! /usr/bin/python
# -*- coding: utf8 -*-
import sys
from datetime import date, timedelta
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

outfilename='RA-' + today.strftime('%Y-%m-%d') + '.csv'
outfullpath='/usr/local/reports/' + outfilename
tabheader = u"\nУдаленный доступ с " + startdate + u" по " + enddate + u"\n\n"
colheader = u"Время;Имя;Группа;IP;Страна;Город;Назначенный IP\n"
myquery = {"query":{\
    "bool":{\
        "must":{"match_all":{}},\
        "filter":[{"term":{"event-code":"Remconn address assigned"}},{"range":{"@timestamp":{"gte":starttime, "lte":endtime, "format":"yyyy:MM:dd HH:mm:ss"}}}]\
    }\
    },\
"sort":{"@timestamp":{"order":"asc"}},\
"size":"10000"\
}

es = Elasticsearch()
res = es.search(index="cisco-asa-*",body=myquery)
with codecs.open(outfullpath, 'a', encoding="utf8") as out:
    out.write(tabheader)
    out.write(colheader)
    for hit in res['hits']['hits']:
        str = hit["_source"]["@timestamp"].replace("T"," ").split(".")[0]
        str += u";" + hit["_source"]["user"]
        str += u";" + hit["_source"]["group"]
        str += u";" + hit["_source"]["src_ip"]
        str += u";" + hit["_source"]["geoip"]["country_code2"]
        try:
            str += u";" + hit["_source"]["geoip"]["city_name"]
        except:
            str += u";-"
        str += u";" + hit["_source"]["assigned_ip"]
        str += u"\n"
        out.write(str)
out.close

