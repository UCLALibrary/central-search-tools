import requests
from abc import ABC, abstractmethod
from typing import Any, Generator
from pysolr import Solr
from retry.api import retry_call


class BaseSearch(ABC):
    @property
    @abstractmethod
    def hits(self) -> int: ...

    @abstractmethod
    def search(
        self, query: str, rows_per_batch: int = 1000, max_records: int = 999_999_999
    ) -> Generator[dict, Any, Any]: ...


class DataverseSearch(BaseSearch):
    def __init__(self, source_url: str):
        self.source_url = source_url
        self._hits: int = 0

    @property
    def hits(self) -> int:
        # This will be the initial 0 until search results
        # start being evaluated by the caller.
        return self._hits

    def search(
        self, query: str, rows_per_batch: int = 1000, max_records: int = 999_999_999
    ) -> Generator[dict, Any, Any]:
        # Add a hard limit to published records only.
        query += "&publicationStatus:Published"
        # Minimal valid response looks like this:
        # {
        #     "status": "OK",
        #     "data": {
        #         "q": "*",
        #         "total_count": 0,
        #         "start": 0,
        #         "spelling_alternatives": {},
        #         "items": [],
        #         "count_in_response": 0,
        #     },
        # }

        # TODO: Error handling
        # Don't fetch more records per batch than max wanted.
        rows_per_batch = min(rows_per_batch, max_records)
        # Initialize the loop
        start = 0
        self._hits = max_records
        while start < self._hits and start < max_records:
            # Make sure final batch does not exceed max wanted.
            if start + rows_per_batch > max_records:
                rows_per_batch = max_records - start

            query_url = (
                f"{self.source_url}?q={query}&start={start}&per_page={rows_per_batch}"
            )

            results = retry_call(requests.get, fargs=[query_url])
            data = results.json().get("data")
            self._hits = data.get("total_count")
            start += rows_per_batch

            for doc in data.get("items"):
                yield doc


class SolrSearch(BaseSearch):
    def __init__(self, source_url: str):
        self.source_url = source_url
        self._hits: int = 0

    @property
    def hits(self) -> int:
        # This will be the initial 0 until search results
        # start being evaluated by the caller.
        return self._hits

    def search(
        self, query: str, rows_per_batch: int = 1000, max_records: int = 999_999_999
    ) -> Generator[dict, Any, Any]:
        solr_client = Solr(self.source_url, timeout=10)

        # Don't fetch more records per batch than max wanted.
        rows_per_batch = min(rows_per_batch, max_records)
        # Initialize the loop
        start = 0
        self._hits = max_records
        while start < self._hits and start < max_records:
            # Make sure final batch does not exceed max wanted.
            if start + rows_per_batch > max_records:
                rows_per_batch = max_records - start

            results = retry_call(
                solr_client.search,
                fargs=[query],
                fkwargs={"defType": "lucene", "start": start, "rows": rows_per_batch},
            )
            self._hits = results.hits
            start += rows_per_batch

            for doc in results.docs:
                yield doc
