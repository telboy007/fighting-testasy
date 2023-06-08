#!/usr/bin/env python

"""
    Finding exits since 2023
"""

import argparse
from pathlib import Path
import os
from ast import literal_eval
from jinja2 import Environment, FileSystemLoader  # pylint: disable=import-error
from src.helpers.config import import_config
from src.helpers.parse_adventure import parse_input_file


def flatten(alist, ltypes=(list, tuple)):
    """modified from https://code.activestate.com/recipes/363051/#c10"""
    ltype = type(alist)
    alist = list(alist)
    i = 0
    while i < len(alist):
        while isinstance(alist[i], ltypes):
            if not alist[i]:
                alist.pop(i)
                i -= 1
                break
            alist[i : i + 1] = alist[i]
        i += 1
    return ltype(alist)


# configure internal settings
PATHING_DIRECTORY = "exit-checks"

# Check if the directory exists
if not os.path.exists(PATHING_DIRECTORY):
    # If it doesn't exist, create it
    os.makedirs(PATHING_DIRECTORY)

# tidy up prior test runs
for file in Path(PATHING_DIRECTORY).glob("*.html"):
    try:
        file.unlink()
    except OSError as error:
        print(f"Error removing {file}: {error.strerror}")

# set up command line parser
parser = argparse.ArgumentParser(
    prog="python exit_checker.py",
    description="Finding orphaned sections so you don't have to.",
    epilog="See README for more details.",
)

parser.add_argument(
    "-i", "--input_file", help="Name of input file", required=True
)  # required
parser.add_argument(
    "-s",
    "--section_number",
    help="Starting section will be ignored when checking for orphaned sections",
    default=1,
    required=False,
)  # optional
parser.add_argument(
    "-c",
    "--config_file",
    help="Config file for test tool",
    default="testtool_config.json",
    required=False,
)  # optional

args = parser.parse_args()

# parser settings
section_start = args.section_number
input_file = args.input_file
config_file_path = args.config_file

# import config settings
config = import_config(config_file_path)

# set the config settings we want to use
insert_zero = config["insert_zero"]
page_dimensions = config["page_dimensions"]
not_allowed_choices = config["not_allowed_choices"]
last_section = config["last_section"]
next_section_text = config["link_text"]
end_of_adventure_text = config["end_of_adventure_text"]

# grab pdf contents and organise into dict
entries = parse_input_file(input_file, config)

# MAIN LOOP

# initialise lists
sections = []
list_of_exits = []

# create list of all sections
full_section_list = range(int(last_section) + 1)

# create list of exits from adventure dict
for entry in list(entries):
    list_of_exits.append(entries[entry]["exits"])

# created ordered list of integers from list of lists
list_of_exits = flatten(list_of_exits)
list_of_exits_int = [literal_eval(i) for i in list_of_exits]
list_of_exits_sorted = sorted(set(list_of_exits_int))

# compare the two lists and create list that can't be accessed
unaccessible_sections = set(full_section_list).difference(list_of_exits_sorted)
if 0 in unaccessible_sections:
    unaccessible_sections.remove(0)
if int(section_start) in unaccessible_sections:
    unaccessible_sections.remove(int(section_start))

# sort it
unaccessible_sections_sorted = sorted(set(unaccessible_sections))

# create list of dicts of these sections
for item in unaccessible_sections_sorted:
    sections.append(entries[str(item)])

# create report for this test run
file_loader = FileSystemLoader("templates")
env = Environment(loader=file_loader)
template = env.get_template("exit-sections.html")
output = template.render(
    unaccessible_sections=unaccessible_sections_sorted,
    sections=sections,
)
# save the report
with open(
    f"{PATHING_DIRECTORY}/exit-check-test-report.html", "w", encoding="utf-8"
) as report:
    report.write(output)
