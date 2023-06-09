#!/usr/bin/env python
# pylint: disable=duplicate-code

# Sources
# https://stackoverflow.com/a/43147251

"""
    Visualising twisted tales since 2023
"""

import argparse
from pathlib import Path
import os
import math
import networkx as nx  # pylint: disable=import-error
import matplotlib  # pylint: disable=wrong-import-position, import-error

matplotlib.use("Agg")
from matplotlib import (  # pylint: disable=wrong-import-position, import-error
    pyplot as plt,
)
from src.helpers.config import import_config  # pylint: disable=wrong-import-position
from src.helpers.parse_adventure import (  # pylint: disable=wrong-import-position
    parse_input_file,
)


# configure internal settings
PATHING_DIRECTORY = "branch-imaging"

# Check if the directory exists
if not os.path.exists(PATHING_DIRECTORY):
    # If it doesn't exist, create it
    os.makedirs(PATHING_DIRECTORY)

# tidy up prior test runs
for file in Path(PATHING_DIRECTORY).glob("*.png"):
    try:
        file.unlink()
    except OSError as error:
        print(f"Error removing {file}: {error.strerror}")

# set up command line parser
parser = argparse.ArgumentParser(
    prog="python branch_imager.py",
    description="Test your own adventure.",
    epilog="See README for more details.",
)

parser.add_argument(
    "-i", "--input_file", help="Name of input file", required=True
)  # required
parser.add_argument(
    "-c",
    "--config_file",
    help="Config file for test tool",
    default="testtool_config.json",
    required=False,
)  # optional

args = parser.parse_args()

# parser settings
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
        # add edges
        G.add_edge(str(section), section_exit)

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
nx.draw(
    G,
    pos=nx.spring_layout(G),
    with_labels=True,
    node_color=colour_map,
    width=0.5,
    node_size=500,
    font_size=12,
    font_color="white",
    font_weight="normal",
)

# save the file
try:
    plt.savefig(f"{PATHING_DIRECTORY}/branching.png")
except ValueError as error:
    raise error
