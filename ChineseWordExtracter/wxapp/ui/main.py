'''
Copyright 2011 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

import wx
from wx.lib.wordwrap import wordwrap

import version

# non-standard menus
ID_REFRESH_RESULTS = 101

## Constants for identifying control keys and classes of keys:
WXK_CTRL_A = ord('A')


class SelectableTextCtrl(wx.TextCtrl):                                
    def __init__(self, parent, *args, **kwargs):
        wx.TextCtrl.__init__(self, parent, *args, **kwargs)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def OnKeyDown(self,event=None):
        if event.ControlDown() and event.GetKeyCode() == WXK_CTRL_A:
            self.SetSelection(-1, -1)
        else:
            event.Skip()

class EditorPanel1(SelectableTextCtrl):
    def __init__(self, parent, *args, **kwargs):
        SelectableTextCtrl.__init__(self, parent, *args, **kwargs)

        
class ResultPanel1(SelectableTextCtrl):
    def __init__(self, parent, *args, **kwargs):
        SelectableTextCtrl.__init__(self, parent, *args, **kwargs)


class SummaryPanel1(SelectableTextCtrl):
    def __init__(self, parent, *args, **kwargs):
        SelectableTextCtrl.__init__(self, parent, *args, **kwargs)

class MessagePanel1(SelectableTextCtrl):
    def __init__(self, parent, *args, **kwargs):
        SelectableTextCtrl.__init__(self, parent, *args, **kwargs)

class TokenPanel1(SelectableTextCtrl):
    def __init__(self, parent, *args, **kwargs):
        SelectableTextCtrl.__init__(self, parent, *args, **kwargs)



    
class NoteBook1(wx.Notebook):
    def __init__(self, parent, id, *args, **kwargs):
        #wx.Notebook.__init__(self, parent, *args, **kwargs)

        wx.Notebook.__init__(self, parent, id, size=(21,21), style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             # | wx.NB_MULTILINE
                             )

        self.editorPanel = EditorPanel1(self, 1, style=wx.TE_MULTILINE)
        #the first paste into a TextCtrl truncates at 30k characters on Windows. The following
        #line, while setting a hard-limit on the text size, is a quick way to fix
        #the 30k bug
        self.editorPanel.SetMaxLength(1e9)
        self.AddPage(self.editorPanel, 'Source')

        self.summaryPanel = SummaryPanel1(self, 1, style=wx.TE_MULTILINE |wx.TE_READONLY | wx.TE_DONTWRAP )
        self.AddPage(self.summaryPanel, 'Summary', )

        self.resultPanel = ResultPanel1(self, 1, style=wx.TE_MULTILINE |wx.TE_READONLY | wx.TE_DONTWRAP )
        self.resultPanel.SetMaxLength(1e9)
        self.AddPage(self.resultPanel, 'Results', )

        self.tokenPanel = TokenPanel1(self, 1, style=wx.TE_MULTILINE |wx.TE_READONLY )
        self.tokenPanel.SetMaxLength(1e9)
        self.AddPage(self.tokenPanel, 'Segmented', )

        self.messagePanel = ResultPanel1(self, 1, style=wx.TE_MULTILINE |wx.TE_READONLY | wx.TE_DONTWRAP )
        self.messagePanel.SetMaxLength(1e9)
        self.AddPage(self.messagePanel, 'Messages', )


class MainWindow(wx.Frame):

    config = None
    segHelper = None

    def OnRefreshResults(self, e):
        self.segHelper.setText(self.notebook.editorPanel.GetValue())

        prog = wx.ProgressDialog(parent=self, title="Progress", message="parsing Results", style=wx.PD_AUTO_HIDE|wx.PD_SMOOTH)
        self.segHelper.SummarizeResults(updatefunction=prog.Update)
        prog.Destroy()

        #st = wx.StaticText(self.notebook.resultPanel, -1, self.segHelper.summary, (10, 10))
        self.notebook.summaryPanel.SetValue(self.segHelper.summary)
        self.notebook.resultPanel.SetValue(self.segHelper.results)
        self.notebook.tokenPanel.SetValue(self.segHelper.tokens)
        self.notebook.messagePanel.SetValue(self.segHelper.getMessages())


    def OnAbout(self, e):
        # First we create and fill the info object
        info = wx.AboutDialogInfo()
        info.Name = "Chinese Word Extractor"
        info.Version = "v. %s" % version.APP_VERSION
        info.Copyright = "(C) 2011 Chad Redman"
        info.Description = wordwrap(
            "This is a tool to extract vocabulary from Chinese text, summarizing "
            "the unique words with word count, pinyin, English definition, and other useful "
            "statistics.",
            500, wx.ClientDC(self))
        info.WebSite = ("http://www.zhtoolkit.com/apps/Chinese Word Extractor", "Project home page")
        #info.Developers = [ "Joe Programmer",
        #                    "Jane Coder",
        #                    "Vippy the Mascot" ]
        info.License = wordwrap(
            "This program is licensed under the terms of the "
            "GPL v.3.0; see http://www.gnu.org/licenses/gpl-3.0.html for details.",
            500, wx.ClientDC(self))

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)

    def OnDocumentation(self, e):
        import webbrowser
        webbrowser.open("http://www.zhtoolkit.com/apps/Chinese Word Extractor/help.html") 
    
    def OnOpen(self, e):
        """ Open a file """

        self.dirname = self.config['currentdir']
        #dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "Text Files (*.txt)|*.txt|UTF-8 text files (*.txt, *.u8)|*.u8;*.txt|All files (*)|*.*", style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
        dlg = wx.FileDialog(self, "Choose one or more files", self.dirname, "", "text files (*.txt, *.u8, *.gb, *.big5)|*.txt;*.u8;*.gb;*.big5|HTML files (*.htm, *.html)|*.htm;*.html|All files (*)|*.*", style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            #self.filename = dlg.GetFilename()
            #self.dirname = dlg.GetDirectory()
            #f = open(os.path.join(self.dirname, self.filename), 'r')
            #self.notebook.editorPanel.SetValue(f.read())
            #f.close()
            
            self.notebook.editorPanel.SetValue(self.segHelper.ReadFiles(dlg.GetPaths()))
            
            self.notebook.messagePanel.SetValue(self.segHelper.getMessages())

            self.config['currentdir'] = dlg.GetDirectory()
            self.config.save()

        dlg.Destroy()

    def OnExit(self, e):
        self.config.save()
        self.Close(True)
        
    def OnPreferences(self, e):
        import prefsdialog
        d = prefsdialog.PrefsDialog(self, self.config)
        d.ShowModal()
        d.Destroy()
        if self.config.dirtyDicts:
            prog = wx.ProgressDialog(parent=None, title="Progress", message="Loading Dictionary", style=wx.PD_AUTO_HIDE|wx.PD_SMOOTH)
            self.segHelper.LoadData(updatefunction=prog.Update)
            prog.Destroy()

            #self.segHelper.LoadData(self.config, updatefunction=wx.ProgressDialog(title="Progress", message="Loading Dictionary", style=wx.PD_AUTO_HIDE|wx.PD_SMOOTH).Update)
            self.config.dirtyDicts = False

        if self.config.dirtyFilters:
            self.segHelper.LoadKnownWords()
            #self.segHelper.LoadData(self.config, updatefunction=wx.ProgressDialog(title="Progress", message="Loading Dictionary", style=wx.PD_AUTO_HIDE|wx.PD_SMOOTH).Update)
            self.config.dirtyFilters = False

        if self.config.dirtyExtraCols:
            self.segHelper.LoadExtraColumns()
            self.config.dirtyExtraCols = False

        self.notebook.messagePanel.SetValue(self.segHelper.getMessages())


    def __init__(self, parent, *args, **kwargs):
        wx.Frame.__init__(self, parent, *args, **kwargs)

        mainmenu = wx.MenuBar()                  # Create menu bar.
        filemenu = wx.Menu()
        helpmenu = wx.Menu()

        item = filemenu.Append(wx.ID_OPEN, '&Open', 'Open a file')
        self.Bind(wx.EVT_MENU, self.OnOpen, item)  # Create and assign a menu event.
        item = filemenu.Append(ID_REFRESH_RESULTS, '&Analyze', 'Analyze Results')
        self.Bind(wx.EVT_MENU, self.OnRefreshResults, item)  # Create and assign a menu event.
        item = filemenu.Append(wx.ID_PREFERENCES, 'P&references', 'Configure application settings')
        self.Bind(wx.EVT_MENU, self.OnPreferences, item)  # Create and assign a menu event.
        item = filemenu.Append(wx.ID_EXIT, 'E&xit', 'Terminate the program')
        self.Bind(wx.EVT_MENU, self.OnExit, item)  # Create and assign a menu event.

        item = helpmenu.Append(wx.ID_HELP_CONTENTS, '&Documentation', 'Launches a web browser to view online instructions')
        self.Bind(wx.EVT_MENU, self.OnDocumentation, item)  # Create and assign a menu event.
        item = helpmenu.Append(wx.ID_ABOUT, '&About', 'Information about this program')
        self.Bind(wx.EVT_MENU, self.OnAbout, item)  # Create and assign a menu event.

        mainmenu.Append(filemenu, '&File')
        mainmenu.Append(helpmenu, '&Help')
        self.SetMenuBar(mainmenu)

        self.notebook = NoteBook1(self, 1)        
