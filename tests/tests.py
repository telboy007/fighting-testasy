#!/usr/bin/env python

import os
from unittest import TestCase
import pathlib as pl


# command line
path_command_line = "python pathway_tester.py -i {0} -c tests/test-config.json"
exits_command_line = "python exit_checker.py -i {0} -s 1 -c tests/test-config.json"
imager_command_line = "python branch_imager.py -i {0} -c tests/test-config.json"
path_input_file = "tests/data/test.pdf"
path_output_file = "pathing-tests/pass_1_test_report.html"
exits_output_file = "exit-checks/exit_check_test_report.html"
image_output_file = "branch-imaging/branching.png"


class Paths(TestCase):
    """ Test cases for pathing tester """
    # test creation of pathing test
    def test_pathway_tester_content(self):
        os.system(f"{path_command_line.format(path_input_file)}")
        with open(path_output_file, "r", encoding="utf-8") as path:
            contents = path.read()
            self.assertIn("<b>Last section visited:</b> 5 (last section in adventure is 5)" , contents)


class Exits(TestCase):
    """ Test cases for exit tester """
    # test creation of pathing test
    def test_exist_tester_length(self):
        os.system(f"{exits_command_line.format(path_input_file)}")
        with open(exits_output_file, "r", encoding="utf-8") as path:
            # check file length
            check_value = len(path.read())
            self.assertEqual(check_value, 1056)


    def test_exits_tester_content(self):
        os.system(f"{exits_command_line.format(path_input_file)}")
        with open(exits_output_file, "r", encoding="utf-8") as path:
            # check correct section found
            contents = path.read()
            self.assertIn("[4]", contents)


class Images(TestCase):
    """ Test cases for branch imager """
    # test creation of pathing test
    def test_imaging_file_exists(self):
        os.system(f"{imager_command_line.format(path_input_file)}")
        path = pl.Path(image_output_file)
        self.assertEqual((str(path), path.is_file()), (str(path), True))
