'''
Copyright 2011 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

import os, sys

from segmenterhelper import SegmenterHelper



if __name__ == "__main__":
    try:
        modDir=os.path.dirname(os.path.abspath(__file__))
        runningDir=os.path.split(modDir)[0]
    except NameError:
        runningDir=os.path.dirname(sys.argv[0])
        modDir=runningDir

    segHelper = SegmenterHelper(modDir)
    wxapp.run(segHelper)
