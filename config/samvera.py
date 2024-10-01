SOURCE_QUERY = "ark_ssi:*"


def get_id(record: dict) -> str:
    return f"https://digital.library.ucla.edu/catalog/{record['ark']}"


def map_record(record: dict) -> dict:
    # Only take a selection of fields for now;
    # rename fields for consistency.
    # There are MANY more fields we could consider using.
    fields_to_keep = {
        "id": "id",
        "ark_ssi": "ark",
        "title_tesim": "titles",
        "artist_tesim": "artists",
        "author_tesim": "authors",
        "composer_tesim": "composers",
        "creator_tesim": "creators",
        "director_tesim": "directors",
        "editor_tesim": "editors",
        "named_subject_tesim": "named_subjects",
        "photographer_tesim": "photographers",
        "producer_tesim": "producers",
        "program_tesim": "programs",
        "description_tesim": "descriptions",
        "publisher_tesim": "publishers",
        "subject_tesim": "subjects",
        "subject_topic_tesim": "subject_topics",
        "genre_tesim": "types",
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
        output_record.get("artists"),
        output_record.get("authors"),
        output_record.get("composers"),
        output_record.get("creators"),
        output_record.get("directors"),
        output_record.get("editors"),
        output_record.get("photographers"),
        output_record.get("producers"),
    ]
    # Each of the values in tmp_names is a list already, so add just the values
    # from each field in tmp_names.
    output_record["names"] = [name for field in tmp_names if field for name in field]

    # add fields for url and source
    output_record["url"] = (
        f"https://digital.library.ucla.edu/catalog/{output_record['ark']}"
    )
    output_record["source"] = "Ursus"
    return output_record
