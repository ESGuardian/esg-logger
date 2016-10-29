# Апгрейд ELK на версию 5.0 #
## Общие замечания ##
После апгрейда кое-что изменится. Например, плагин geoip больше не сможет работать со старой версией базы данных Maxmind. В каталоге `_upgrade50` в соответствующих подкаталогах лежат файлы которые необходимо скопировать на сервер elastic (разумеется с заменой старых) и перезапустить сервисы ELK.

## Как проводить апгрейд ##
Во-первых, запишите новый адрес и ключ реапозитария ELK и установите apt-transport https

    wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
    echo "deb https://artifacts.elastic.co/packages/5.x/apt stable main" | tee -a /etc/apt/sources.list.d/elastic-5.x.list 
    apt-get install apt-transport-https 

Во-вторых, остановите все сервисы ELK.

    service kibana stop
    service logstash stop
    service elasticsearch stop

Я обновлял elasticsearch простой переустановкой, файлы конфигурации будут сохранены (там вопрос будет, обновлять или нет, по умолчанию - нет).

    apt-get update && apt-get install elasticsearch 

А вот logstash я обновлял апгрейдом.

    apt-get upgrade logstash 

Я думал, что обновится только logstash, а нет. Обновились сразу logstash, kibana и даже nginx. Но это не самое интересное.

Интересно то, что не записался новый скрипт init.d для logstash. Я так и не понял почему. А зря не записался, поскольку в logstash изменилось многое, в том числе домашняя директория и кое-какие параметры командной строки, например `--configtest` больше нет, вместо него `-t`. Пришлось поправить скрипт руками. Еще пришлось скачать базу GeoLite2-City.mmdb c [maxmind](http://dev.maxmind.com/geoip/geoip2/geolite2/) и поправить конфиги logstash для обработки источников, где у меня используется фильтр geoip, поскольку новый плагин geoip не работает со старым форматом базы.

Все необходимые правленые файлы лежат в каталоге `_upgrade50` в соответствующих подкаталогах в репозитарии на [bitbucket](https://bitbucket.org/esguardian/esg-logger/src/3b164a7aff018f76da68e33dcabe6b91f63e8f7b/ELK/?at=master). Их следует скопировать на сервер elastic. 

Теперь можно запустить стек.

    service elasticsearch start
    service logstash start
    service kibana start

Вот и всё.
 