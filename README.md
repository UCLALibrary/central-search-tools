# Central Search Tools

Command-line tools for working with Solr and Elasticsearch indexes.

Build (first time) / rebuild (as needed):

`docker compose build`

## Local experimentation

The full local environment can be used for experimenting, with local copies of
* Python (version 3.11), with required packages
* Solr (version 7.4), with some UCLA-specific indexes
* Elasticsearch (version 7.17.19)
* Kibana (version 7.17.19)

To run the full system locally:

`docker-compose -f docker-compose_FULL.yml up -d`

This provides 2 Solr indexes:
* http://localhost:8983/solr/#/sinai (742 documents)
* http://localhost:8983/solr/#/ursus (80,297 documents)

Elasticsearch
* http://localhost:9200/

Kibana, for easier exploration of Elasticsearch indexes
* http://localhost:5601/app/dev_tools#/console

For an alternative, with local Elasticsearch and Kibana but no local Solr:

`docker-compose -f docker-compose_ES_ONLY.yml up -d`

### Command-line tools

The command-line tool for working with data is `centralsearch.py`.  Its main purpose is to copy data
from Solr to Elasticsearch, but it has other commands - see below for more.

The easiest way to work with it is to open a dockerized python environment,
then run commands within that environment.

Command-line examples below all assume you are running commands within Docker.
If running in a virtual environment instead, URLs may need to be changed to use `localhost`.

#### Open python console using the full local environment

`docker-compose -f docker-compose_FULL.yml run python bash` or `docker-compose -f docker-compose_ES_ONLY.yml run python bash`

#### List commands

`python ./centralsearch.py`

#### Get help for a command

`python ./centralsearch.py copy --help`

#### Copy data from the local Sinai Solr index to local Elasticsearch
```
python centralsearch.py copy \
--source-url http://solr:8983/solr/sinai \
--elastic-url http://elastic:9200/ \
--destination-index-name test-sinai \
--profile config.samvera
```

#### Copy 150 records from remote Datasearch index to local Elasticsearch
```
python centralsearch.py copy \
--source-url https://dataverse.ucla.edu/api/search \
--source-type dataverse \
--elastic-url http://elastic:9200/ \
--destination-index-name test-dataverse \
--profile config.dataverse \
--max-records 150
```

#### Copy 150 records from remote Frontera index to local Elasticsearch
```
python centralsearch.py copy \
--source-url https://USER:PASSWORD@frontera.library.ucla.edu/solr-proxy \
--source-type frontera \
--elastic-url http://elastic:9200/ \
--destination-index-name test-frontera \
--profile config.frontera \
--max-records 150
```

#### Copy 150 records from remote Oral History index to local Elasticsearch
 ```
 # Requires update to hosts file in container and on local machine
python centralsearch.py copy \
--source-url https://USER:PASSWORD@oralhistory-solr.library.ucla.edu:8982/solr/blacklight-core/ \
--source-type solr \
--elastic-url http://elastic:9200/ \
--destination-index-name test-oralhistory \
--profile config.oralhistory \
--max-records 150
```

Ignore security warnings in the local environment.

#### List fields in an index
Lists all fields in all records in an index, along with number of occurrences of each field.
Generally takes 5-15 minutes, depending on number of records.
```
python centralsearch.py get_fields --source-type [solr|dataverse|frontera] --source-url URL
```

#### Review / explore data

Elasticsearch and Kibana provide the same data, but Kibana is friendlier to use via its console.

* Elasticsearch: http://localhost:9200/test-sinai/_search?pretty=true
* Kibana: http://localhost:5601/app/dev_tools#/console
  * Search: GET /test-sinai/_search?pretty=true

#### Exit from the python console

`exit`

#### Shut down the local environment

`docker-compose -f docker-compose_FULL.yml down` or `docker-compose -f docker-compose_ES_ONLY.yml down`

## Production use

Coming soon (TM).

For production use, only the python environment is needed, since it will run against real Solr and Elasticsearch instances.

`docker compose run python bash`
