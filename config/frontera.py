source_query = "*:*"


def get_id(record: dict) -> str:
    return record.get("id")


def map_record(record: dict) -> dict:
    fields_to_keep = {
        "id": "id",
        "ss_title": "title",
        "content": "description",
        "ss_type": "type",
        "ss_field_recording_artist_name_string": "recording_artist_name",
        "ss_field_composer_string": "composer",
    }

    output_record = {}
    for fld in fields_to_keep.keys():
        if fld in record:
            output_record[fields_to_keep[fld]] = record[fld]

    # URL isn't in original metadata, but we can construct it
    id = record.get("id")
    id_number = id.split("-")[-1]
    output_record["url"] = f"https://frontera.library.ucla.edu/node/{id_number}"

    # add new field for source
    output_record["source"] = "Frontera"

    return output_record
