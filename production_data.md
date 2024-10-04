# Commands for production data harvests
Below are the commands to harvest production Solr data into production Elasticsearch indexes.
Environment variables are set via files loaded in the relevant `docker-compose*.yml` files.

For local data review:
* See `README.md` for examples, or if using commands from below:
  * `docker compose -f docker-compose_ES_ONLY.yml up -d`
  * Wait for Elasticsearch & Kibana to be ready (`docker compose -f docker-compose_ES_ONLY.yml logs -f`)
  * `docker compose -f docker-compose_ES_ONLY.yml run python bash`
  * `export ELASTIC_URL="http://elastic:9200/"`
  * `ELASTIC_API_KEY` is not set, and the commands below will work fine as-is.

## Harvested systems

### Dataverse
```
python centralsearch.py copy \
--source-url https://dataverse.ucla.edu/api/search \
--source-type dataverse \
--elastic-url "${ELASTIC_URL}" \
--elastic-api-key "${ELASTIC_API_KEY}" \
--destination-index-name systems-index-dataverse \
--profile config.dataverse
```

### Frontera
```
python centralsearch.py copy \
--source-url https://"${FRONTERA_USER}:${FRONTERA_PASS}"@frontera.library.ucla.edu/solr-proxy \
--source-type frontera \
--elastic-url "${ELASTIC_URL}" \
--elastic-api-key "${ELASTIC_API_KEY}" \
--destination-index-name systems-index-frontera \
--profile config.frontera
```

### Oral History
This requires remote HTTPS/TLS tunneling setup as per https://uclalibrary.atlassian.net/wiki/x/1gOWGg
```
python centralsearch.py copy \
--source-url https://"${OH_USER}:${OH_PASS}"@oralhistory-solr.library.ucla.edu:8983/solr/blacklight-core/ \
--source-type solr \
--elastic-url "${ELASTIC_URL}" \
--elastic-api-key "${ELASTIC_API_KEY}" \
--destination-index-name systems-index-oralhistory \
--profile config.oralhistory
```

### PRL
```
python centralsearch.py copy \
--source-url https://p-u-prlsolr01.library.ucla.edu/solr/prl/ \
--source-type solr \
--elastic-url "${ELASTIC_URL}" \
--elastic-api-key "${ELASTIC_API_KEY}" \
--destination-index-name systems-index-prl \
--profile config.PRL
```

### Sheet Music
```
python centralsearch.py copy \
--source-url https://p-u-sheetmusicsolr01.library.ucla.edu/solr/sheetmusicprod/ \
--source-type solr \
--elastic-url "${ELASTIC_URL}" \
--elastic-api-key "${ELASTIC_API_KEY}" \
--destination-index-name systems-index-sheetmusic \
--profile config.sheet_music
```

### Sinai Manuscripts
Assumes HTTP tunnel to `p-u-sinaimanuscriptssolr01.library.ucla.edu`
```
python centralsearch.py copy \
--source-url http://host.docker.internal:8983/solr/sinaimanu/ \
--source-type solr \
--elastic-url "${ELASTIC_URL}" \
--elastic-api-key "${ELASTIC_API_KEY}" \
--destination-index-name systems-index-sinai-manuscripts \
--profile config.samvera
```

### Ursus
Assumes HTTP tunnel to `p-u-calursussolrmaster01.library.ucla.edu`
```
python centralsearch.py copy \
--source-url http://host.docker.internal:8983/solr/calursus/ \
--source-type solr \
--elastic-url "${ELASTIC_URL}" \
--elastic-api-key "${ELASTIC_API_KEY}" \
--destination-index-name systems-index-calursus \
--profile config.samvera
```

## Systems which will not be harvested
These are included just for completeness.  They will not work as-is.

### DL Legacy
Data is already in Ursus, or will soon be copied into Ursus Solr.
`config.dl_legacy.py` has been deleted.
```
python centralsearch.py copy \
--source-url https://dl.library.ucla.edu/solr/ \
--source-type solr \
--elastic-url "${ELASTIC_URL}" \
--elastic-api-key "${ELASTIC_API_KEY}" \
--destination-index-name systems-index-dl-legacy \
--profile config.dl_legacy
```

### Sinai Palimpsests
Data is not relevant, and/or is already in Sinai Manuscripts collection.
`config.sinai_palimpsests.py` has been deleted.
```
python centralsearch.py copy \
--source-url https://p-u-sinaipalimpsolr01.library.ucla.edu:8983/solr/sinaimetaprod/ \
--source-type solr \
--elastic-url "${ELASTIC_URL}" \
--elastic-api-key "${ELASTIC_API_KEY}" \
--destination-index-name systems-index-sinai-palimpsests \
--profile config.sinai_palimpsests
```