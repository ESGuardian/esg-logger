#! /usr/bin/python
# -*- coding: utf8 -*-
import sys
from datetime import date, timedelta
from elasticsearch import Elasticsearch 
import codecs
period=1
if len(sys.argv) > 1:
    period=int(sys.argv[1])

app_install = True
antimalware_config = True
file_integrity = True
app_monitor = True


today=date.today()
enddate=today.strftime('%Y:%m:%d')
endtime=enddate + ' 09:00:00' # local time
startdate=(today - timedelta(days=period)).strftime('%Y:%m:%d')
starttime=startdate + ' 09:00:00'

outfilename='APP-' + today.strftime('%Y-%m-%d') + '.csv'
outfullpath='/usr/local/reports/' + outfilename
es = Elasticsearch()

if app_install :
    tabheader = u"\nУстановка приложений с " + startdate + u" по " + enddate + u"\n\n"
    colheader = u"Время;Действие;Источник;Оператор;Установщик;Продукт\n"
    myquery =   {"query":\
                    {\
                        "constant_score":{\
                            "filter":[\
                                {"bool":{\
                                    "must":[\
                                        {"range":{"@timestamp":{"gte":starttime, "lte":endtime, "format":"yyyy:MM:dd HH:mm:ss"}}},\
                                        {"bool": {
                                            "should":[\
                                                {"term":{"rule.sidid":"18146"}},\
                                                {"term":{"rule.sidid":"18147"}}\
                                            ]\
                                        }}\
                                    ]\
                                }},\
                            ]\
                        }\
                    },\
                    "sort":{"@timestamp":{"order":"asc"}},\
                    "size":"10000"\
                }
    res = es.search(index="ossec-*",body=myquery)
    with codecs.open(outfullpath, 'a', encoding="utf8") as out:
        out.write(tabheader)
        out.write(colheader)
        for hit in res['hits']['hits']:
            str = hit["_source"]["@timestamp"].replace("T"," ").split(".")[0]
            try:
                str += u";" + hit["_source"]["rule"]["description"]
            except:
                str += u";-"
            try:
                str += u";" + hit["_source"]["systemname"]
            except:
                try:
                    str += u";" + hit["_source"]["AgentIP"]
                except:
                    str += u";-"
            try:
                str += u";" + hit["_source"]["dstuser"]
            except:
                str += u";-"
            try:
                data = hit["_source"]["data"]
            except:
                data = "-"
            try:
                msg = hit["_source"]["full_log"]
            except:
                msg = "-"
            str += u";" + data
            
            if data == "MsiInstaller":
                msg1 = msg.split(u"Product:")[-1].replace("(NULL)","").strip().replace(","," ").replace(";",":")
                msg1 = msg1.split(u"Продукт:")[-1].replace("(NULL)","").strip().replace(","," ").replace(";",":")
            else:
                msg1 = msg.replace(","," ").replace("\t"," ").replace(";",":")
            str += u";" + msg1   
            str += u"\n"
            out.write(str)
    out.close

if antimalware_config :
    tabheader = u"\nКонфигурация антивируса с " + startdate + u" по " + enddate + u"\n\n"
    colheader = u"Время;Действие;Источник;Оператор;Установщик;Продукт\n"
    myquery =   {"query":\
                    {\
                        "constant_score":{\
                            "filter":[\
                                {"bool":{\
                                    "must":[\
                                        {"range":{"@timestamp":{"gte":starttime, "lte":endtime, "format":"yyyy:MM:dd HH:mm:ss"}}},\
                                        {"bool": {
                                            "should":[\
                                                {"term":{"rule.sidid":"7721"}},\
                                                {"term":{"rule.sidid":"7722"}},\
                                                {"term":{"rule.sidid":"7726"}},\
                                            ]\
                                        }}\
                                    ]\
                                }},\
                            ]\
                        }\
                    },\
                    "sort":{"@timestamp":{"order":"asc"}},\
                    "size":"10000"\
                }
    res = es.search(index="ossec-*",body=myquery)
    with codecs.open(outfullpath, 'a', encoding="utf8") as out:
        out.write(tabheader)
        out.write(colheader)
        for hit in res['hits']['hits']:
            str = hit["_source"]["@timestamp"].replace("T"," ").split(".")[0]
            try:
                str += u";" + hit["_source"]["rule"]["description"]
            except:
                str += u";-"
            try:
                str += u";" + hit["_source"]["systemname"]
            except:
                try:
                    str += u";" + hit["_source"]["AgentIP"]
                except:
                    str += u";-"
            try:
                str += u";" + hit["_source"]["dstuser"]
            except:
                str += u";-"
            try:
                data = hit["_source"]["data"]
            except:
                data = "-"
            try:
                msg = hit["_source"]["full_log"]
            except:
                msg = "-"
            str += u";" + data
            
            if data == "Microsoft Antimalware":
                msg1 = msg.split(u"domain: ",1)[-1].replace(","," ").replace("\t"," ").replace(";",":").strip()     
            else:
                msg1 = msg.replace(","," ").replace("\t"," ").replace(";",":").strip()
            str += u";" + msg1   
            str += u"\n"
            out.write(str)
    out.close
    
