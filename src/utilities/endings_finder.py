#!/usr/bin/env python

"""
    Finding exits since 2023
"""

import argparse
from pathlib import Path
import json
import os
import re
import fitz # pylint: disable=import-error
from jinja2 import Environment, FileSystemLoader # pylint: disable=import-error


def flatten(lis, ltypes=(list, tuple)):
    """ modified from https://code.activestate.com/recipes/363051/#c10 """
    ltype = type(lis)
    lis = list(lis)
    i = 0
    while i < len(lis):
        while isinstance(lis[i], ltypes):
            if not lis[i]:
                lis.pop(i)
                i -= 1
                break
            lis[i:i + 1] = lis[i]
        i += 1
    return ltype(lis)


# configure internal settings
PATHING_DIRECTORY = "endings-finder"

# Check if the directory exists
if not os.path.exists(PATHING_DIRECTORY):
    # If it doesn't exist, create it
    os.makedirs(PATHING_DIRECTORY)

# tidy up prior test runs
for file in Path(PATHING_DIRECTORY).glob('*.html'):
    try:
        file.unlink()
    except OSError as error:
        print(f"Error removing {file}: {error.strerror}")

# set up command line parser
parser = argparse.ArgumentParser(
                    prog = 'python endings-finder.py',
                    description = 'Finds endings (except the best ending) that can be added to the not allowed list', # pylint: disable=line-too-long
                    epilog = 'See README for more details.')

parser.add_argument('-i', '--input_file', help='Name of input file', required=True) # required
parser.add_argument('-s',
                    '--section_number',
                    help='Help the tool start in the correct place',
                    default=1,
                    required=False
                    ) # optional
parser.add_argument('-c',
                    '--config_file',
                    help='Config file for test tool',
                    default="testtool_config.json",
                    required=False
                    ) # optional

args = parser.parse_args()

# parser settings
section_start = args.section_number
input_file = args.input_file
config_file_path = args.config_file

# import config file
with open(config_file_path, "r", encoding="utf-8") as jsonfile:
    config = json.load(jsonfile)

# config settings
insert_zero = config["insert_zero"]
page_dimensions = config["page_dimensions"]
last_section = config["last_section"]
next_section_text = []
for link_text in config["link_text"]:
    next_section_text.append(link_text.replace(' ', r'\s*'))

# grab pdf contents and organise into dict
FULL_CONTENT = ""

with fitz.open(input_file) as doc:
    for index, page in enumerate(doc):
        # for letter = fitz.Rect(0, 0, 612, 792)
        text_container = fitz.Rect(page_dimensions)
        FULL_CONTENT += page.get_text("text", clip=text_container)

with open('temp.txt', 'w', encoding="utf-8") as out_file:
    if insert_zero:
        out_file.write("0\n")
    out_file.write(FULL_CONTENT)

# build dict of sections, descriptions and exits
with open('temp.txt', 'r', encoding="utf-8") as temp:
    content = temp.read()

    # Define the regular expression for matching the entries
    SECTION_REGEX = r'(\d+)\n((?:(?!^\d+$).)*)'

    # Initialize the dictionary to store the parsed entries
    entries = {}

    # Find all matching entries in the text
    matches = re.findall(SECTION_REGEX, content, re.DOTALL | re.MULTILINE)

    # Process the matches and populate the dictionary
    for match in matches:
        section = match[0]
        DESC = ' '.join(match[1].split('\n'))
        exits = re.findall(fr'(?:{("|").join(next_section_text)})(\d+)', match[1], re.IGNORECASE) # pylint: disable=line-too-long
        if exits == []:
            entries[section] = {
                'section': section,
                'desc': DESC.replace("’", "'").replace('“', '"').replace('”', '"'),
                'exits': exits
            }

# MAIN LOOP

# create list of dicts of these sections
sections = []
section_list = []
for item in entries:
    if item == last_section:
        continue
    section_list.append(entries[str(item)]["section"])
    sections.append(entries[str(item)])


# create report for this test run
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)
template = env.get_template('ending-sections.html')
output = template.render(
                        section_list=section_list,
                        sections=sections,
                        )
# save the report
with open(f"{PATHING_DIRECTORY}/endings-test-report.html", "w", encoding="utf-8") as report:
    report.write(output)
