#!/usr/bin/env python

""" Parse adventure and return dict of sections to main loop """

import re
import fitz # pylint: disable=import-error


def find_matches(full_content):
    """
        Takes in a tring and returns matches based on regex
        Returns a list
    """
    # setup internal settings
    section_regex = r'(\d+)\n((?:(?!^\d+$).)*)'

    # Find all matching entries in the text
    matches = re.findall(section_regex, full_content, re.DOTALL | re.MULTILINE)

    return matches


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

    with fitz.open(input_file_path) as doc:
        for page in doc:
            # for letter = fitz.Rect(0, 0, 612, 792)
            text_container = fitz.Rect(page_dimensions)
            full_content += page.get_text("text", clip=text_container)

        if insert_zero:
            full_content = "0\n" + full_content

        # get matches
        matches = find_matches(full_content)

        # Process the matches and populate the dictionary
        for match in matches:
            section = match[0]
            desc = ' '.join(match[1].split('\n'))
            exits = re.findall(fr'(?:{("|").join(next_section_text)})(\d+)', match[1], re.IGNORECASE) # pylint: disable=line-too-long
            entries[section] = {
                'section': section,
                'desc': desc.replace("’", "'").replace('“', '"').replace('”', '"'),
                'exits': exits
            }

        return entries
