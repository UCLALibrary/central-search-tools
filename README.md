# Central Search Tools

Command-line tools for working with Solr and Elasticsearch indexes.

Build (first time) / rebuild (as needed):

`docker-compose build`

## Local experimentation

The full local environment can be used for experimenting, with local copies of
* Python (version 3.11), with required packages
* Solr (version 7.4), with some UCLA-specific indexes
* Elasticsearch (version 7.17.19)
* Kibana (version 7.17.19)

To run the full system locally:

`docker-compose -f docker-compose_LOCAL.yml up -d`

This provides 2 Solr indexes:
* http://localhost:8983/solr/#/sinai (742 documents)
* http://localhost:8983/solr/#/ursus (80,297 documents)

Elasticsearch
* http://localhost:9200/

Kibana, for easier exploration of Elasticsearch indexes
* http://localhost:5601/app/dev_tools#/console

### Command-line tools

The command-line tool for working with data is `centralsearch.py`.  Currently, it has only
one function, copying data from Solr to Elasticsearch; more may be added later.

The easiest way to work with it is to open a dockerized python environment,
then run commands within that environment.

#### Open python console using the full local environment

`docker-compose -f docker-compose_LOCAL.yml run python bash`

#### List commands

`python ./centralsearch.py`

#### Get help for a command

`python ./centralsearch.py copy --help`

#### Copy data from the local Sinai Solr index to local Elasticsearch
```
python centralsearch.py copy \
    --source-url http://localhost:8983/solr/sinai \
    --elastic-url http://localhost:9200/ \
    --destination-index-name test-sinai \
    --profile config.samvera
```

Ignore security warnings in the local environment.

#### Review / explore data

Elasticsearch and Kibana provide the same data, but Kibana is friendlier to use via its console.

* Elasticsearch: http://localhost:9200/test-sinai/_search?pretty=true
* Kibana: http://localhost:5601/app/dev_tools#/console
  * Search: GET /test-sinai/_search?pretty=true

#### Exit from the python console

`exit`

#### Shut down the local environment

`docker-compose -f docker-compose_LOCAL.yml down`

## Production use

Coming soon (TM).

For production use, only the python environment is needed, since it will run against real Solr and Elasticsearch instances.

`docker-compose run python bash`
