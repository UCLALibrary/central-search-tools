SOURCE_QUERY = "*:*"


def get_id(record: dict) -> str:
    return record.get("id")


def map_record(record: dict) -> dict:
    # Only take a selection of fields for now.
    # Rename fields as needed for consistency with other sources.
    fields_to_keep = {
        "id": "id",
        "title_display": "titles",
        "subject_topic_facet": "subjects",
        "author_display": "names",
        # TODO: interviewee_display - add to names, as a list?
    }

    output_record = {}
    for fld in fields_to_keep.keys():
        if fld in record:
            output_record[fields_to_keep[fld]] = record[fld]

    # Every record has title_display (now in titles);
    # for now, append subtitle_display if it exists.
    # TODO: Should titles be a list instead? (for all sources?)
    if "subtitle_display" in record:
        output_record["titles"] += f" {record['subtitle_display']}"

    # Clean up subjects, which often has duplicates in solr data.
    if "subjects" in output_record and isinstance(output_record["subjects"], list):
        output_record["subjects"] = sorted(set(output_record["subjects"]))

    # URL isn't in original metadata, but we can construct it.
    output_record["url"] = (
        f"https://oralhistory.library.ucla.edu/catalog/{get_id(record)}"
    )

    # Add new field for source.
    output_record["source"] = "Oral History"

    return output_record
