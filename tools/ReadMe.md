## process_*.py

简单的添加进入数据库，不处理model、reaction和metabolite之间的关系

### 使用方式

```bash
python ../bigg_database/manage.py shell < process_*.py
```

## link_*_*.py

处理model、reaction和metabolite之间的关系，处理through类

### 使用方式

```bash
python ../bigg_database/manage.py shell < link_*_*.py
```

## clean_up.sh (*deprecated*)

删除数据库，并重新创建（不会再次makemigration）

测试时若需要刷新数据库，建议：

```shell
python manage.py flush
```

