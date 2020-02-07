--------------------------------

# 安装Logstash + filebeat  & AMI 制作



[Logstash 官网安装地址](https://www.elastic.co/guide/en/logstash/current/installing-logstash.html)

[Filebeat 官方安装地址](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-installation.html)

[amazon_es 插件介绍](https://github.com/awslabs/logstash-output-amazon_es)

[amazon_es 插件安装](https://aws.amazon.com/cn/premiumsupport/knowledge-center/cloudfront-logs-elasticsearch/)


### 启动一个Ec2 实例用于制作AMI

[官方参考文档](https://docs.aws.amazon.com/zh_cn/AWSEC2/latest/UserGuide/creating-an-ami-ebs.html)

### 配置java （1.8以上）

### 安装步骤
```shell script

cd ~
mkdir tools
cd tools

wget https://artifacts.elastic.co/downloads/logstash/logstash-7.5.2.tar.gz
tar xzvf logstash-7.5.2.tar.gz

wget  https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.5.2-linux-x86_64.tar.gz
tar xzvf filebeat-7.5.2-linux-x86_64.tar.gz

# amazon-es 插件
cd logstash-7.5.2
bin/logstash-plugin install logstash-output-amazon_es

```

### 添加环境变量

```shell script
vim ~/.bash_profile
# 添加以下环境变量到 bash_profile 中 
  export PATH=~/tools/logstash-7.5.2/bin:$PATH
  export PATH=~/tools/filebeat-7.5.2-linux-x86_64:$PATH

source ~/.bash_profile
```


### Copy 脚本文件

将 [./logstash/server/](../logstash/server) 文件夹下面所有文件 copy到服务器上

将 [./web-demo/](../web-demo/) Springboot 项目编译， 然后将jar 上传到 Ec2上 (实际使用过程中， 可以配置CodeDeploy). 

完成测试以后，制作镜像。 



------------------------------------------------
#  LogStash 使用方法


####  测试LogStash

step1.conf  一个简单读取输入， 用json 格式输出
```
cat ./data_step1.txt | logstash -f step1.conf
```

step1.conf 文件内容， 从标准输入读取数据， 以json格式发送到标准输出上。 
```shell script

input {
  stdin { }
}
output {
  stdout {
   codec => rubydebug {}
  }
}

```
输出的示例： 
```shell script
{
       "message" => "hello",
    "@timestamp" => 2020-02-05T08:53:01.186Z,
          "host" => "localhost",
      "@version" => "1"
}
{
       "message" => "filebeat",
    "@timestamp" => 2020-02-05T08:53:01.209Z,
          "host" => "localhost",
      "@version" => "1"
}
{
       "message" => "filebeat",
    "@timestamp" => 2020-02-05T08:53:01.208Z,
          "host" => "localhost",
      "@version" => "1"
}
```




###  测试grok

将文本 转换成json 格式
[官方文档](https://www.elastic.co/guide/en/logstash/current/advanced-pipeline.html)

```
head  -n 2 ./data_step2.txt | logstash -f step2.conf
```

原始数据
```shell script
2020/01/20-20:07:29|com.xxx.yyy.service.LvBoServiceImpl~getActiveStatus~-981616682~设备标识~172.19.71.224~9999~执行成功~T~3
```

grok 转换语法
```shell script
  grok {
    match => {
       "message" => '%{TESTTIME:create_time}\|%{JAVACLASS:class_name}~%{WORD:method}~%{NUMBER:link_id:int}~%{DATA:device_id}\~%{IPORHOST:remote_ip}~%{NUMBER:error_code:int}~%{DATA:error_msg}~%{WORD:status}~%{NUMBER:use_time:int}'
    }
...... 
}

```
转换后的结果

```shell script
{
     "error_code" => 9999,
       "use_time" => 3,
       "@version" => "1",
      "remote_ip" => "172.19.71.224",
      "error_msg" => "执行成功",
         "status" => "T",
         "method" => "getActiveStatus",
        "link_id" => -981616682,
     "@timestamp" => 2020-02-05T09:06:51.625Z,
    "create_time" => 2020-01-20T12:07:29.000Z,
      "device_id" => "设备标识",
     "class_name" => "com.xxx.yyy.service.LvBoServiceImpl"
}
```



###  启动AWS ES 集群

[官方安装教程](https://docs.aws.amazon.com/zh_cn/elasticsearch-service/latest/developerguide/es-gsg-create-domain.html)
[https://aws.amazon.com/cn/premiumsupport/knowledge-center/cloudfront-logs-elasticsearch/](https://aws.amazon.com/cn/premiumsupport/knowledge-center/cloudfront-logs-elasticsearch/)

[通过CDK自动生成Elastic Search 集群](../cdk-infra/README.md)

启动成功以后会生成 ES 和 Kibana 访问地址。 

###  将数据导入到ES

配置Elasticsearch


需要配置 logstash 的 amazon_es 插件， 并且替换以下变量。 
从下面可以看出， 只要把输出从stout 替换成 es就可以。
```
output {
  stdout {
   codec => rubydebug {}
  }
  amazon_es {
      hosts => ["_ES_URL_"]
      region => "_REGION_"
      aws_access_key_id => '_ES_AK_'
      aws_secret_access_key => '_ES_SK_'
      index => "_INDEX_NAME_"
  }
 
}
```

执行以下命令， 然后到kibana 中查看

```
head  -n 2 ./data_step2.txt | logstash -f step3.conf
```




### FileBeat

[数据导入教程](https://blog.csdn.net/UbuntuTouch/article/details/100675502)



filebeat.yml 配置文件
```yaml

filebeat.inputs:
- type: log
  enabled: true
  #要监控的文件列表
  paths:
    - ./data_step2.txt

# 输出路径
output.logstash:
  hosts: ["localhost:5044"]
```

分别启动  logstash filebeat
```
logstash -f step4.conf
filebeat -c filebeat.yml
```
向 ./data_step2.txt 中添加内容， 然后观察logstash的输出




------------------------------------------------ 

# 服务器执行方式

* 将./logstash/server  文件夹内容复制到服务器上
* 添加环境变量
```shell script
export _ES_URL_='xxxxx'
export _ES_AK_='xxxxx'
export _ES_SK_='xxxxx'
export _INDEX_NAME_='xxxxx'
export _REGION_='xxxxx'
export _LOG_PATH_='xxxxx'
```

*  执行start.sh


---------------------------------------

# Kibana 使用

[官方教程](https://www.elastic.co/guide/en/kibana/7.1/tutorial-load-dataset.html)




# FAQ

* Logstash could not be started because there is already another instance using the configured data directory.  If you wish to run multiple instances, you must change the "path.data" setting.

  需要kill 现在的logstash 进程， 或者配置path.data， 新启动一个logstash 进程。 
  
  
* logstash 导入ES时, 报401错误

需要使用amazon_es插件 ，配置IAM role（推荐）或者AKSK。
   
  
   
   
