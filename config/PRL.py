SOURCE_QUERY = "*:*"


def get_id(record: dict) -> str:
    return record.get("id")


def map_record(record: dict) -> dict:

    # only take a selection of fields for now
    # rename fields for consistency
    fields_to_keep = {
        "id": "id",
        "title_keyword": "titles",
        "description_keyword": "descriptions",
        "publisher_keyword": "publishers",
        "subject_keyword": "subjects",
        "creator_keyword": "creators",
        "contributor_keyword": "contributors",
        "type_keyword": "types",
        "external_link": "url",
    }

    output_record = {}
    for fld in fields_to_keep.keys():
        if fld in record and record[fld] != [" "]:
            output_record[fields_to_keep[fld]] = record[fld]

    # Add names for (some) consistency with other sources,
    # but keep separate fields as well for distinction.
    # None of these names is guaranteed to exist, so create names
    # only when at least one does.
    tmp_names = [
        output_record.get("creators"),
        output_record.get("contributors"),
    ]
    # Each of the values in tmp_names is a list already, so add just the values
    # from each field in tmp_names.
    output_record["names"] = [name for field in tmp_names if field for name in field]

    # add new field for source
    output_record["source"] = "PRL"

    return output_record
