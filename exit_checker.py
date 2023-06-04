#!/usr/bin/env python

"""
    Finding exits since 2023
"""

import argparse
from pathlib import Path
import json
import os
import re
from ast import literal_eval
import fitz
from jinja2 import Environment, FileSystemLoader


def flatten(l, ltypes=(list, tuple)):
    """ modified from https://code.activestate.com/recipes/363051/#c10 """
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            l[i:i + 1] = l[i]
        i += 1
    return ltype(l)


# configure internal settings
PATHING_DIRECTORY = "exit-checks"

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
                    prog = 'python exit_checker.py',
                    description = 'Finding orphaned sections so you don\'t have to.',
                    epilog = 'See README for more details.')

parser.add_argument('-i', '--input_file', help='Name of input file', required=True) # required
parser.add_argument('-s',
                    '--section_number',
                    help='Starting section will be ignored when checking for orphaned sections',
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
next_section_text = config["link_text"].replace(' ', r'\s*')

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
    out_file.write(FULL_CONTENT.replace('get to 350', 'go to 350'))

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
        exits = re.findall(fr'{next_section_text}(\d+)', match[1], re.IGNORECASE)
        entries[section] = {
            'section': section,
            'desc': DESC.replace("’", "'").replace('“', '"').replace('”', '"'),
            'exits': exits
        }

# MAIN LOOP

# initialise lists
sections = []
list_of_exits = []

# create list of all sections
full_section_list = range(int(last_section) + 1)

# create list of exits from adventure dict
for entry in entries:
    list_of_exits.append(entries[entry]['exits'])

# created ordered list of integers from list of lists
list_of_exits = flatten(list_of_exits)
list_of_exits_int = [literal_eval(i) for i in list_of_exits]
list_of_exits_sorted = sorted(set(list_of_exits_int))

# compare the two lists and create list that can't be accessed
unaccessible_sections = set(full_section_list).difference(list_of_exits_sorted)
unaccessible_sections.remove(0)
if not insert_zero:
    unaccessible_sections.remove(int(section_start))

# sort it
unaccessible_sections_sorted = sorted(set(unaccessible_sections))

# create list of dicts of these sections
for item in unaccessible_sections_sorted:
    sections.append(entries[str(item)])

# create report for this test run
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)
template = env.get_template('sections.html')
output = template.render(
                        unaccessible_sections=unaccessible_sections_sorted,
                        sections=sections,
                        )
# save the report
with open(f"{PATHING_DIRECTORY}/exit_check_test_report.html", "w", encoding="utf-8") as report:
    report.write(output)
