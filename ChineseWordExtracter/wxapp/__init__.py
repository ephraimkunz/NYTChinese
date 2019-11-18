'''
Copyright 2011 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

import wx

try:
    WindowsError
except NameError:
    WindowsError = OSError

config = None

def run(segHelper):
    import os, sys, optparse
    #import config
    import ui, config

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


    app = wx.PySimpleApp()

    # Notes on icon bundles:
    # 1) can't be 256x256 because too big to import within the application
    # 2) the 16x16 object will be the shown in taskbar , Explorer list view, application context menu, etc.
    #     - It will choose the 16-color icon if it exists. I don't know why anyone would want this
    #     - the 256 color works fine. I haven't tried other sizes.

    # pre-load icons; they need to be set for the load dictionary progress, since it happens before the main frame shows
    ib = wx.IconBundle()
    ib.AddIconFromFile(os.path.join(segHelper.runningDir, "application-icon.ico"), wx.BITMAP_TYPE_ANY)

    # configuration
    config = config.Config(
       unicode(os.path.abspath(opts.config), sys.getfilesystemencoding()))

    #config.appDir = segHelper.runningDir
    config.appDir = opts.appdir

    prog = wx.ProgressDialog(parent=None, title="Progress", message="Loading Dictionary", style=wx.PD_AUTO_HIDE|wx.PD_SMOOTH)
    prog.SetIcons(ib)
    segHelper.config = config
    segHelper.LoadData(updatefunction=prog.Update)
    prog.Destroy()

    segHelper.LoadKnownWords()
    segHelper.LoadExtraColumns()

    #loads main window
    ui.importAll()
    frame = ui.main.MainWindow(None, -1, "Chinese Word Extractor", size=(750,500))

    frame.SetIcons(ib)
    
    frame.segHelper = segHelper
    frame.config = config
    
    if opts.inputfile:
        frame.notebook.editorPanel.SetValue(segHelper.ReadFiles( [opts.inputfile]))


    if opts.outputfile:
        segHelper.SummarizeResults()
        if opts.outputfile == "-":
            print segHelper.summary
            print "\n\n"
            print segHelper.results
        else:
            import codecs
            try:
                f = codecs.open(opts.outputfile, encoding='utf-8', mode='w')
                f.write(segHelper.summary + "\n\n" + segHelper.results)
                f.close()        
            except (WindowsError, OSError, IOError), e:
                print "Warning: Failed to write to output file %s: %s" % (opts.outputfile, e)
        frame.DestroyChildren()
        frame.Destroy()
        sys.exit()
            

    frame.notebook.messagePanel.SetValue(frame.segHelper.getMessages())
    frame.Show(True)
    

    app.MainLoop()


#if __name__ == "__main__":
#    run()
