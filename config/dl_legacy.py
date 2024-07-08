SOURCE_QUERY = "*:*"


def get_id(record: dict) -> str:
    return record.get("PID")


def map_record(record: dict) -> dict:
    # Still quite TBD....
    # Remove Solr fields we don't want
    # RELS_EXT*
    # _version_
    # fedora_*
    # All fgs_* except fgs_label_s
    # All mods_* except mods_titleInfo_title_s and mods_xml
    # timestamp

    # Easiest just to keep what we do want, for now
    fields_to_keep = [
        "PID",
        "fgs_label_s",
        "mods_titleInfo_title_s",
        "mods_title_ms",
        "mods_xml",
    ]
    record_keep = {}
    for fld in fields_to_keep:
        if fld in record:
            record_keep[fld] = record[fld]

    # Also keep all Dublin Core fields (dc.*)
    record_keep.update({k: v for k, v in record.items() if k.startswith("dc.")})

    return record_keep
