# 操作步骤

--------------------------------
LogStash
=============================================


###  安装LogStash

[官网安装地址](https://www.elastic.co/guide/en/logstash/current/installing-logstash.html)

```shell 

#Mac
brew tap elastic/tap
brew install elastic/tap/logstash-full

#YUM
sudo yum install logstash


#APT
sudo apt-get install logstash
```


###  测试LogStash

step1.conf  一个简单读取输入， 用json 格式输出
```
cat ./data_step1.txt | logstash -f step1.conf
```

###  测试grok

将文本 转换成json 格式

```
head  -n 2 ./data_step2.txt | logstash -f step2.conf
```



###  启动AWS ES 集群

[官方安装教程](https://docs.aws.amazon.com/zh_cn/elasticsearch-service/latest/developerguide/es-gsg-create-domain.html)
[https://aws.amazon.com/cn/premiumsupport/knowledge-center/cloudfront-logs-elasticsearch/](https://aws.amazon.com/cn/premiumsupport/knowledge-center/cloudfront-logs-elasticsearch/)


启动成功以后会生成 ES 和 Kibana 访问地址。 

###  将数据导入到ES

配置Elasticsearch

```
head  -n 2 ./data_step2.txt | logstash -f step3.conf
```

```
  amazon_es {
      hosts => ["es_host_url"]
      region => "cn-northwest-1"
      aws_access_key_id => 'AK'
      aws_secret_access_key => 'SK'
      index => "index_demo"
  }
```

###  安装FileBeat
[官方安装地址](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-installation.html)

```
filebeat -c filebeat.yml

head  -n 2 ./data_step2.txt | logstash -f step4.conf
```

分别启动filebeat 和 logstash 后， 打开data_step2.txt 文件， 复制几行新内容， 可以看到新加的数据导入到ES集群中。 



------------------------------------------

# FAQ

> 1.  Logstash could not be started because there is already another instance using the configured data directory.  If you wish to run multiple instances, you must change the "path.data" setting.

  需要kill 现在的logstash 进程， 或者配置path.data， 新启动一个logstash 进程。 
   
  
   
   