if file_integrity :
    tabheader = u"\nКонтроль файлов с " + startdate + u" по " + enddate + u"\n\n"
    colheader = u"Время;Действие;Агент;-;-;Сообщение\n"
    myquery =   {"query":\
                    {\
                        "constant_score":{\
                            "filter":[\
                                {"bool":{\
                                    "must":[\
                                        {"range":{"@timestamp":{"gte":starttime, "lte":endtime, "format":"yyyy:MM:dd HH:mm:ss"}}},\
                                        {"bool": {
                                            "should":[\
                                                {"term":{"rule.sidid":"553"}},\
                                                {"term":{"rule.sidid":"550"}},\
                                                {"term":{"rule.sidid":"550"}},\
                                                {"term":{"rule.sidid":"513"}},\
                                            ]\
                                        }}\
                                    ]\
                                }},\
                            ]\
                        }\
                    },\
                    "sort":{"@timestamp":{"order":"asc"}},\
                    "size":"10000"\
                }
    res = es.search(index="ossec-*",body=myquery)
    with codecs.open(outfullpath, 'a', encoding="utf8") as out:
        out.write(tabheader)
        out.write(colheader)
        for hit in res['hits']['hits']:
            str = hit["_source"]["@timestamp"].replace("T"," ").split(".")[0]
            try:
                str += u";" + hit["_source"]["rule"]["description"]
            except:
                str += u";-"
            try:
                str += u";" + hit["_source"]["AgentName"]
            except:
                try:
                    str += u";" + hit["_source"]["AgentIP"]
                except:
                    str += u";-"
            
            try:
                msg = hit["_source"]["full_log"]
            except:
                msg = "-"
            str += u";-;-;" + msg.split("\n")[0].replace(","," ").replace("\t"," ").replace(";",":").strip()
             
            str += u"\n"
            out.write(str)
    out.close
if app_monitor :
    tabheader = u"\nКонтроль приложений с " + startdate + u" по " + enddate + u"\n\n"
    colheader = u"Время;Действие;Агент;-;-;Сообщение\n"
    myquery =   {"query":\
                    {\
                        "constant_score":{\
                            "filter":[\
                                {"bool":{\
                                    "must":[\
                                        {"range":{"@timestamp":{"gte":starttime, "lte":endtime, "format":"yyyy:MM:dd HH:mm:ss"}}},\
                                        {"bool": {
                                            "should":[\
                                                {"term":{"rule.sidid":"514"}},\
                                            ]\
                                        }}\
                                    ]\
                                }},\
                            ]\
                        }\
                    },\
                    "sort":{"@timestamp":{"order":"asc"}},\
                    "size":"10000"\
                }
    res = es.search(index="ossec-*",body=myquery)
    with codecs.open(outfullpath, 'a', encoding="utf8") as out:
        out.write(tabheader)
        out.write(colheader)
        for hit in res['hits']['hits']:
            str = hit["_source"]["@timestamp"].replace("T"," ").split(".")[0]
            try:
                str += u";" + hit["_source"]["rule"]["description"]
            except:
                str += u";-"
            try:
                str += u";" + hit["_source"]["AgentName"]
            except:
                try:
                    str += u";" + hit["_source"]["AgentIP"]
                except:
                    str += u";-"
            
            try:
                msg = hit["_source"]["full_log"]
            except:
                msg = "-"
            str += u";-;-;" + msg.split("\n")[0].replace(","," ").replace("\t"," ").replace(";",":").strip()
             
            str += u"\n"
            out.write(str)
    out.close
