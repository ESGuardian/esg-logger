# Заменяем OSSIM более простой конструкцией на основе ELK #
Такая вот осенняя мысль закралась в мою голову. Заменить OSSIM чем-то более простым и более производительным. Чтобы не было "лишних" функций, например, собственно SIEM, и чтобы лучше работалось с "сырыми" логами. Я остановился на стеке Elasticsearch - Logstash - Kibana (ELK) в качестве хранилища, парсера, и средства просмотра и анализа логов. Основными компонентами OSSIM являются AlienVault HIDS и AlienVault NIDS, проще говоря, OSSEC и Suricata. Сурикату я взял из репозитария Debian. Это не последняя версия, зато ставится одной командочкой apt-get install. А вот OSSEC я взял форкнутый, Wazuh OSSEC на [wazuh.com](http://wazuh.com). Почему его? Wazuh изначально делал конструкцию OSSEC + ELK и они уже проработали такие вещи, как шаблоны индексов для Elasticsearch, дашборды для Kibana, и учли потребности соответствия стандартам, вроде PCI DSS. Их документация содержит очень толковую инструкцию, как по установке ELK, так и по интеграции OSSEC с ELK. Правда, я делал немножко иначе. Совсем чуть-чуть иначе, поскольку их инструкции рассчитаны на более старую версию ELK, а я установил последнюю стабильную версию. И конфиги пришлось переделать отчасти по причине новой версии, отчасти из-за того, что в документации описан случай, когда ELK принимает данные только от OSSEC, а у меня, как понятно, OSSEC не единственный поставщик событий.

Архитектурно конструкция состоит из двух виртуальных машин Debian 8. На одной установлен ELK, на другой - OSSEC, Suricata и Logstash forvarder. Обе эти машины вместе потребляют только половину от тех ресурсов, которые отъедал один Alienvault OSSIM. А вот поиск и анализ данных происходит намного шустрее.

Теперь приступим к описанию установки и конфигурации. Начнем с ELK.

## Установка и настройка ELK ##
Прежде всего необходимо подготовить чистую виртуальную машину с Debian 8. Базовая установка системы + SSH Server (это для удобства). Условимся называть эту машину elastic. Далее зайти на консоль рутом.


    cd ~
    apt-get install git
    apt-get install openssl

Теперь нужно сделать заготовку для генерации самоподписанного сертификата для сервера (понадобится для шифрования линка со второй машиной). Надо открыть в редакторе файл `/etc/ssl/openssl.cnf` и вписать в секцию `[ v3_ca ]` нужные параметры:


    [ v3_ca ]
    subjectAltName = IP: elastic_server_ip

Разумеется, надо вписать реальный IP машины elastic. Теперь можно продолжить.

    git clone -b master https://bitbucket.org/esguardian/ESG-Logger.git
    ./ESG-Logger/ELK/elk-install.sh

В процессе установки придется принять лицензионное соглашение Oracle на Java, и задать пароль для пользователя kibana.

После установки заходим на http://your_host/ и входим под именем kibana с тем самым паролем. 

В этом решении kibana прикрыта сервером nginx. Это сделано специально, чтобы можно было организовать защиту доступа, а при необходимости использовать SSL.

ВАЖНО! В текущей конфигурации параметры резервирования памяти для elasticsearch установлены в расчете на то, что на машине имеется по крайней мере 12GB оперативной памяти. Если не знаете где это поменять, смотрите мою статью [elastic для маленьких](https://esguardian.ru/2016/12/25/elastic-for-little-ones-optimize-for-a-small-company/)

## Установка Wazuh OSSEC и Suricata ##

А вот здесь нам придется поработать вручную. Простого скрипта у меня пока нет. Прежде всего нам понадобится чистая виртуальная машина Debian 8 (базовая установка + SSH Server) с двумя сетевыми интерфейсами. Eth0 оставьте обычным интерфейсом, а на eth1 подайте поток SPAN от ваших коммутаторов. Условимся называть эту машину wazuh.

Начнем с установки Wazuh OSSEC. Это просто.

    apt-get update && apt-get upgrade
    apt-get install unzip
    apt-get install curl
    apt-get install apt-transport-https
    apt-key adv --fetch-keys http://ossec.wazuh.com/repos/apt/conf/ossec-key.gpg.key
    echo -e "deb http://ossec.wazuh.com/repos/apt/debian jessie main" >> /etc/apt/sources.list.d/ossec.list
    apt-get update
    apt-get install gcc make git
    apt-get install libssl-dev
    cd ~
    git clone -b stable https://github.com/wazuh/ossec-wazuh.git
    cd ossec-wazuh
    ./install.sh

Проверим, что OSSEC настроен на вывод в формате JSON. Для этого откроем файл `/var/ossec/etc/ossec.conf` и убедимся что в самом верху написано так:

      <global>
        <jsonout_output>yes</jsonout_output>
        <email_notification>no</email_notification>
      </global>

Запустим OSSEC.

    /var/ossec/bin/ossec-control start

Теперь установим Сурикату. Возьмем её из репозитария Debian.

    apt-get install suricata

Конфиг сурикаты проще скопировать, чем описать, поэтому делаем так:

    cd ~
    git clone -b master https://bitbucket.org/esguardian/ESG-Logger.git
    rm /etc/suricata/suricata-debian.yaml
    cp ~/ESG-Logger/wazuh/etc/suricata/suricata-debian.yaml /etc/suricata/
    rm /etc/default/suricata
    cp ~/ESG-Logger/wazuh/etc/default/* /etc/default/
    cp ~/ESG-Logger/wazuh/etc/logrotate.d/* /etc/logrotate.d/

Теперь ставим менеджер сигнатур

    apt-get install oinkmaster
    rm /etc/oinkmaster.conf
    cp ~/ESG-Logger/wazuh/etc/* /etc/
    oinkmaster -C /etc/oinkmaster.conf -o /etc/suricata/rules
    rm /etc/suricata/rules/decoder-events.rules
    rm /etc/suricata/rules/stream-events.rules

Последние два файла с правилами я удаляю, поскольку ничего, кроме мусора, от них нет. Запускаем сурикату.

    /bin/systemctl daemon-reload
    /bin/systemctl enable suricata.service
    /bin/systemctl start suricata.service 

Теперь установим Java.

    echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" > /etc/apt/sources.list.d/webupd8team-java.list
    echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" >> /etc/apt/sources.list.d/webupd8team-java.list
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886
    apt-get update
    apt-get install oracle-java8-installer

Теперь filebeat
    
    curl https://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -
    echo "deb https://packages.elastic.co/beats/apt stable main" | tee -a /etc/apt/sources.list.d/beats.list
    apt-get update && apt-get install filebeat
    


Теперь нам нужно скопировать файл с сертификатом машины elastic на машину wazuh в каталог `/etc/filebeat/`. Этот файл сгенерировался скриптом установки и лежит здесь: `/etc/logstash/logstash-forwarder.crt`. После этого необходимо на машине wazuh отредактировать файл `/etc/filebeat/filebeat.yml`. Он должен стать вот таким:

        filebeat:
          # List of prospectors to fetch data.
          prospectors:
            # Each - is a prospector. Below are the prospector specific configurations
            -
              paths:
                - /var/ossec/logs/alerts/alerts.json
               
              encoding: cp1251
              input_type: log
              document_type: ossec-alerts
            -
              paths:
                - /var/log/suricata/eve-ids.json
              encoding: plain
              input_type: log
              document_type: suricata-alerts

          
          registry_file: /var/lib/filebeat/registry

          
        output:
          logstash:
            # The Logstash hosts
            hosts: ["192.168.1.1:5043"]

            tls:
              certificate_authorities: ["/etc/filebeat/logstash-forwarder.crt"]

        logging:

          files:
            rotateeverybytes: 10485760 # = 10MB


Опять же не забудем указать реальный IP машины elastic. Можем запускать forwarder.

    /bin/systemctl daemon-reload
    /bin/systemctl enable filebeat.service
    service filebeat start

Всё. События пошли на elastic.
Теперь поработаем с kibana.
## Dashboards, searches and vizualizations
Если вы следовали инструкции, то в `/root/ESG-logger/ELK` лежит файл `ESG-dashboards.json`. Он содержит мои дашборды и визуализации, которыми я обычно пользуюсь. Частью это измененные дашборды от Wazuh, частью мои собственные. Вы можете импортировать их в Kibana через веб-интерфейс (меню Settings - Objects). Конечно, каждый делает дашборды под себя, но может быть пригодятся для начала. Там кроме OSSEC и Suricata еще Fortigate и Cisco-ASA.

В текущих конфигурациях лог с Fortigate принимается на машину elastic на порт 5000, а с Cisco-ASA на порт 10514. grok-patterns для парсинга лога Cisco мои собственные, часть переделана из стандартных, часть добавлена.

В Fortigate нельзя сменить порт для отправки syslog из веб-интерфейса. Это можно сделать только в CLI. 

	config log syslogd setting
	set port <port_integer>
	end

## Изменения ##
- 21.10.2016

Перешел на Suricata 3.1. Соответственно изменен файл конфигурации `suricata-debian.yaml`, добавил в вывод `eve-ids.json` payload пакетов. Это удобнее для просмотра логов.

Добавил скрипты на python для генерации отчетов, аналогичных тем, что делал когда-то для OSSIM. Лежат в `ELK/usr/local/bin`.

- 25.10.2016

Добавил сбор журнала Zecurion Zlock. Это делает logstash, через input plugin jdbc. Драйвер jdbc лежит в `/opt/logstash/jdbc` этот каталог надо скопировать в аналогичный на сервере elastic. Для подключения к базе данных zlock необходимо создать пользователя с правами select на таблицу ZNTF_Data2. Данные подключения вписать в файл `/etc/logstash/config.d/06-zlock.conf`. Кстати, пользоваться намного удобнее, чем консолью zlock.

- 27.10.2016

Добавил скрипт для генерации отчета по событиям Suricata в csv для импорта в Libre Office Calc (или MS Excel)

- 28.10.2016

Обновлены отчеты и выгружены новые дашборды и визуализации для kibana.

- 29.10.2016

Выполнен апгрейд стека ELK до версии 5.0. Это требует ряда изменений в конфигурационных файлах. Подробности [здесь](https://bitbucket.org/esguardian/esg-logger/src/e6d6c1db42fc38c4005d18566671ae862f6426b8/ELK/_upgrade50/?at=master).

- 03.11.2016

Добавил чтение журнала аудита Oracle DB аналогично чтению журнала Zlock, только контроль последней прочитанной записи по timestamp, ну и база Oracle, а не MS SQL, соответственно другой jdbc драйвер и немного другие параметры соединения.

Немного поправил скрипт установки elastic он теперь не копирует в рабочий каталог файлы конфигурации logstash для zlock и oracle, поскольку их перед использованием надо править руками вписывая необходимые параметры соединения.

И да, версию 5.0 я таки не использую. В основном по причине багов в работе Kibana 5.0 с браузером IE 11. К тому же мне не нравится новый интерфейс Kibana. Когда-нибудь перейти придется, но пока подождем.

И еще. Я больше не буду выкладывать дашборды. Это совсем не нужное дело. Старый файл с дашбордами пусть остается для образца.

- 07.11.2016

Немного "замутил" логи ORACLE, чтобы их удобнее было читать.

- 07.01.2017

За это время многое переделалось. Сейчас я выложил обновленные файлы конфигурации. И на машине wazuh я давно не использую logstash-forwarder, поэтому переписал инструкцию под filebeat.

- 15.01.17

Я постепенно убираю OSSEC. Штука хорошая, но я хочу иметь более нативную систему сбора логов и более простую в развертывании. Сбор логов Windows уже давно делается на Winlogbeat, а теперь и linux переезжает на filebeat. Соответственно файл конфигурации Logstash `03-winlogbeat.conf` превратился в `03-beats.conf`.


