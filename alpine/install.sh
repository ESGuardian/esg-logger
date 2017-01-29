#!/bin/ash
apk add nano
nano /etc/apk/repositories
apk update
apk add openjdk8-jre
apk add curl
apk add bash
apk add util-linux pciutils usbutils coreutils binutils findutils grep
cd /tmp
curl -L -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.1.2.tar.gz
tar -xvf elasticsearch-5.1.2.tar.gz
cp -R elasticsearch-5.1.2/ /usr/share/elasticsearch
rm /usr/share/elasticsearch/bin/*.bat
rm /usr/share/elasticsearch/bin/*.exe
curl -L -O https://raw.githubusercontent.com/ESGuardian/esg-logger/master/alpine/01-elasticsearch.conf
cp 01-elasticsearch.conf /etc/sysctl.d/01-elasticsearch.conf
chmod 644 /etc/sysctl.d/01-elasticsearch.conf
curl -L -O https://raw.githubusercontent.com/ESGuardian/esg-logger/master/alpine/elasticsearch
cp elasticsearch /etc/init.d/elasticsearch
chmod 755 /etc/init.d/elasticsearch
curl -L -O https://raw.githubusercontent.com/ESGuardian/esg-logger/master/alpine/elasticsearch.yml
rm /usr/share/elasticsearch/config/elasticsearch.yml
cp elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml 
curl -L -O https://raw.githubusercontent.com/ESGuardian/esg-logger/master/alpine/jvm.options.elastic
rm /usr/share/elasticsearch/config/jvm.options
cp jvm.options.elastic /usr/share/elasticsearch/config/jvm.options 
addgroup elasticsearch
adduser -G elasticsearch elasticsearch
mkdir /var/log/elasticsearch
mkdir /var/elasticsearch
chown -R elasticsearch:elasticsearch /var/elasticsearch
chown -R elasticsearch:elasticsearch /var/log/elasticsearch
chown -R elasticsearch:elasticsearch /usr/share/elasticsearch
rc-update add elasticsearch
