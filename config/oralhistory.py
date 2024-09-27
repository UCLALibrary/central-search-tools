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
    # add subtitle_display if it exists.
    # Either way, make titles a list.
    if "titles" in output_record:
        output_record["titles"] = [output_record["titles"]]
    if "subtitle_display" in record:
        output_record["titles"].append(record["subtitle_display"])

    # Make names a list, and add interviewee_display if it exists.
    if "names" in output_record:
        output_record["names"] = [output_record["names"]]
        if "interviewee_display" in record:
            output_record["names"].append(record["interviewee_display"])

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
