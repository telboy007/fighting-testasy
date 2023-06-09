#!/usr/bin/env python

""" Parse adventure and return dict of sections to main loop """

import re
import docx  # pylint: disable=import-error
import fitz  # pylint: disable=import-error
from striprtf.striprtf import rtf_to_text  # pylint: disable=import-error


def find_matches(full_content):
    """
    Takes in a string and returns matches based on regex
    Returns list of matches
    """
    # setup internal settings
    section_regex = r"(\d+)\n((?:(?!^\d+$).)*)"

    # Return all matching entries in a list
    return re.findall(section_regex, full_content, re.DOTALL | re.MULTILINE)


def parse_input_file(input_file_path, config):
    """
    Takes input file and based on settings extracts text
    Returns dict of adventure's sections
    """
    # setup internal settings
    full_content = ""
    entries = {}

    # extract necessary config settings
    insert_zero = config["insert_zero"]
    page_dimensions = config["page_dimensions"]
    next_section_text = config["link_text"]

    if input_file_path.split(".")[-1] in ["txt"]:
        with open(input_file_path, "r", encoding="utf-8") as input_file:
            full_content = input_file.read()
            print(full_content)
    elif input_file_path.split(".")[-1] in ["doc", "docx"]:
        doc = docx.Document(input_file_path)
        for para in doc.paragraphs:
            full_content += para.text + "\n"
    elif input_file_path.split(".")[-1] in ["rtf"]:
        with open(input_file_path, "r", encoding="utf-8") as input_file:
            full_content += rtf_to_text(input_file.read())
    elif input_file_path.split(".")[-1] in ["pdf", ".pb2", ".pb2.xml", "epub"]:
        with fitz.open(input_file_path) as doc:
            for page in doc:
                # fitz.Rect(0, 0, 612, 792) uses points not px
                full_content += page.get_text("text", clip=fitz.Rect(page_dimensions))
    else:
        raise SystemError("File format not recognised!")

    if insert_zero:
        full_content = "0\n" + full_content

    # process found matches and populate dictionary
    for match in find_matches(full_content):
        section = match[0]
        desc = " ".join(match[1].split("\n"))
        exits = re.findall(
            rf'(?:{("|").join(next_section_text)})(\d+)', match[1], re.IGNORECASE
        )
        entries[section] = {
            "section": section,
            "desc": desc.replace("’", "'").replace("“", '"').replace("”", '"'),
            "exits": exits,
        }

    return entries
