'''
Copyright 2011 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

import os, sys

from segmenterhelper import SegmenterHelper


config = None

def run(segHelper):
    import os, sys, optparse
    #import config
    from . import config

    # parse args
    parser = optparse.OptionParser()
    parser.usage = "%prog"
    parser.add_option("-c", "--config", help="path to config file",
                      default=os.path.expanduser("~/Chinese Word Extractor/config.db"))
    parser.add_option("-i", "--inputfile", help="Path to input file")
    parser.add_option("-o", "--outputfile", help="When using an inputfile parameter, print summary output to a file (use '-' as filename to print to the console), and do not show an application window")
    parser.add_option("--appdir", help="Base directory of the application. It must contain subdirectories dict, data, and filter",
                      default=segHelper.runningDir)
    (opts, args) = parser.parse_args(sys.argv[1:])

    # configuration
    config = config.Config(
       str(os.path.abspath(opts.config), sys.getfilesystemencoding()))

    #config.appDir = segHelper.runningDir
    config.appDir = opts.appdir

    segHelper.config = config
    segHelper.LoadData()
    segHelper.LoadKnownWords()
    segHelper.LoadExtraColumns()

    if opts.inputfile:
        segHelper.ReadFiles( [opts.inputfile])


    if opts.outputfile:
        segHelper.SummarizeResults()
        if opts.outputfile == "-":
            print(segHelper.summary)
            print("\n\n")
            print(segHelper.results)
        else:
            import codecs
            try:
                f = codecs.open(opts.outputfile, encoding='utf-8', mode='w')
                f.write(segHelper.summary + "\n\n" + segHelper.results)
                f.close()        
            except (OSError, IOError) as e:
                print("Warning: Failed to write to output file %s: %s" % (opts.outputfile, e))
        sys.exit()

if __name__ == "__main__":
    try:
        modDir=os.path.dirname(os.path.abspath(__file__))
        runningDir=os.path.split(modDir)[0]
    except NameError:
        runningDir=os.path.dirname(sys.argv[0])
        modDir=runningDir

    segHelper = SegmenterHelper(modDir)
    run(segHelper)
