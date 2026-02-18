import requests
from abc import ABC, abstractmethod
from typing import Any, Generator
from pysolr import Solr
from retry.api import retry_call
from pprint import pprint


class BaseSearch(ABC):
    @property
    @abstractmethod
    def hits(self) -> int: ...

    @abstractmethod
    def search(
        self,
        query: str,
        rows_per_batch: int = 1000,
        max_records: int = 999_999_999,
        **kwargs,
    ) -> Generator[dict, Any, Any]: ...

    @abstractmethod
    def get_fields(self, *args, **kwargs) -> None: ...


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
        self,
        query: str,
        rows_per_batch: int = 1000,
        max_records: int = 999_999_999,
        **kwargs,
    ) -> Generator[dict, Any, Any]:
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

    def get_fields(self, *args, **kwargs):
        rows_per_batch = 1000
        max_records = 999_999_999
        query = "*&publicationStatus:Published"
        all_keys = {}
        # Initialize the loop
        start = 0
        self._hits = max_records
        while start < self._hits and start < max_records:
            # Make sure final batch does not exceed max wanted.
            if start + rows_per_batch > max_records:
                rows_per_batch = max_records - start

            query_url = (
                f"{self.source_url}?"
                f"q={query}&start={start}&per_page={rows_per_batch}"
            )
            results = retry_call(requests.get, fargs=[query_url])
            data = results.json().get("data")
            self._hits = data.get("total_count")
            start += rows_per_batch

            docs = data.get("items")
            for doc in docs:
                for key in doc.keys():
                    if key in all_keys.keys():
                        all_keys[key] = all_keys[key] + 1
                    else:
                        all_keys[key] = 1
        pprint(dict(sorted(all_keys.items())), width=132)


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
        self,
        query: str,
        rows_per_batch: int = 1000,
        max_records: int = 999_999_999,
        def_type: str = "lucene",
        **kwargs,
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
                fkwargs={"defType": def_type, "start": start, "rows": rows_per_batch},
            )
            self._hits = results.hits
            start += rows_per_batch

            for doc in results.docs:
                yield doc

    def get_fields(self, def_type: str, *args, **kwargs) -> None:
        """List all fields in all records of a Solr index,
        along with the number of times they occur."""
        source_solr = Solr(self.source_url, timeout=10, always_commit=True)
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
            start += chunk_size
        pprint(dict(sorted(all_keys.items())), width=132)


class FronteraSearch(BaseSearch):
    def __init__(self, source_url: str):
        self.source_url = source_url
        self._hits: int = 0

    @property
    def hits(self) -> int:
        # This will be the initial 0 until search results
        # start being evaluated by the caller.
        return self._hits

    def search(
        self,
        query: str,
        rows_per_batch: int = 1000,
        max_records: int = 999_999_999,
        **kwargs,
    ) -> Generator[dict, Any, Any]:

        rows_per_batch = min(rows_per_batch, max_records)
        # Initialize the loop
        start = 0
        self._hits = max_records
        while start < self._hits and start < max_records:
            # Make sure final batch does not exceed max wanted.
            if start + rows_per_batch > max_records:
                rows_per_batch = max_records - start

            query_url = (
                f"{self.source_url}?"
                f"query={query}&start={start}&rows={rows_per_batch}&wt=json"
            )
            results = retry_call(requests.get, fargs=[query_url])
            data = results.json().get("response")
            self._hits = data.get("numFound")
            start += rows_per_batch

            docs = data.get("docs")
            for doc in docs:
                yield doc

    def get_fields(self, *args, **kwargs):
        rows_per_batch = 1000
        max_records = 999_999_999
        query = "*:*"
        all_keys = {}
        # Initialize the loop
        start = 0
        self._hits = max_records
        while start < self._hits and start < max_records:
            # Make sure final batch does not exceed max wanted.
            if start + rows_per_batch > max_records:
                rows_per_batch = max_records - start

            query_url = (
                f"{self.source_url}?"
                f"query={query}&start={start}&rows={rows_per_batch}&wt=json"
            )
            results = retry_call(requests.get, fargs=[query_url])
            data = results.json().get("response")
            self._hits = data.get("numFound")
            start += rows_per_batch

            docs = data.get("docs")
            for doc in docs:
                for key in doc.keys():
                    if key in all_keys.keys():
                        all_keys[key] = all_keys[key] + 1
                    else:
                        all_keys[key] = 1
        pprint(dict(sorted(all_keys.items())), width=132)
