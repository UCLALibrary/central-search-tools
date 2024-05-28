#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert UCLA Library CSV files for Ursus, our Blacklight installation."""

from datetime import datetime
from numbers import Number
import os
import re
import typing

import click
from retry.api import retry_call
import rich.progress
from pysolr import Solr  # type: ignore
from elasticsearch import Elasticsearch


# Custom Types

Record = typing.Dict[str, typing.Any]


@click.group()
def centralsearch():
    pass


@click.option("--max-records", default=float("inf"))
@click.option("--source-url", required=True)
@click.option(
    "--source-query",
    default="*:*",
    help="Solr query to select records for copying."
    + "The default value will copy all records.",
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
    help="API key for Elasticsearch. Untested, I've been using username and password in --elastic-url.",
)
@click.option("--destination-index-name", required=True)
@centralsearch.command("copy")
def copy(
    source_url: str,
    source_query: str,
    destination_index_name: str,
    max_records: Number,
    elastic_url: str,
    elastic_api_key: str | None,
):
    """Copy records from a Solr index to the central Elasticsearch index."""

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


# TODO: Move to a per-source config file
def get_id(record: Record) -> Record:
    return record["ark_ssi"]


HYRAX_SUFFIX = re.compile(r"_(te|s|b|dt)s?i?m?$")


def map_record(record: Record) -> Record:
    """Strip hyrax suffixes from field names."""

    if record.get("date_dtsim"):
        record["date_dtsim"] = [
            d for d in record["date_dtsim"] if isinstance(d, datetime)
        ]

    # remove unwanted fields
    for k in [
        "accessControl",
        "id",
        "score",
        "system_create",
        "system_modified",
        "timestamp",
    ]:
        record.pop(k) if k in record else None

    # add fields for url and source
    record["url"] = f"https://digital.library.ucla.edu/catalog/{record['ark_ssi']}"
    record["source"] = "Californica"

    return {HYRAX_SUFFIX.sub("", key): value for (key, value) in record.items()}


if __name__ == "__main__":
    centralsearch()  # pylint: disable=no-value-for-parameter
