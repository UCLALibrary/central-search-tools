SOURCE_QUERY = "*:*"


def get_id(record: dict) -> str:
    return record.get("id")


def map_record(record: dict) -> dict:

    # only take a selection of fields for now
    # use the "keyword" version of fields since these are deduped
    fields_to_keep = [
        "id",
        "title_keyword",
        "publisher_keyword",
        "subjectTopic_keyword",
        "nameNamePart_keyword",
        "url_keyword",
    ]
    keep_record = {}
    for fld in fields_to_keep:
        if fld in record:
            keep_record[fld] = record[fld]

    # rename fields for consistency
    output_record = {}
    output_record["id"] = keep_record["id"]
    output_record["title"] = keep_record["title_keyword"]
    output_record["publisher"] = keep_record["publisher_keyword"]
    output_record["subject"] = keep_record["subjectTopic_keyword"]
    output_record["name"] = keep_record["nameNamePart_keyword"]
    output_record["url"] = keep_record["url_keyword"]

    # URL for MODS record isn't in original metadata, but we can construct it
    output_record["mods_url"] = (
        "https://static.library.ucla.edu/sheetmusic/mods/"
        + f"{record['collectionKey'][0]}/{record['id']}"
    )
    # add new field for source
    output_record["source"] = "Sheet Music"

    return output_record
