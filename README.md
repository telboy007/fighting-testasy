# Fighting Testasy

Tests your choose your own adventure!  This tool is very much an alpha at the moment, collaboration is welcome.

### What it currently does

* Takes a pdf with embedded text (not image) and produces several test reports about pathing through your adventure, sections that are orphaned and not accessible by the reader and funky images of the branching - because why not!

You can use the test assets in numerous ways:
* The pathing test reports can be used by proof readers to check the flow of the adventure and make sure there aren't any logic jumps / story inconsistencies
* Run the pathing tests multiple times to see if there are any sections that don't get visited often (not orphaned sections - see below)
* Check out the orphaned sections mentioned by the exit checker report to check why they aren't accessible (i.e. plot lines that you dropped but some sections still remain)
* Frame images of the branching pathways of your adventure and hang them on the wall!

### What it doesn't currently do

* Doesn't do any OCR shenanigans on image PDFs (not yet anayway)
* Doesn't currently deal with txt, doc, etc. files (not yet anayway)

### What adventure structure can the test tool deal with?

Currently the test tool can deal with this style of structure

```
1

The adventure begins, you are in a room with a door to the left and another to the right. If you go left (go to 3), if you go right (go to 2).

2 

You enter into another room, this seems to be a dead end. You failed!

3

You enter the room and see another door in front of you Go through the door (go to 5).

4

This section of text can’t be accessed by the reader.

5

You find the treasure you’ve been searching for, congratulations adventurer. You win!

```

### How to use it

This test tool only runs locally at the moment, there is not packaged version yet.

1. Clone the repo
1. Add your PDF into the repo

PLEASE NOTE: Only have the adventure part in this pdf - remove the introduction sections, appendix, etc.  The adventure part can have images, maps, etc. they will be ignored.  Any font that is not recognised will appear as garbled characters in the section descriptions.

1. Run the following command:
  `python pathway_tester.py -i *your_pdf_file_name* -s 1 -r 10`
  This will run the path tester against your pdf starting at section 1 and it will run 10 times.
  Results can be found in the "pathing-tests" folder.
1. Each tool has its own help text to show you which command line args they need, use `-h` as the only arg to access this text.

### Features of the test reports

* The pathing test report will have debug information showing by dark grey bars that appear between the sections of text, these show the decision logic the tool used to navigate to the next section - in case you're wondering what is going on behind the scenes.  Also there is a summary at the bottom showing the journey through the adventure, what sections have been visited so far and which haven't.  The summary changes over the test run, i.e. by the 10th test run report the not visited sections should a lot smaller than in the first report.
* The exit checker test report will show a list of the sections the reader will never access and also print out the section text along with any exits mentioned in it's text.
* The branch imager creates cool looking images of the pathways through the adventure, but they will be colour coded (difficult to see unless you zoom in) - the start is purple, the best ending is green and any of the configured not allowed sections will be coloured red.

### How to configure it

* Anything that will need changing frequently is a command line arg - i.e. starting section, input file, number of test runs.
* Anything that isn't changed frequently is set up in the config file (json format)

```
{
    "insert_zero": false,
    "page_dimensions": [0, 0, 612, 700],
    "not_allowed_choices": ["50", "150"],
    "link_text": "go to section ",
    "last_section": "200"
}
```

If you adventure starts with an introduction passage with doesn't have a section number change "insert_zero" to true and this will add a zero to the start of the adventure.

Page dimensions is super important, this tells the PDF parser what sections of the page to ignore, i.e. headers and footers.  Page numbers will cause multiple problems if they are captured along with the adventure text.

Not allowed choices allows you to add all the sections which end the adventure, the pathing tool will avoid them. NOTE: at a later date another config option will be added to the pathing tool that will let you tell the tool to visit these end sections at least once.

Link text is also super important, this tells the pathing tool what text phrase is used before the section number the reader needs to jump to.

Last section allows you to configure the last section, this can be the end of the adventure or the end of a chapter or any section you want.

### Tests

All PRs will have tests run against them, just a heads up that the tests are functional at best due to the way the code is currently written.  As it is refactored over time the tests will get better.  Pinky promise.

### Big thanks

* Artifex Software's MuPDF library and the python implementation of it that powers this test tool.

### Troubleshooting

Raise an issue here and I will get back to you, thanks!
