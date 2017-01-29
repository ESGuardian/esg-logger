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
addgroup elasticsearch
adduser -G elasticsearch elasticsearch
mkdir /var/log/elasticsearch
mkdir /var/elasticsearch
chown -R elasticsearch:elasticsearch /var/elasticsearch
chown -R elasticsearch:elasticsearch /var/log/elasticsearch
chown -R elasticsearch:elasticsearch /usr/share/elasticsearch
rc-update add elasticsearch
