SOURCE_QUERY = "*:*"


def get_id(record: dict) -> str:
    return record.get("id")


def map_record(record: dict) -> dict:

    # only take a selection of fields for now
    # rename fields for consistency
    fields_to_keep = {
        "id": "id",
        "title_tesim": "titles",
        "alternative_title_tesim": "alternative_titles",
        "descriptive_title_tesim": "descriptive_titles",
        "uniform_title_tesim": "uniform_titles",
        "contributor_tesim": "contributors",
        "contents_tesim": "contents",
        "contents_note_tesim": "contents_notes",
        "keywords_tesim": "keywords",
    }

    output_record = {}
    for fld in fields_to_keep.keys():
        if fld in record:
            output_record[fields_to_keep[fld]] = record[fld]

    # original index doesn't contain URLs, but we can construct them
    if "id" in output_record:
        # replace forward slash in ARK with URL encoded '%2F'
        ark = output_record["id"].replace("/", "%2F")
        output_record["url"] = (
            f"https://sinaimanuscripts.library.ucla.edu/catalog/{ark}"
        )
    # add new field for source
    output_record["source"] = "Sinai Palimpsests"

    return output_record
