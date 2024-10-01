source_query = "*:*"


def get_id(record: dict) -> str:
    return record.get("id")


def map_record(record: dict) -> dict:
    fields_to_keep = {
        "id": "id",
        "ss_title": "titles",
        "content": "content",
        "ss_type": "types",
        "ss_field_recording_artist_name_string": "recording_artist",
        "ss_field_recording_composer_string": "composer",
    }

    output_record = {}
    for fld in fields_to_keep.keys():
        if fld in record:
            output_record[fields_to_keep[fld]] = record[fld]

    # Make each of these fields a list, consistent with other sources.
    for field in ["titles", "types"]:
        if field in output_record:
            output_record[field] = [output_record[field]]

    # Add names for (some) consistency with other sources,
    # but keep separate fields as well for distinction.
    # None of these names is guaranteed to exist, so create names
    # only when at least one does.
    tmp_names = [
        output_record.get("recording_artist"),
        output_record.get("composer"),
    ]
    output_record["names"] = [name for name in tmp_names if name is not None]

    # URL isn't in original metadata, but we can construct it
    id = record.get("id")
    id_number = id.split("-")[-1]
    output_record["url"] = f"https://frontera.library.ucla.edu/node/{id_number}"

    # add new field for source
    output_record["source"] = "Frontera"

    return output_record
