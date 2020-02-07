


rm ./logstash.conf
rm ./filebeat.yml
cp ./logstash.conf.template  ./logstash.conf
cp ./filebeat.yml.template ./filebeat.yml

logstash_conf=./logstash.conf
filebeat_conf=./filebeat.yml

#echo '-------------------logstash conf  before'
#cat ${logstash_conf}
#echo '-------------------filebeat conf before'
#cat ${filebeat_conf}
#vpc-cdk-es-demo-w2a7o4s272gfzo2f3rn5mrlycu.cn-northwest-1.es.amazonaws.com.cn cn-northwest-1 /home/ec2-user/web-app/* log_index


sed -i "" "s@_ES_URL_@$1@g"  ${logstash_conf}
sed -i "" "s@_ES_AK_@${_ES_AK_}@g"  ${logstash_conf}
sed -i "" "s@_ES_SK_@${_ES_SK_}@g"  ${logstash_conf}
sed -i "" "s@_INDEX_NAME_@$4@g"  ${logstash_conf}
sed -i "" "s@_REGION_@$2@g"  ${logstash_conf}

sed -i "" "s@_LOG_PATH_@$3@g"  ${filebeat_conf}


echo '------------------- logstash conf  after'
cat ${logstash_conf}
echo '------------------- filebeat conf after'
cat ${filebeat_conf}



echo '-------------------start logstash------------------'
logstash -f ${logstash_conf} &


echo '-------------------start filebeat------------------'
filebeat -c ${filebeat_conf} &



