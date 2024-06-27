from datetime import datetime
import re

SOURCE_QUERY = "ark_ssi:*"
HYRAX_SUFFIX = re.compile(r"_(te|s|b|dt)s?i?m?$")


def get_id(record: dict) -> str:
    return f"https://digital.library.ucla.edu/catalog/{record['ark_ssi']}"


def map_record(record: dict) -> dict:
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