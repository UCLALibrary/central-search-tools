SOURCE_QUERY = "ark_ssi:*"


def get_id(record: dict) -> str:
    return f"https://digital.library.ucla.edu/catalog/{record['ark_ssi']}"


def map_record(record: dict) -> dict:
    # These fields should not be included in the output record.
    fields_to_remove = [
        "_version_",
        "accessControl_ssim",
        "accessTo_ssim",
        "admin_set_sim",
        "admin_set_tesim",
        "bytes_lts",
        "collection_type_gid_ssim",
        "date_dtsim",
        "date_modified_dtsi",
        "date_uploaded_dtsi",
        "depositor_ssim",
        "depositor_tesim",
        "discover_access_group_ssim",
        "edit_access_group_ssim",
        "edit_access_person_ssim",
        "file_set_ids",
        "hasRelatedImage_ssim",
        "hasRelatedMediaFragment_ssim",
        "hashed_id_ssi",
        "member_ids_ssim",
        "nesting_collection__ancestors_ssim",
        "nesting_collection__deepest_nested_depth_isi",
        "nesting_collection__parent_ids_ssim",
        "nesting_collection__pathnames_ssim",
        "ordered_targets_ssim",
        "proxyFor_ssim",
        "proxy_in_ssi",
        "read_access_group_ssim",
        "recalculate_size_bsi",
        "score",
        "suppressed_bsi",
        "system_create_dtsi",
        "system_modified_dtsi",
        "timestamp",
        "ursus_id_ssie",
    ]
    # These fields should be duplicated with new names in the output record.
    fields_to_duplicate = {
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
    }

    output_record = {}
    for key, value in record.items():
        # Skip unwanted fields.
        if key in fields_to_remove:
            continue
        # Copy existing fields.
        output_record[key] = value
        # Duplicate fields with new names.
        if key in fields_to_duplicate.keys():
            new_key = fields_to_duplicate[key]
            output_record[new_key] = value

    # Add "names" field for (some) consistency with other sources,
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
    names = [name for field in tmp_names if field for name in field]
    if names:
        output_record["names"] = names

    # add fields for url and source
    output_record["url"] = (
        f"https://digital.library.ucla.edu/catalog/{output_record['ark_ssi']}"
    )
    output_record["source"] = "Ursus"
    return output_record
