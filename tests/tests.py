#!/usr/bin/env python

import os
from unittest import TestCase
import pathlib as pl


# command line
path_command_line = "python pathway_tester.py -i {0} -r 2 -c tests/test-config.json"
exits_command_line = "python exit_checker.py -i {0} -s 1 -c tests/test-config.json"
endings_command_line = "python lib/utilities/endings_finder.py -i {0} -c tests/test-config.json"
imager_command_line = "python branch_imager.py -i {0} -c tests/test-config.json"
test_input_file = "tests/data/test.pdf"
path_output_file1 = "pathing-tests/pass-1-test-report.html"
path_output_file2 = "pathing-tests/pass-2-test-report.html"
exits_output_file = "exit-checks/exit-check-test-report.html"
endings_output_file = "endings-finder/endings-test-report.html"
image_output_file = "branch-imaging/branching.png"


class Paths(TestCase):
    """ Test cases for pathing tester """
    # test pathing test file
    def test_pathway_tester_content(self):
        os.system(f"{path_command_line.format(test_input_file)}")
        with open(path_output_file1, "r", encoding="utf-8") as path:
            contents = path.read()
            self.assertIn("<b>Last section visited:</b> 5 (last section in adventure is 5)" , contents)


    # test pathing logic
    def test_pathway_tester_logic(self):
        os.system(f"{path_command_line.format(test_input_file)}")
        with open(path_output_file2, "r", encoding="utf-8") as path:
            contents = path.read()
            self.assertIn("has been previously visited, moving on." , contents)


    # test no zero in unvisited sections
    def test_pathway_tester_no_zero(self):
        os.system(f"{path_command_line.format(test_input_file)}")
        with open(path_output_file2, "r", encoding="utf-8") as path:
            contents = path.read()
            self.assertNotIn("<b>Sections not visited by any journey:</b> [0" , contents)


class Exits(TestCase):
    """ Test cases for exit tester """
    # test creation of exit test file
    def test_exist_tester_length(self):
        os.system(f"{exits_command_line.format(test_input_file)}")
        with open(exits_output_file, "r", encoding="utf-8") as path:
            # check file length
            check_value = len(path.read())
            self.assertEqual(check_value, 1056)


    # test correct orphaned section found
    def test_exits_tester_content(self):
        os.system(f"{exits_command_line.format(test_input_file)}")
        with open(exits_output_file, "r", encoding="utf-8") as path:
            # check correct section found
            contents = path.read()
            self.assertIn("[4]", contents)


class Images(TestCase):
    """ Test cases for branch imager """
    # test creation of imaging file
    def test_imaging_file_exists(self):
        os.system(f"{imager_command_line.format(test_input_file)}")
        path = pl.Path(image_output_file)
        self.assertEqual((str(path), path.is_file()), (str(path), True))


class Endings(TestCase):
    """ Test cases for ending finder """
    # test creation of exit test file
    def test_endings_finder_length(self):
        os.system(f"{endings_command_line.format(test_input_file)}")
        with open(endings_output_file, "r", encoding="utf-8") as path:
            # check file length
            check_value = len(path.read())
            self.assertEqual(check_value, 1194)


    # test correct orphaned section found
    def test_endings_finder_content(self):
        os.system(f"{endings_command_line.format(test_input_file)}")
        with open(endings_output_file, "r", encoding="utf-8") as path:
            # check correct section found
            contents = path.read()
            self.assertIn("['2', '4']", contents)
