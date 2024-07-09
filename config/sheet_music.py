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
    output_record = {}
    for fld in fields_to_keep:
        if fld in record:
            output_record[fld] = record[fld]

    # URL for MODS record isn't in original metadata, but we can construct it
    output_record["mods_url"] = (
        "https://static.library.ucla.edu/sheetmusic/mods/"
        + f"{record['collectionKey'][0]}/{record['id']}"
    )
    # add new field for source
    output_record["source"] = "Sheet Music"

    return output_record
