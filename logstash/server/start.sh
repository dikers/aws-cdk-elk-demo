#!/bin/bash
su - ec2-user <<EOF
whoami
pwd;

whoami >> /home/ec2-user/ec2-user.txt
/bin/echo "Hello World" >> /home/ec2-user/ec2-user.txt
date >> /home/ec2-user/ec2-user.txt

cd /home/ec2-user/src/server
rm /home/ec2-user/src/server/logstash.conf
rm /home/ec2-user/src/server/filebeat.yml
rm -fr /home/ec2-user/logs/*


cp /home/ec2-user/src/server/logstash.conf.template  /home/ec2-user/src/server/logstash.conf
cp /home/ec2-user/src/server/filebeat.yml.template /home/ec2-user/src/server/filebeat.yml

export logstash_con=/home/ec2-user/src/server/logstash.conf
export filebeat_conf=/home/ec2-user/src/server/filebeat.yml


echo '--------------';
echo '1 ' $1
echo '2 ' $2
echo '3 ' $3
echo '4 ' $4
echo '---------------------'

chmod 400 /home/ec2-user/src/server/logstash.conf
chmod 400 /home/ec2-user/src/server/filebeat.yml


sed -i  "s@_ES_URL_@$1@g"  /home/ec2-user/src/server/logstash.conf
sed -i  "s@_INDEX_NAME_@$4@g"  /home/ec2-user/src/server/logstash.conf
sed -i  "s@_REGION_@$2@g"  /home/ec2-user/src/server/logstash.conf

sed -i  "s@_LOG_PATH_@$3@g"  /home/ec2-user/src/server/filebeat.yml

echo '------------------- logstash conf  after'
cat /home/ec2-user/src/server/logstash.conf
echo '------------------- filebeat conf after'
cat /home/ec2-user/src/server/filebeat.yml

echo '-------------------start logstash------------------'
/home/ec2-user/tools/logstash-7.5.2/bin/logstash -f /home/ec2-user/src/server/logstash.conf > /home/ec2-user/logs/logstash.log &

echo '-------------------start filebeat------------------'
/home/ec2-user/tools/filebeat-7.5.2-linux-x86_64/filebeat -c /home/ec2-user/src/server/filebeat.yml > /home/ec2-user/logs/filebeat.log &


cd /home/ec2-user/web-app/
echo '-------------------start web ------------------'
/home/ec2-user/tools/jdk1.8.0_221/bin/java -jar /home/ec2-user/web-app/metrodemo-1.0.jar   > /home/ec2-user/logs/springboot.log  &


exit;
EOF

whoami