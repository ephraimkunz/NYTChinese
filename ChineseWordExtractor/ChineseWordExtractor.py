'''
Copyright 2011 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

import os, sys

from segmenterhelper import SegmenterHelper, RachelsCategories

NUM_NEW_WORDS_PER_RUN = 20

config = None

def run(segHelper):
    import os, sys, optparse
    #import config
    import config

    # parse args
    parser = optparse.OptionParser()
    parser.usage = "%prog"
    parser.add_option("-c", "--config", help="path to config file",
                      default=os.path.expanduser("~/Chinese Word Extractor/config.db"))
    parser.add_option("-i", "--inputfile", help="Path to input file")
    parser.add_option("-o", "--outputfile", help="When using an inputfile parameter, print summary output to a file (use '-' as filename to print to the console), and do not show an application window")
    parser.add_option("--appdir", help="Base directory of the application. It must contain subdirectories dict, data, and filter",
                      default=segHelper.runningDir)
    (opts, _) = parser.parse_args(sys.argv[1:])

    # configuration
    config = config.Config(
       str(os.path.abspath(opts.config)))

    #config.appDir = segHelper.runningDir
    config.appDir = opts.appdir

    segHelper.config = config
    segHelper.LoadData()
    segHelper.LoadKnownWords()
    segHelper.LoadExtraColumns()

    if opts.inputfile:
        segHelper.ReadFiles( [opts.inputfile])

    segHelper.SummarizeResults()
    print("\n")
    print(segHelper.summary)

    import codecs
    import csv
    try:
        # Read out all rows in file
        all_words = set()

        if os.path.exists(opts.outputfile):
            with open(opts.outputfile, 'r+') as tsvfile:
                reader = csv.DictReader(tsvfile, dialect='excel-tab')
                for row in reader:
                    all_words.add(row["original_word"])

        with open(opts.outputfile, 'a+') as tsvfile:
            if len(all_words) == 0:
                tsvfile.write(RachelsCategories.csv_header)

            new_words = []

            for word in segHelper.results:
                if word.orig_word not in all_words:
                    new_words.append(word)

                if len(new_words) == NUM_NEW_WORDS_PER_RUN:
                    break

            tsvfile.write("\n")
            results = '\n'.join([str(x) for x in new_words])
            tsvfile.write(results)
    except (OSError, IOError) as e:
        print("Warning: Failed to write to output file %s: %s" % (opts.outputfile, e))
    
if __name__ == "__main__":
    try:
        modDir=os.path.dirname(os.path.abspath(__file__))
        runningDir=os.path.split(modDir)[0]
    except NameError:
        runningDir=os.path.dirname(sys.argv[0])
        modDir=runningDir

    segHelper = SegmenterHelper(modDir)
    run(segHelper)
