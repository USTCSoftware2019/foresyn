#### haystack and elasticsearch

Due to the limit from the haystack, the version of elasticsearch must lower than 3.x

For this project, we choose elasticsearch 2.4.6

Download: [elasticsearch-2-4-6](https://www.elastic.co/cn/downloads/past-releases/elasticsearch-2-4-6)

Usage (Ubuntu): 
Install: ```sudo dpkg elasticsearch-2.4.6.deb```
Start: ```sudo service elasticsearch start```

> To start elasticsearch, java 8 is required
> Install: ```sudo apt install openjdk-8-jre-headless```

To match the version of elasticsearch, install elasticsearch-dsl using
```pip3 install "elsaticsearch>=2.0.0,<3.0.0"```