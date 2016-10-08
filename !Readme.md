# Заменяем OSSIM более простой конструкцией на основе ELK #
Такая вот осенняя мысль закралась в мою голову. Заменить OSSIM чем-то более простым и более производительным. Чтобы не было "лишних" функций, например, собственно SIEM, и чтобы лучше работалось с "сырыми" логами. Я остановился на стеке Elasticsearch - Logstash - Kibana (ELK) в качестве хранилища, парсера, и средства просмотра и анализа логов. Основными компонентами OSSIM являются AlienVault HIDS и AlienVault NIDS, проще говоря, OSSEC и Suricata. Сурикату я взял из репозитария Debian. Это не последняя версия, зато ставится одной командочкой apt-get install. А вот OSSEC я взял форкнутый, Wazuh OSSEC на [wazuh.com](http://wazuh.com). Почему его? Wazuh изначально делал конструкцию OSSEC + ELK и они уже проработали такие вещи, как шаблоны индексов для Elasticsearch, дашборды для Kibana, и учли потребности соответствия стандартам, вроде PCI DSS. Их документация содержит очень толковую инструкцию, как по установке ELK, так и по интеграции OSSEC с ELK. Правда, я делал немножко иначе. Совсем чуть-чуть иначе, поскольку их инструкции рассчитаны на более старую версию ELK, а я установил последнюю стабильную версию. И конфиги пришлось переделать отчасти по причине новой версии, отчасти из-за того, что в документации описан случай, когда ELK принимает данные только от OSSEC, а у меня, как понятно, OSSEC не единственный поставщик событий.

Архитектурно конструкция состоит из двух виртуальных машин Debian 8. На одной установлен ELK, на другой - OSSEC, Suricata и Logstash forvarder. Обе эти машины вместе потребляют только половину от тех ресурсов, которые отъедал один Alienvault OSSIM. А вот поиск и анализ данных происходит намного шустрее.

Теперь приступим к описанию установки и конфигурации. Начнем с ELK.

## Установка и настройка ELK ##