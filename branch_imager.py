#!/usr/bin/env python

# Sources
# https://stackoverflow.com/a/43147251

"""
    Visualising twisted tales since 2023
"""

import argparse
import json
from pathlib import Path
import os
import re
import math
import fitz
import networkx as nx
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt


# configure internal settings
PATHING_DIRECTORY = "branch-imaging"

# Check if the directory exists
if not os.path.exists(PATHING_DIRECTORY):
    # If it doesn't exist, create it
    os.makedirs(PATHING_DIRECTORY)

# tidy up prior test runs
for file in Path(PATHING_DIRECTORY).glob('*.png'):
    try:
        file.unlink()
    except OSError as error:
        print(f"Error removing {file}: {error.strerror}")

# set up command line parser
parser = argparse.ArgumentParser(
                    prog = 'python branch_imager.py',
                    description = 'Test your own adventure.',
                    epilog = 'See README for more details.')

parser.add_argument('-i', '--input_file', help='Name of input file', required=True) # required
parser.add_argument('-c',
                    '--config_file',
                    help='Config file for test tool',
                    default="testtool_config.json",
                    required=False
                    ) # optional

args = parser.parse_args()

# parser settings
input_file = args.input_file
config_file_path = args.config_file

# import config file
with open(config_file_path, "r", encoding="utf-8") as jsonfile:
    config = json.load(jsonfile)

# config settings
insert_zero = config["insert_zero"]
page_dimensions = config["page_dimensions"]
not_allowed_choices = config["not_allowed_choices"]
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

# build dict of sections, DESCriptions and exits
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

# create list of all sections depending on start section
if insert_zero:
    full_section_list = range((int(last_section) + 1))
else:
    full_section_list = [i for i in range(int(last_section) + 1) if i != 0]

# initialise graph
G = nx.DiGraph()

for section in full_section_list:
    # grab section exits
    exits = entries[str(section)]["exits"]

    # start adding node
    G.add_node(str(section))
    G.add_nodes_from(exits)

    for section_exit in exits:
        #add edges
        G.add_edge(str(section),section_exit)

# try to work out decent sizes for the image
figsizex = 6.4 * math.ceil(float(G.size() / 24))
figsizey = 3.6 * math.ceil(float(G.size() / 32))

# configure size and quality of final image
fig = plt.figure(1, figsize=(figsizex, figsizey), dpi=100)

# create colour map for nodes
colour_map = ["#1f78b4"] * len(full_section_list)

# successful end node
position = list(G).index(last_section)
element = colour_map.pop(position)
colour_map.insert(position, "green")

# not allowed nodes
for section in not_allowed_choices:
    position = list(G).index(section)
    element = colour_map.pop(position)
    colour_map.insert(position, "red")

# overwrite starting node in case it was previously changed
element = colour_map.pop(0)
colour_map.insert(0, "purple")

# draw all the nodes
nx.draw(G,
        pos=nx.spring_layout(G),
        with_labels=True,
        node_color=colour_map,
        width=0.5,
        node_size=500,
        font_size=12,
        font_color="white",
        font_weight="normal"
        )

# save the file
try:
    plt.savefig(f"{PATHING_DIRECTORY}/branching.png")
except ValueError as error:
    raise
