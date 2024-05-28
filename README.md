# Central Search Tools

Command-line tools for working with central Elasticsearch index.

Open with a dockerized python environment:
```docker-compose run python bash```

List commands:
```python ./centralsearch.py```

Get help for a command:
```python ./centralsearch.py copy --help```

Copy between the included test docker images:
```
python centralsearch.py copy \
    --max-records 1000 \
    --source-url http://localhost:8983/solr/ursus \
    --source-query "*:*" \
    --elastic-url "http://localhost:9200" \
    --destination-index-name systems-index-digitallibrary-ursus
```
