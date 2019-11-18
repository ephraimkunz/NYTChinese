'''
Copyright 2011 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

import os, pickle
import errno

class Config(dict):

    configFileFullPath = None
    appDir = None

    dirtyDicts = False
    dirtyFilters = False
    dirtyExtraCols = False

    def __init__(self, configFileFullPath):
        # TODO platform-independent
        #self.configFileFullPath = os.path.join(self.configPath, self.configFileName)
        self.configFileFullPath = configFileFullPath

#        self.makeWorkingDir()
        self.load()


    def setDefaults(self):
        fields = {
            #'dicts': {"cedict_ts.u8" : "cedict"},
            'filters': [],
            'extracolumns': [],
            'currentdir': "samples",
            'dictionaries': ['cedict_ts-merged-refs.u8'],
            'charset': 'simplified',
            }

        for (k,v) in list(fields.items()):
            if k not in self:
                self[k] = v


#    def makeWorkingDir(self):
#        base = self.configPath
#        for x in (base,
#                  os.path.join(base, "plugins"),
#                  os.path.join(base, "backups")):
#            try:
#                os.mkdir(x)
#            except:
#                pass


    def _makedir(self, dirpath):
        try:            
            #os.makedirs(dirpath)
            #os.mkdir(dirpath, 0700)
            os.mkdir(dirpath)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        
    def save(self):
        # create directory if it doesn't exist
        
        configDir = os.path.dirname(self.configFileFullPath)
        try:            
            self._makedir(configDir)
            # write to a temp file
            from tempfile import mkstemp
            (fd, tmpname) = mkstemp(dir=configDir)
            tmpfile = os.fdopen(fd, 'w')
            pickle.dump(dict(self), tmpfile)
            tmpfile.close()
            # the write was successful, delete config file (if exists) and rename
            if os.path.isfile(self.configFileFullPath):
                os.unlink(self.configFileFullPath)
            os.rename(tmpname, self.configFileFullPath)
            return (True, None)
        except Exception as e:
            #print u"Error saving preferences file %s (%s)" % (self.configFileFullPath, e)
            return (False, e)


    def load(self):
        if os.path.isfile(self.configFileFullPath):
            try:
                f = open(self.configFileFullPath)
                self.update(pickle.load(f))
            except (IOError, EOFError):
                # Corrupted format
                #print u"DEBUG: config.load(): unable to read file %s: (%s)" % (self.configFileFullPath, ex)
                #print u"DEBUG:   Using the defaults instead"
                pass

        self.setDefaults()

    def setDicts(self, dict_ar):
        # TODO move setting of dirtyDict here instead of caller
        self["dictionaries"] = dict_ar

    def setFilters(self, filter_ar):
        self["filters"] = filter_ar

    def setExtraColumns(self, extracols_ar):
        self["extracolumns"] = extracols_ar
