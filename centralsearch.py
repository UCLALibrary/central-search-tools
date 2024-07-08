#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert UCLA Library CSV files for Ursus, our Blacklight installation."""

from importlib import import_module
from numbers import Number

import click
from retry.api import retry_call
import rich.progress
from pysolr import Solr  # type: ignore
from elasticsearch import Elasticsearch
from pprint import pprint


@click.group()
def centralsearch():
    pass


@click.option("--max-records", default=float("inf"))
@click.option("--source-url", required=True, help="Solr URL")
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
@centralsearch.command("copy")
def copy(
    source_url: str,
    destination_index_name: str,
    max_records: Number,
    elastic_url: str,
    elastic_api_key: str | None,
    profile: str | None,
):
    """Copy records from a Solr index to the central Elasticsearch index."""

    profile_module = import_module(profile) if profile else None
    get_id = getattr(profile_module, "get_id", lambda x: x["id"])
    map_record = getattr(profile_module, "map_record", lambda x: x)
    source_query = getattr(profile_module, "SOURCE_QUERY", "*:*")

    # TODO: click has a built-in progress bar; and I think pysolr can handle
    # chunking if we just iterate over a Results object
    with rich.progress.Progress() as progress:
        task = progress.add_task("Copying...", total=None)
        es_client = Elasticsearch(
            hosts=[elastic_url],
            verify_certs=True,
            api_key=elastic_api_key,
        )

        source_solr = Solr(source_url, timeout=10, always_commit=True)

        n_hits = float("inf")
        start = 0
        chunk_size = 250
        while start < n_hits and start < max_records:
            chunk = retry_call(
                source_solr.search,
                fargs=[source_query],
                fkwargs={"defType": "lucene", "start": start, "rows": chunk_size},
            )
            n_hits = chunk.hits

            # TODO: combine these into a single bulk request
            for index, doc in enumerate(chunk.docs):
                try:
                    retry_call(
                        es_client.index,
                        fkwargs={
                            "index": destination_index_name,
                            "document": map_record(doc),
                            "id": get_id(doc),
                        },
                        delay=0.5,
                        backoff=2,
                        max_delay=60 * 5,  # 5 min
                    )
                except Exception as e:
                    print(e)
                progress.update(task, total=n_hits, completed=start + index)

            start += chunk_size


@click.option("--source-url", required=True, help="Solr URL")
@centralsearch.command("get_solr_fields")
def get_solr_fields(source_url: str) -> None:
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
                source_query, defType="lucene", start=start, rows=chunk_size
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
