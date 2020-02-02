# 操作步骤

--------------------------------
LogStash
=============================================

### 配置java （1.8以上）

### 安装
```shell script

wget https://artifacts.elastic.co/downloads/logstash/logstash-7.5.2.tar.gz
tar xzvf logstash-7.5.2.tar.gz

wget  https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.5.2-linux-x86_64.tar.gz
tar xzvf filebeat-7.5.2-linux-x86_64.tar.gz

# amazon-es 插件
cd logstash-7.5.2
bin/logstash-plugin install logstash-output-amazon_es

```

### 添加环境变量
> export PATH=/home/ec2-user/tools/logstash-7.5.2/bin:$PATH
> export PATH=/home/ec2-user/tools/filebeat-7.5.2-linux-x86_64:$PATH

```shell script
vim ~/.bash_profile

source ~/.bash_profile
```





### LogStash

[官网安装地址](https://www.elastic.co/guide/en/logstash/current/installing-logstash.html)

###  测试LogStash

step1.conf  一个简单读取输入， 用json 格式输出
```
cat ./data_step1.txt | logstash -f step1.conf
```

###  测试grok

将文本 转换成json 格式

```
head  -n 2 ./data_step2.txt | logstash -f step2.conf

cat ../target/logs/metrodemo.log | logstash -f step2.conf
```



###  启动AWS ES 集群

[官方安装教程](https://docs.aws.amazon.com/zh_cn/elasticsearch-service/latest/developerguide/es-gsg-create-domain.html)
[https://aws.amazon.com/cn/premiumsupport/knowledge-center/cloudfront-logs-elasticsearch/](https://aws.amazon.com/cn/premiumsupport/knowledge-center/cloudfront-logs-elasticsearch/)


启动成功以后会生成 ES 和 Kibana 访问地址。 

###  将数据导入到ES

配置Elasticsearch


[amazon_es 插件介绍](https://github.com/awslabs/logstash-output-amazon_es)

[amazon_es 插件安装](https://aws.amazon.com/cn/premiumsupport/knowledge-center/cloudfront-logs-elasticsearch/)

```
head  -n 2 ./data_step2.txt | logstash -f step3.conf

cat ../target/logs/metrodemo.log | logstash -f step3.conf
```

```
  amazon_es {
      hosts => ["_ES_URL_"]
      region => "_REGION_"
      aws_access_key_id => '_ES_AK_'
      aws_secret_access_key => '_ES_SK_'
      index => "_INDEX_NAME_"
  }

```

### FileBeat



[官方安装地址](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-installation.html)

[数据导入教程](https://blog.csdn.net/UbuntuTouch/article/details/100675502)


```
filebeat -c filebeat.yml

head  -n 2 ./data_step2.txt | logstash -f step4.conf
```




### 执行 启动脚本
```shell script
./server/start.sh

```


###  Kibana 使用

---------------------------------------

[官方教程](https://www.elastic.co/guide/en/kibana/7.1/tutorial-load-dataset.html)




# FAQ

> 1.  Logstash could not be started because there is already another instance using the configured data directory.  If you wish to run multiple instances, you must change the "path.data" setting.

  需要kill 现在的logstash 进程， 或者配置path.data， 新启动一个logstash 进程。 
  
  
> 2. logstash 导入ES 时  报401 错误

需要适用amazon_es 插件 配置IAM role（推荐）或者AKSK。
   
  
   
   
