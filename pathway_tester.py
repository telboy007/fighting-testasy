#!/usr/bin/env python

"""
    Branching out since 2023
"""

import argparse
import os
import random
from ast import literal_eval
from pathlib import Path
from jinja2 import Environment, FileSystemLoader # pylint: disable=import-error
from lib.helpers.config import import_config
from lib.helpers.parse_adventure import parse_input_file


# configure internal settings
PATHING_DIRECTORY = "pathing-tests"

# check if the directory exists
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
                    prog = 'python pathway_test.py',
                    description = 'Test your own adventure.',
                    epilog = 'See README for more details.')

parser.add_argument('-i', '--input_file', help='Name of input file', required=True) # required
parser.add_argument('-r',
                    '--test_runs',
                    help='Number of times to run the pathway tests',
                    default=1,
                    required=False
                    ) # optional
parser.add_argument('-s',
                    '--section_number',
                    help='To start test at a different section number than one',
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
total_run_count = int(args.test_runs)
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

# initialise required lists outside of test loop
all_sections_run = []

# run the tests based on number of test runs
for run in range(total_run_count):

    # need to add one to get a nice iteration number
    iteration = run + 1

    # initialise required lists inside of test loop
    content = []
    current_journey = []

    # initialise current section
    CURRENT_SECTION = str(section_start)

    # first section content - no debug info needed
    section = {
        "section_number": f"Starting from section {section_start}",
        "description": entries[str(section_start)]['desc']
    }

    # add content to list for jinja2 template
    content.append(section)

    # add starting point to both lists
    current_journey.append(str(section_start))
    all_sections_run.append(str(section_start))

    while entries[CURRENT_SECTION]["exits"] != []:
        # reset exit loop
        EXIT_LOOP = False

        # make note of previous section
        previous_section = CURRENT_SECTION if CURRENT_SECTION is not None else section_start

        # start to create pathing decision logic debug info
        DEBUG = ""
        DEBUG += f"Current section: {previous_section}<br />"
        DEBUG += f"Current section exits: {entries[CURRENT_SECTION]['exits']}<br />"

        # grab current exits as we may need to remove options
        current_section_exits = entries[CURRENT_SECTION]["exits"]

        # iterate through exits to find next valid path
        for index, section_exit in enumerate(current_section_exits):
            if section_exit in not_allowed_choices:
                DEBUG += f"Exit not allowed removing from valid options: {section_exit}<br />"
                # remove exit from list to prevent infinite loops
                current_section_exits.remove(section_exit)
                continue
            if len(entries[CURRENT_SECTION]["exits"]) == 1:
                CURRENT_SECTION = section_exit
                DEBUG += f"Section only has the one exit, picking: {section_exit}<br />"
                break
            if section_exit not in all_sections_run:
                CURRENT_SECTION = section_exit
                DEBUG += f"Exit hasn't been visited yet, picking: {section_exit}<br />"
                break
            if index == len(entries[CURRENT_SECTION]["exits"]) - 1:
                CURRENT_SECTION = random.choice(entries[CURRENT_SECTION]["exits"])
                DEBUG += f"Visited all options, picking random exit: {CURRENT_SECTION}<br />"
                break
            DEBUG += f"\"{section_exit}\" has been previously visited, moving on.<br />"

        # write out pathing logic
        DEBUG += f"Moving to section: {CURRENT_SECTION}"

        # if end of adventure text is set trim desc here but remain in loop
        if end_of_adventure_text:
            if end_of_adventure_text in entries[CURRENT_SECTION]["desc"]:
                # split description text with end of adventure text and use left portion
                entries[CURRENT_SECTION]["desc"] = entries[CURRENT_SECTION]["desc"].split(end_of_adventure_text)[0] # pylint: disable=line-too-long
                EXIT_LOOP = True

        # subsequent section content
        section = {
            "section_number": f"Section {entries[CURRENT_SECTION]['section']}",
            "description": entries[CURRENT_SECTION]['desc'],
            "pathing": f"Moving from \"{previous_section}\" to \"{CURRENT_SECTION}\"",
            'debug_info': DEBUG
        }

        # add content to list for jinja2 template
        content.append(section)

        # keep track of sections visited in this journey
        current_journey.append(entries[CURRENT_SECTION]["section"])

        # keep track of the all sections visited so far
        all_sections_run.append(entries[CURRENT_SECTION]["section"])

        # if end of adventure text was found finish loop here
        if EXIT_LOOP:
            break

    # format lists into ordered integers for test summary

    # all sections list
    all_sections_run_int = [literal_eval(i) for i in all_sections_run]
    all_sections_run_sorted = sorted(set(all_sections_run_int))

    # create list of sections not visited yet
    comparison_range = range(int(last_section) + 1)
    sections_not_visited = set(comparison_range).difference(all_sections_run_sorted)

    # remove not allowed choices from the not visited list including zero
    not_allowed_choices_int = [literal_eval(i) for i in not_allowed_choices]
    not_allowed_choices_int.append(0)

    for item in not_allowed_choices_int:
        try:
            sections_not_visited.remove(item)
        except: # pylint: disable=bare-except
            continue

    # and finally sort it
    sections_not_visited_sorted = sorted(set(sections_not_visited))

    # update all sections run to feed back into next test run
    all_sections_run = [str(i) for i in all_sections_run_sorted]

    # create report for this test run
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('content.html')
    output = template.render(
                            iteration=iteration,
                            total_run_count=total_run_count,
                            content=content,
                            current_section=CURRENT_SECTION,
                            last_section=last_section,
                            current_journey=(" > ").join(current_journey),
                            all_sections_run_sorted=all_sections_run_sorted,
                            sections_not_visited_sorted=sections_not_visited_sorted
                            )
    # save the report
    with open(
              f"{PATHING_DIRECTORY}/pass-{iteration}-test-report.html", # output file
              "w", # mode
              encoding="utf-8" # encoding
              ) as report:
        report.write(output)
