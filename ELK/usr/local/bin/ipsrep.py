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

outfilename='IPS-' + today.strftime('%Y-%m-%d') + '.csv'
outfullpath='/usr/local/reports/' + outfilename
tabheader = u"Подозрительные события Suricata с " + startdate + u" по " + enddate + u"\n\n"
colheader = u"Сигнатура;Время;Источник;Целевой хост;Ссылка на событие\n"
myquery =   {"query":\
    {\
        "constant_score":{\
            "filter":[\
                {"bool":{\
                    "must":[\
                        {"range":{"@timestamp":{"gte":starttime, "lte":endtime, "format":"yyyy:MM:dd HH:mm:ss", "time_zone": "+03:00"}}},\
                        {"bool": {
                            "should":[\
                                {"term":{"alert.category":"A Network Trojan was Detected"}},\
                                {"term":{"alert.category":"Potentially Bad Traffic"}},\
                                {"term":{"alert.category":"Potential Corporate Privacy Violation"}},\
                            ],\
                            "must_not":[\
                                {"term":{"alert.signature_id":"2014170"}},\
                                {"term":{"alert.signature_id":"2002157"}},\
                                {"term":{"alert.signature_id":"2001595"}},\
                            ]\
                        }}\
                    ]\
                }},\
            ]\
        }\
    },\
    "sort":[{"alert.signature":{"order":"asc"}}, {"@timestamp":{"order":"asc"}}],\
    "size":"10000"\
}

es = Elasticsearch()
res = es.search(index="suricata-*",body=myquery)
with codecs.open(outfullpath, 'a', encoding="utf8") as out:
    out.write(tabheader)
    out.write(colheader)
    prev_str=""
    for hit in res['hits']['hits']:
        try:
            str = hit["_source"]["alert"]["signature"]
        except:
            str = u"-"
        if prev_str != "" :
            if prev_str != str :
                prev_str = str
                str = u"\n\n" + str
        else :
            prev_str = str
        timestr = hit["_source"]["@timestamp"].replace("T"," ").split(".")[0]
        timeUTC = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
        timeUTC = timeUTC.replace(tzinfo=timezone('UTC'))
        timeLocal = timeUTC.astimezone(timezone('Europe/Moscow'))
        str += u";" + timeLocal.strftime("%Y-%m-%d %H:%M:%S")
        try:
            str += u";" + hit["_source"]["src_ip"]
        except:
            str += u";-"
        try:
            str += u";" + hit["_source"]["dest_ip"]
        except:
            str += u";-"
        urlstring = u'=HYPERLINK("http://elastic/app/kibana#/doc/suricata-*/'
        urlstring += hit["_index"]
        urlstring += u'/suricata?id=' + hit["_id"]  + '")'   
        str += u";" + urlstring        
        str += u"\n"
        out.write(str)
out.close

