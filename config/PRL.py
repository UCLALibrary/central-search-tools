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

    # add new field for source
    output_record["source"] = "PRL"

    return output_record
