#!/usr/bin/env python

""" Import config and return values """

import json


def import_config(config_file_path):
    """import config file"""
    with open(config_file_path, "r", encoding="utf-8") as jsonfile:
        config = json.load(jsonfile)

    # update link text config settings to be more regex-y
    next_section_text = []
    for link_text in config["link_text"]:
        next_section_text.append(link_text.replace(" ", r"\s*"))

    config["link_text"] = next_section_text

    return config
