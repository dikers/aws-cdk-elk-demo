


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


# 从环境变量里面输入
# export _ES_URL_='xxxxx'
# export _ES_AK_='xxxxx'
# export _ES_SK_='xxxxx'
# export _INDEX_NAME_='xxxxx'
# export _REGION_='xxxxx'
# export _LOG_PATH_='xxxxx'


echo '_ES_URL_' : ${_ES_URL_}
echo '_ES_AK_' : ${_ES_AK_}
echo '_ES_SK_' : ${_ES_SK_}
echo '_INDEX_NAME_' : ${_INDEX_NAME_}
echo '_REGION_' : ${_REGION_}
echo '_LOG_PATH_' : ${_LOG_PATH_}



sed -i "" "s@_ES_URL_@${_ES_URL_}@g"  ${logstash_conf}
sed -i "" "s@_ES_AK_@${_ES_AK_}@g"  ${logstash_conf}
sed -i "" "s@_ES_SK_@${_ES_SK_}@g"  ${logstash_conf}
sed -i "" "s@_INDEX_NAME_@${_INDEX_NAME_}@g"  ${logstash_conf}
sed -i "" "s@_REGION_@${_REGION_}@g"  ${logstash_conf}

sed -i "" "s@_LOG_PATH_@${_LOG_PATH_}@g"  ${filebeat_conf}


echo '------------------- logstash conf  after'
cat ${logstash_conf}
echo '------------------- filebeat conf after'
cat ${filebeat_conf}



echo '-------------------start logstash------------------'
logstash -f ${logstash_conf} &


echo '-------------------start filebeat------------------'
filebeat -c ${filebeat_conf} &



