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

Теперь logstash-forwarder (aka Lamberjack).

    wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -
    echo "deb https://packages.elasticsearch.org/logstashforwarder/debian stable main" | tee -a /etc/apt/sources.list
    apt-get update
    apt-get install logstash-forwarder
    usermod -a -G ossec logstash-forwarder

Теперь нам нужно скопировать файл с сертификатом машины elastic на машину wazuh в каталог `/opt/logstash-forwarder/`. Этот файл сгенерировался скриптом установки и лежит здесь: `/etc/logstash/logstash-forwarder.crt`. После этого необходимо на машине wazuh отредактировать файл `/etc/logstash-forwarder.conf`. Он должен стать вот таким:

    {
      "network": {
        "servers": [ "elastic_server_ip:5043" ],
        "ssl ca": "/opt/logstash-forwarder/logstash-forwarder.crt",
        "timeout": 15
      },
      "files": [
        {
            "paths": [
              "/var/ossec/logs/alerts/alerts.json"
             ],
            "fields": { "type": "ossec-alerts" }
        },
        {
            "paths": [
              "/var/log/suricata/eve-ids.json"
             ],
            "fields": { "type": "suricata-alerts" }
        }
    
      ]
    }

Опять же не забудем указать реальный IP машины elastic. Можем запускать forwarder.

    /bin/systemctl daemon-reload
    /bin/systemctl enable logstash-forwarder.service
    /bin/systemctl start logstash-forwarder.service 

Всё. События пошли на elastic.
Теперь поработаем с kibana.
## Dashboards, searches and vizualizations
Если вы следовали инструкции, то в `/root/ESG-logger/ELK` лежит файл `ESG-dashboards.json`. Он содержит мои дашборды и визуализации, которыми я обычно пользуюсь. Частью это измененные дашборды от Wazuh, частью мои собственные. Вы можете импортировать их в Kibana через веб-интерфейс (меню Settings - Objects). Конечно, каждый делает дашборды под себя, но может быть пригодятся для начала. Там кроме OSSEC и Suricata еще Fortigate и Cisco-ASA.

В текущих конфигурациях лог с Fortigate принимается на машину elastic на порт 5000, а с Cisco-ASA на порт 10514. grok-patterns для парсинга лога Cisco мои собственные, часть переделана из стандартных, часть добавлена.

В Fortigate нельзя сменить порт для отправки syslog из веб-интерфейса. Это можно сделать только в CLI. 

	config log syslogd setting
	set port <port_integer>
	end

Пока всё.