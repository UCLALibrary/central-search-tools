SOURCE_QUERY = "*"


def get_id(record: dict) -> str:
    # Only type=dataverse seems to have reliable "identifier" field;
    # use url field for now.
    return record.get("url")


def map_record(record: dict) -> dict:
    # Only take a selection of fields for now;
    # rename fields for consistency.
    fields_to_keep = {
        "id": "id",
        "type": "type",
        "url": "url",
        "name": "title",
        "publisher": "publisher",
        "description": "description",
        "subjects": "subjects",
        "keywords": "keywords",
    }

    output_record = {}
    for fld in fields_to_keep.keys():
        if fld in record:
            output_record[fields_to_keep[fld]] = record[fld]

    # Add new field for source
    output_record["source"] = "Dataverse"

    return output_record
