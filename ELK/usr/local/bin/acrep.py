#! /usr/bin/python
# -*- coding: utf8 -*-
import sys
import string
from datetime import date, timedelta, datetime
from pytz import timezone
from elasticsearch import Elasticsearch 
import codecs
period=1
if len(sys.argv) > 1:
    period=int(sys.argv[1])

global_group = True
local_group = True
accounts = True



today=date.today()
enddate=today.strftime('%Y:%m:%d')
endtime=enddate + ' 09:00:00' # local time
startdate=(today - timedelta(days=period)).strftime('%Y:%m:%d')
starttime=startdate + ' 09:00:00'

outfilename='AC-' + today.strftime('%Y-%m-%d') + '.csv'
outfullpath='/usr/local/reports/' + outfilename
es = Elasticsearch()

if global_group :
    tabheader = u"\nИзменение глобальных групп с " + startdate + u" по " + enddate + u"\n\n"
    colheader = u"Время;Действие;Источник;Оператор;Группа;Пользователь\n"
    myquery =   {"query":\
                    {\
                        "constant_score":{\
                            "filter":[\
                                {"bool":{\
                                    "must":[\
                                        {"range":{"@timestamp":{"gte":starttime, "lte":endtime, "format":"yyyy:MM:dd HH:mm:ss", "time_zone": "+03:00"}}},\
                                        {"bool": {
                                            "should":[\
                                                {"term":{"rule.sidid":"18202"}},\
                                                {"term":{"rule.sidid":"18203"}},\
                                                {"term":{"rule.sidid":"18204"}},\
                                                {"term":{"rule.sidid":"18214"}},\
                                                {"term":{"rule.sidid":"18215"}},\
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
            timestr = hit["_source"]["@timestamp"].replace("T"," ").split(".")[0]
            timeUTC = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
            timeUTC = timeUTC.replace(tzinfo=timezone('UTC'))
            timeLocal = timeUTC.astimezone(timezone('Europe/Moscow'))
            str = timeLocal.strftime("%Y-%m-%d %H:%M:%S")
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
                    msg = hit["_source"]["full_log"]
            except:
                msg = "-"
            if hit["_source"]["rule"]["sidid"] == 18202 :
                try:
                    operator = msg.split("Account Name:")[1].split("Account Domain:")[0].strip()
                except:
                    operator = "-"
                str += u";" + operator
                group_name = msg.split("Group Name:")[-1].split("Group Domain:")[0].strip()
                str += u";" + group_name
                # извлекаем описание операции из payload, если не получится запишем payload как есть
                try:
                    info = msg.split('Subject:',1)[0].split(': ')[-1].strip()
                except:
                    info = msg.replace(","," ").replace("\t"," ").replace(";",":").strip()
                str += u";" + info
            elif hit["_source"]["rule"]["sidid"] == 18215 or hit["_source"]["rule"]["sidid"] == 18214:
                try:
                    operator = msg.split('Group: Security ID:',1)[-1].split(' Account Domain:',1)[0].split('Account Name: ')[-1]
                except:
                    operator = u"-"
                str += u";" + operator
                # извлекаем название группы из payload
                try:
                    group_name = msg.split('Account Domain',1)[-1].split('Account Name: ',1)[-1].split('Account Name: ',1)[-1].split(' Account',1)[0]
                except:
                    group_name = u"-"
                str += u";" + group_name
                # извлекаем имя пользователя из payload, если не получится запишем payload как есть
                try:
                    member_name = string.capwords(msg.lower().split('cn=', 1)[-1].split(',ou=',1)[0])
                except:
                    member_name = msg.replace(","," ").replace("\t"," ").replace(";",":").strip()
                str += u";" + member_name 
            else:                
                try:
                    operator = msg.split("Account Name:")[1].split("Account Domain:")[0].strip()
                except:
                    operator = "-"
                str += u";" + operator
                group_name = msg.split("Group Name:")[-1].split("Group Domain:")[0].strip()
                str += u";" + group_name
                member_name = msg.split("Account Name:")[-1].split(",")[0].strip().lower().split("cn=")[-1]
                member_name = string.capwords(member_name)
                str += u";" + member_name             
            str += u"\n"
            out.write(str)
    out.close

if local_group :
    tabheader = u"\nИзменение локальных групп с " + startdate + u" по " + enddate + u"\n\n"
    colheader = u"Время;Действие;Источник;Оператор;Группа;Пользователь\n"
    myquery =   {"query":\
                    {\
                        "constant_score":{\
                            "filter":[\
                                {"bool":{\
                                    "must":[\
                                        {"range":{"@timestamp":{"gte":starttime, "lte":endtime, "format":"yyyy:MM:dd HH:mm:ss", "time_zone": "+03:00"}}},\
                                        {"bool": {
                                            "should":[\
                                                {"term":{"rule.sidid":"18207"}},\
                                                {"term":{"rule.sidid":"18208"}},\
                                                {"term":{"rule.sidid":"18209"}},\
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
            timestr = hit["_source"]["@timestamp"].replace("T"," ").split(".")[0]
            timeUTC = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
            timeUTC = timeUTC.replace(tzinfo=timezone('UTC'))
            timeLocal = timeUTC.astimezone(timezone('Europe/Moscow'))
            str = timeLocal.strftime("%Y-%m-%d %H:%M:%S")
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
                    msg = hit["_source"]["full_log"]
            except:
                msg = "-"
            try:
                operator = msg.split("Account Name:")[1].split("Account Domain:")[0].strip()
            except:
                operator = "-"
            str += u";" + operator
            group_name = msg.split("Group Name:")[-1].split("Group Domain:")[0].strip()
            str += u";" + group_name
            if hit["_source"]["rule"]["sidid"] == 18207 or hit["_source"]["rule"]["sidid"] == 18208 :
                member_name = msg.split("Member:")[-1].split("Account Name:")[0].strip()
            else:
                member_name = u"-"
            str += u";" + member_name             
            str += u"\n"
            out.write(str)
    out.close
    
if accounts :
    tabheader = u"\nИзменение учетных записей с " + startdate + u" по " + enddate + u"\n\n"
    colheader = u"Время;Действие;Источник;Оператор;Сообщение;Пользователь\n"
    myquery =   {"query":\
                    {\
                        "constant_score":{\
                            "filter":[\
                                {"bool":{\
                                    "must":[\
                                        {"range":{"@timestamp":{"gte":starttime, "lte":endtime, "format":"yyyy:MM:dd HH:mm:ss", "time_zone": "+03:00"}}},\
                                        {"bool": {
                                            "should":[\
                                                {"term":{"rule.sidid":"18112"}},\
                                                {"term":{"rule.sidid":"18110"}},\
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
            timestr = hit["_source"]["@timestamp"].replace("T"," ").split(".")[0]
            timeUTC = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
            timeUTC = timeUTC.replace(tzinfo=timezone('UTC'))
            timeLocal = timeUTC.astimezone(timezone('Europe/Moscow'))
            str = timeLocal.strftime("%Y-%m-%d %H:%M:%S")
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
                    msg = hit["_source"]["full_log"]
            except:
                msg = "-"
            try:
                operator = msg.split("Account Name:")[1].split("Account Domain:")[0].strip()
            except:
                operator = "-"
            str += u";" + operator
            info = msg.split("Subject:")[0].split(": ")[-1].strip()
            str += u";" + info
            acc_name = msg.split("Account Domain:")[1].split("Account Name:")[-1].strip()
            str += u";" + acc_name             
            str += u"\n"
            out.write(str)
    out.close