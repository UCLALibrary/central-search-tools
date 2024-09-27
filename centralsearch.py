from importlib import import_module
from numbers import Number
from typing import Generator, Any

import click
import rich.progress
from pysolr import Solr  # type: ignore
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
from datasources import DataverseSearch, SolrSearch, FronteraSearch
from pprint import pprint


@click.group()
def centralsearch():
    pass


@click.option(
    "--source-url",
    required=True,
    help="Solr URL. Can contain username and password "
    + "(e.g. https://[username]:[password]@solr.url/",
)
@click.option(
    "--source-type",
    default="solr",
    help="Type of data source; defaults to solr",
    type=click.Choice(["solr", "dataverse", "frontera"], case_sensitive=False),
)
@click.option(
    "--elastic-url",
    required=True,
    help="Elasticsearch URL. Can include username and password "
    + "(e.g. https://[username]:[password]@elastic.url/",
)
@click.option(
    "--elastic-api-key",
    default=None,
    help="API key for Elasticsearch",
)
@click.option("--destination-index-name", required=True)
@click.option("--profile", required=False)
@click.option("--max-records", default=999_999_999)
@click.option(
    "--def-type",
    default="lucene",
    help="Solr defType; defaults to lucene",
    type=click.Choice(["lucene", "dismax", "edismax"], case_sensitive=False),
)
@centralsearch.command("copy")
def copy(
    source_url: str,
    source_type: str,
    destination_index_name: str,
    max_records: Number,
    elastic_url: str,
    elastic_api_key: str | None,
    profile: str | None,
    def_type: str | None,
):
    """Copy records from a source index to the central Elasticsearch index."""

    profile_module = import_module(profile) if profile else None
    get_id = getattr(profile_module, "get_id", lambda x: x["id"])
    map_record = getattr(profile_module, "map_record", lambda x: x)
    source_query = getattr(profile_module, "SOURCE_QUERY", "*:*")

    def _generate_docs(results: Generator) -> Generator[dict, Any, Any]:
        """Generator for use by Elasticsearch's streaming_bulk."""
        for doc in results:
            es_doc = map_record(doc)
            # Explicitly set _id as that can't be done per record via streaming_bulk.
            es_doc["_id"] = get_id(doc)
            yield es_doc

    if source_type == "solr":
        searcher = SolrSearch(source_url)
    elif source_type == "dataverse":
        searcher = DataverseSearch(source_url)
    elif source_type == "frontera":
        searcher = FronteraSearch(source_url)
    else:
        raise (NotImplementedError(f"Unsupported {source_type=}"))

    rows_per_batch = 1000
    results = searcher.search(
        source_query,
        rows_per_batch=rows_per_batch,
        max_records=max_records,
        def_type=def_type,
    )

    es_client = Elasticsearch(
        hosts=[elastic_url],
        verify_certs=True,
        api_key=elastic_api_key,
    )

    # Load documents into Elasticsearch in bulk, via a generator:
    # https://elasticsearch-py.readthedocs.io/en/7.x/helpers.html
    completed = 0
    for ok, action in streaming_bulk(
        client=es_client,
        index=destination_index_name,
        actions=_generate_docs(results),
        chunk_size=rows_per_batch,
        max_retries=5,
        initial_backoff=2,
        max_backoff=60,
        request_timeout=30,
    ):
        completed += ok
        total = min(searcher.hits, max_records)
        if (completed % rows_per_batch == 0) or (completed == total):
            print(f"{completed} / {total}")


@click.option("--source-url", required=True, help="Solr URL")
@click.option(
    "--def-type",
    default="lucene",
    help="Solr defType; defaults to lucene",
    type=click.Choice(["lucene", "dismax", "edismax"], case_sensitive=False),
)
@centralsearch.command("get_solr_fields")
def get_solr_fields(source_url: str, def_type: str) -> None:
    """List all fields in all records of a Solr index,
    along with the number of times they occur."""
    with rich.progress.Progress() as progress:
        task = progress.add_task("Getting fields...", total=None)
        source_solr = Solr(source_url, timeout=10, always_commit=True)
        source_query = "*:*"
        n_hits = float("inf")
        max_records = float("inf")
        start = 0
        chunk_size = 250
        all_keys = {}
        while start < n_hits and start < max_records:
            chunk = source_solr.search(
                source_query, defType=def_type, start=start, rows=chunk_size
            )
            n_hits = chunk.hits
            for doc in chunk.docs:
                for key in doc.keys():
                    if key in all_keys.keys():
                        all_keys[key] = all_keys[key] + 1
                    else:
                        all_keys[key] = 1
            progress.update(task, total=n_hits, completed=start + chunk_size)
            start += chunk_size

        pprint(dict(sorted(all_keys.items())), width=132)


if __name__ == "__main__":
    centralsearch()  # pylint: disable=no-value-for-parameter
