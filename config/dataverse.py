# Search for everything, with a hard limit to published records only.
# https://guides.dataverse.org/en/latest/api/search.html
SOURCE_QUERY = "*&publicationStatus:Published"


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
        "name": "titles",
        "publisher": "publishers",
        "description": "descriptions",
        "subjects": "subjects",
        "keywords": "keywords",
    }

    output_record = {}
    for fld in fields_to_keep.keys():
        if fld in record:
            output_record[fields_to_keep[fld]] = record[fld]

    # Make each of these fields a list, consistent with other sources.
    for field in ["descriptions", "publishers", "titles"]:
        if field in output_record:
            output_record[field] = [output_record[field]]

    # Add new field for source
    output_record["source"] = "Dataverse"

    return output_record
