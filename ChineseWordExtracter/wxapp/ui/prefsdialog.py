'''
Copyright 2011 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

import wx
import os

class PrefsDialog ( wx.Dialog ):
    
    def __init__( self, parent, config ):
        self.config = config
        self.currentCharset = config['charset']

        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Preferences", pos = wx.DefaultPosition, size = wx.Size( 709,419 ), style = wx.DEFAULT_DIALOG_STYLE )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        #topSizer = wx.BoxSizer( wx.VERTICAL )
        topSizer = wx.FlexGridSizer( 4, 1, 0, 0 )
        topSizer.SetFlexibleDirection( wx.BOTH )
        topSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.listBoxPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        listBoxGridSizer = wx.FlexGridSizer( 2, 3, 0, 0 )
        listBoxGridSizer.SetFlexibleDirection( wx.BOTH )
        listBoxGridSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText1 = wx.StaticText( self.listBoxPanel, wx.ID_ANY, u"Dictionaries", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        listBoxGridSizer.Add( self.m_staticText1, 0, wx.ALL, 5 )
        
        
        listBoxGridSizer.AddSpacer( ( 40, 0), 1, wx.EXPAND, 5 )
        
        self.m_staticText3 = wx.StaticText( self.listBoxPanel, wx.ID_ANY, u"Filtered Words", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        listBoxGridSizer.Add( self.m_staticText3, 0, wx.ALL, 5 )

        # dictionary ListBox
        dictList = self.GetFileItems( os.path.join(self.config.appDir, 'dict') )
        self.dictListBox = wx.ListBox( self.listBoxPanel, wx.ID_ANY, wx.DefaultPosition, wx.Size( 200,100 ), dictList, wx.LB_EXTENDED|wx.LB_HSCROLL )
        listBoxGridSizer.Add( self.dictListBox, 0, wx.ALL, 5 )

        # pre-select current options
        for idx, val in enumerate(dictList):
            #for dictName in self.config["dictionaries"]:
            #    if dictName == val:
            #        self.dictListBox.SetSelection(idx, True)
            if val in self.config["dictionaries"]:
                self.dictListBox.SetSelection(idx, True)

        listBoxGridSizer.AddSpacer( ( 40, 0), 1, wx.EXPAND, 5 )

        # Filtered Words file ListBox
        filterList = self.GetFileItems( os.path.join(self.config.appDir, 'filter') )
        self.filterListBox = wx.ListBox( self.listBoxPanel, wx.ID_ANY, wx.DefaultPosition, wx.Size( 200,100 ), filterList, wx.LB_MULTIPLE|wx.LB_HSCROLL )
        listBoxGridSizer.Add( self.filterListBox, 0, wx.ALL, 5 )

        # pre-select current options
        for idx, val in enumerate(filterList):
            if val in self.config["filters"]:
                self.filterListBox.SetSelection(idx, True)
        
        self.listBoxPanel.SetSizer( listBoxGridSizer )
        self.listBoxPanel.Layout()
        listBoxGridSizer.Fit( self.listBoxPanel )
        topSizer.Add( self.listBoxPanel, 1, wx.EXPAND |wx.ALL, 5 )

        # Extra Column ListBox
        self.colPrefPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        fgSizer3 = wx.FlexGridSizer( 2, 1, 0, 0 )
        fgSizer3.SetFlexibleDirection( wx.BOTH )
        #fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.extraColLabel = wx.StaticText( self.colPrefPanel, wx.ID_ANY, u"Extra Column(s)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.extraColLabel.Wrap( -1 )
        fgSizer3.Add( self.extraColLabel, 0, wx.ALL, 5 )
        
        self.extraColListBox = wx.ListBox( self.colPrefPanel, wx.ID_ANY, wx.DefaultPosition, wx.Size( 200,100 ), [], wx.LB_MULTIPLE|wx.LB_HSCROLL )
        extraColList = self.GetFileItems( os.path.join(self.config.appDir, 'data', self.currentCharset) )        
        self._RefreshExtraColumnListBox(self.currentCharset)
        # pre-select current options
        for idx, val in enumerate(extraColList):
            if val in self.config["extracolumns"]:
                self.extraColListBox.SetSelection(idx, True)

        fgSizer3.Add( self.extraColListBox, 0, wx.ALL, 5 )

        
        self.colPrefPanel.SetSizer( fgSizer3 )
        self.colPrefPanel.Layout()
        fgSizer3.Fit( self.colPrefPanel )
        topSizer.Add( self.colPrefPanel, 1, wx.EXPAND |wx.ALL, 5 )


        # Character set RadioBox
        self.charsetPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        charsetSizer = wx.BoxSizer( wx.VERTICAL )
        
        # TODO be paranoid and verify the config value is an actual radio option
        charsetRadioBoxChoices = [ u"simplified", u"traditional" ]
        self.charsetRadioBox = wx.RadioBox( self.charsetPanel, wx.ID_ANY, u"Character set", wx.DefaultPosition, wx.DefaultSize, charsetRadioBoxChoices, 1, wx.RA_SPECIFY_ROWS )
        self.Bind(wx.EVT_RADIOBOX, self.OnCharsetChanged, self.charsetRadioBox)
        self.charsetRadioBox.SetStringSelection(config['charset'])
        charsetSizer.Add( self.charsetRadioBox, 0, wx.ALL, 5 )
        
        self.charsetPanel.SetSizer( charsetSizer )
        self.charsetPanel.Layout()
        charsetSizer.Fit( self.charsetPanel )
        topSizer.Add( self.charsetPanel, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.buttonPanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        buttonRowSizer = wx.BoxSizer( wx.HORIZONTAL )
        
        okButton = wx.Button( self.buttonPanel, wx.ID_ANY, u"Ok", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Bind(wx.EVT_BUTTON, self.OnOk, okButton)
        buttonRowSizer.Add( okButton, 0, wx.ALL, 5 )
        
        cancelButton = wx.Button( self.buttonPanel, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.Bind(wx.EVT_BUTTON, self.OnCancel, cancelButton)
        buttonRowSizer.Add( cancelButton, 0, wx.ALL, 5 )
        
        self.buttonPanel.SetSizer( buttonRowSizer )
        self.buttonPanel.Layout()
        buttonRowSizer.Fit( self.buttonPanel )
        topSizer.Add( self.buttonPanel, 1, wx.ALL|wx.EXPAND, 5 )
        
        self.SetSizer( topSizer )
        self.Layout()
        
        self.Centre( wx.BOTH )
    

    def OnCharsetChanged(self, event):
        newcharset = self.charsetRadioBox.GetStringSelection()
        if self.currentCharset != newcharset:
            self.currentCharset = newcharset
            self._RefreshExtraColumnListBox(newcharset)

    def _RefreshExtraColumnListBox(self, charset):
        extraColList = self.GetFileItems(os.path.join(self.config.appDir, 'data', charset))
        self.extraColListBox.SetItems(extraColList)

    def OnCancel(self, event):
        self.Destroy()
        event.Skip()

    def OnOk(self, event):
        # Check for dictionary changes and set reload if necessary
        dictSelected = []
        dictItems = self.dictListBox.GetItems()
        dictIdxSelected = self.dictListBox.GetSelections() 
        for idx in dictIdxSelected:
            dictSelected.append(dictItems[idx])
        
        if self.config["dictionaries"] != dictSelected:
            #need to reload dictionaries. This should be in an subscribed event
            self.config.dirtyDicts = True
            self.config.setDicts(dictSelected)

        # Check for filter file changes and set reload if necessary
        filterSelected = []
        filterItems = self.filterListBox.GetItems()
        filterIdxSelected = self.filterListBox.GetSelections() 
        for idx in filterIdxSelected:
            filterSelected.append(filterItems[idx])

        if self.config["filters"] != filterSelected:
            #need to reload dictionaries. This should be in an subscribed event
            self.config.dirtyFilters = True
            self.config.setFilters(filterSelected)

        # Check for extra column changes and set reload if necessary
        extracolSelected = []
        extracolItems = self.extraColListBox.GetItems()
        extracolIdxSelected = self.extraColListBox.GetSelections() 
        for idx in extracolIdxSelected:
            extracolSelected.append(extracolItems[idx])

        if self.config["extracolumns"] != extracolSelected:
            #need to reload dictionaries. This should be in an subscribed event
            self.config.dirtyExtraCols = True
            self.config.setExtraColumns(extracolSelected)

        newcharset = self.charsetRadioBox.GetStringSelection().encode('iso-8859-1')  # without the encode, converting to unicode yields "decoding Unicode is not supported"
        if self.config["charset"] != newcharset:
            self.config["charset"] = newcharset
            self.config.dirtyDicts = True
            self.config.dirtyExtraCols = True   # The data needs to be reloaded from the new files, even if the filenames have not changed
            self.config.setExtraColumns(extracolSelected)

        (saveStatus, ex) = self.config.save()
        if not saveStatus:
            #print "Error in prefsDialog.OnOk calling config.save: %s" % ex
            dlg = wx.MessageDialog(self, 'Unable to save configuration file. Error was (%s)' % ex, 'Error', wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            


        self.Destroy()
        

    def GetFileItems(self, directory):
        import stat

        choices = []
        filenames = []
        try:
            filenames = os.listdir(directory)
        except Exception, e:
            print "Error in GetFileItems: %s" % e
            dlg = wx.MessageDialog(self, 'Unable to read files in directory %s (%s)' % (directory, e), 'Error', wx.OK|wx.ICON_EXCLAMATION)
            dlg.ShowModal()
            dlg.Destroy()
            return choices
        
        for filename in filenames:
            if filename[0] != "_":
                try:
                    st = os.stat(os.path.join(directory, filename))
                except os.error:
                    continue
                if stat.S_ISREG(st.st_mode):
                    choices.append(filename)
        return choices
