apt-get update && apt-get upgrade
apt-get install python-software-properties-common
apt-get install unzip
apt-get install curl
apt-get install openssl

echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" > /etc/apt/sources.list.d/webupd8team-java.list
echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" >> /etc/apt/sources.list.d/webupd8team-java.list
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886
apt-get update
apt-get install oracle-java8-installer

wget https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/deb/elasticsearch/2.4.0/elasticsearch-2.4.0.deb
dpkg --install elasticsearch-2.4.0.deb
rm /etc/elasticsearch/elasticsearch.yml
rm /etc/elasticsearch/logging.yml
cp ~/ESG-Logger/ELK/etc/elasticsearch/*.yml  /etc/elasticsearch/
mkdir /var/data/elasticsearch
chown elasticsearch:elasticsearch /var/data/elasticsearch


wget https://download.elastic.co/logstash/logstash/packages/debian/logstash-2.4.0_all.deb
dpkg --install logstash-2.4.0_all.deb
cp ~/ESG-Logger/ELK/etc/logstash/conf.d/01-fortigate.conf /etc/logstash/conf.d/
cp ~/ESG-Logger/ELK/etc/logstash/conf.d/02-wazuh.conf /etc/logstash/conf.d/
cp ~/ESG-Logger/ELK/etc/logstash/conf.d/03-winlogbeat.conf /etc/logstash/conf.d/
cp ~/ESG-Logger/ELK/etc/logstash/conf.d/04-cisco.conf /etc/logstash/conf.d/
mkdir /etc/logstash/patterns
cp ~/ESG-Logger/ELK/etc/logstash/patterns/* /etc/logstash/patterns/
cp ~/ESG-Logger/ELK/etc/logstash/*.json /etc/logstash/
curl -O "http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz"
gzip -d GeoLiteCity.dat.gz && mv GeoLiteCity.dat /etc/logstash/
cd /etc/ssl/
openssl req -config /etc/ssl/openssl.cnf -x509 -days 3650 -batch -nodes -newkey rsa:2048 -keyout /etc/logstash/logstash-forwarder.key -out /etc/logstash/logstash-forwarder.crt
cd ~




wget https://download.elastic.co/kibana/kibana/kibana-4.6.1-amd64.deb
dpkg --install kibana-4.6.1-amd64.deb
rm /opt/kibana/config/kibana.yml
cp ~/ESG-Logger/ELK/opt/kibana/config/* /opt/kibana/config/


apt-get install nginx apache2-utils
rm /etc/nginx/sites-available/default
cp ~/ESG-Logger/ELK/etc/nginx/sites-available/default /etc/nginx/sites-available/
htpasswd -c /etc/nginx/conf.d/kibana.htpasswd kibana

cp ~/ESG-Logger/ELK/etc/defaul/* /etc/default/
cp ~/ESG-Logger/ELK/etc/security/* /etc/security/
cp ~/ESG-Logger/ELK/usr/lib/sysctl.d/* /usr/lib/sysctl.d/
cp ~/ESG-Logger/ELK/usr/lib/systemd/* /usr/lib/systemd/

/bin/systemctl daemon-reload
/bin/systemctl enable elasticsearch.service
/bin/systemctl start elasticsearch.service

/bin/systemctl enable logstash.service
/bin/systemctl start logstash.service

/bin/systemctl enable kibana.service
/bin/systemctl start kibana.service

/bin/systemctl enable nginx.service
/bin/systemctl start nginx.service

