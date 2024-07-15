SOURCE_QUERY = "*"


def get_id(record: dict) -> str:
    return record.get("url")


def map_record(record: dict) -> dict:
    return record
