#!/usr/bin/env python

"""
    Finding exits since 2023
"""

import argparse
from pathlib import Path
import json
import os
from jinja2 import Environment, FileSystemLoader  # pylint: disable=import-error
from ..helpers.parse_adventure import parse_input_file


# configure internal settings
PATHING_DIRECTORY = "endings-finder"

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
    prog="python -m src.utilities.endings_finder",
    description="Finds endings (except the best ending) that can be added to the not allowed list",  # pylint: disable=line-too-long
    epilog="See README for more details.",
)

parser.add_argument(
    "-i", "--input_file", help="Name of input file", required=True
)  # required
parser.add_argument(
    "-s",
    "--section_number",
    help="Help the tool start in the correct place",
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

# import config file
with open(config_file_path, "r", encoding="utf-8") as jsonfile:
    config = json.load(jsonfile)

# config settings
insert_zero = config["insert_zero"]
page_dimensions = config["page_dimensions"]
last_section = config["last_section"]
next_section_text = []
for link_text in config["link_text"]:
    next_section_text.append(link_text.replace(" ", r"\s*"))

# grab pdf contents and organise into dict
entries = parse_input_file(input_file, config)

# MAIN LOOP

# create list of dicts of section with no exits
sections = []
section_list = []
for item in entries:
    if item == last_section:
        continue
    if entries[str(item)]["exits"] == []:
        section_list.append(entries[str(item)]["section"])
        sections.append(entries[str(item)])


# create report for this test run
file_loader = FileSystemLoader("templates")
env = Environment(loader=file_loader)
template = env.get_template("ending-sections.html")
output = template.render(
    section_list=section_list,
    sections=sections,
)
# save the report
with open(
    f"{PATHING_DIRECTORY}/endings-test-report.html", "w", encoding="utf-8"
) as report:
    report.write(output)
