'''
Copyright 2011 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

from ChineseWordExtractor import segmenter
import os
import datetime

# The data here gets refreshed when called
class SegmenterHelper:
    #from segmenter import Dictionary, Statistics, Segmenter


    def addMessage(self, text):
        try:
            self.messages.append(str(text))
            #self.messages.append(text)
        except TypeError:
            try:
                self.messages.append(text)
            except:
                print("Failed to log error message for %s" % text)
                self.messages.append("Failed to log error message! Run in console to see details")


    def getMessages(self):
        return "\n".join(self.messages)
    
    def setText(self, text):
        self.text = text

    def __init__(self, runningDir):
        self.text = ''
        self.results = []
        self.summary = ''
        self.messages = []
        self.runningDir = runningDir
        self.dicts = []
        self.filterwords = []
        self.config = None
        self.stats = {}  # a mapping between filenames and data list
        self.statFiles = {}  # a mapping between filenames and heading


    def LoadData(self, updatefunction=None):
        'Called when first starting the program, or when preference change sets dirtyDicts'

        config = self.config
        if config['charset']:
            charset = config['charset']
        else:
            charset = 'simplified'

        self.dicts = []

        for dictname in config['dictionaries']:
            self.addMessage("Loading dictionary %s ..." % dictname)
            dictFile = os.path.join(config.appDir, 'dict', dictname)
            dict = segmenter.Dictionary(dictFile, format='cedict', verbose=True, updatefunction=updatefunction)

            if dict.messages != None:
                for elem in dict.messages:
                    self.addMessage(elem)
                # add a blank line

            self.addMessage("Loaded dictionary %s, %d words" % (dictname, dict.getWordCount()))
            self.dicts.append(dict)

        self.seg = segmenter.Segmenter(charset, self.dicts, self.stats)
        self.addMessage("")


    def LoadKnownWords(self, updatefunction=None):
        self.filterwords = []
        for filtername in self.config['filters']:
            self.LoadFilterFile(os.path.join(self.config.appDir, 'filter', filtername))
            self.addMessage("Loaded filtered word file %s" % filtername)
        self.addMessage("")

    def LoadExtraColumns(self):
        charset = self.config['charset']
        self.stats={}
        for statfile in self.config['extracolumns']:
            self.LoadStatisticsFile(self.config, statfile, charset)

        self.seg.setStatistics(self.stats)

    def LoadFilterFile(self, filename):
        import re
        try:
            fh = open(filename)  #throws IOError
        except Exception as ex:
            self.addMessage("**Error: Failed to load filter file %s: (%s)" % (filename, ex))
            return 0

        lineno = 0
        try:
            for line in fh.read().splitlines():
                lineno += 1
                if not re.match('\s*#', str(line)):
                    m = re.match('[^ \t]+', str(line))
                    if m:
                        self.filterwords.append(m.group(0))
        finally:
            fh.close()
        
        return lineno

    def LoadStatisticsFile(self, config, filename, charset):
        fullpath = os.path.join(config.appDir, 'data', charset, filename)
        try:
            #self.stats.append(segmenter.Statistics(fullpath, 'tab', keyword, charset))
            stat = segmenter.Statistics(fullpath, 'tab', charset)
            self.stats[filename] = stat
            self.statFiles[filename] = stat.statisticType
            self.addMessage("Loaded extra column data file %s/%s" % (charset, filename))
        except IOError as xxx_todo_changeme:
            (errno, strerror) = xxx_todo_changeme.args
            self.addMessage("**Failed to load data file %s: %s" % (fullpath, strerror))

    def ReadFiles(self, filelist):
        # Autodetect the encoding, so that the user doesn't need to worry about utf8 vs. utf16, little endian, etc
        # uses the chardet module from:
        # http://chardet.feedparser.org/
        # Universal Encoding Detector: character encoding auto-detection in Python
        import chardet

        text = ''
        filelist.sort()
        for f in filelist:
            try:
                #text += '%s [%s]\n%s' % (segmenter.Segmenter.sectionBreakChar, f, unicode(open(f, 'r').read(), encoding))
                rawdata = open(f, 'rb').read(-1)

                detector = chardet.detect(rawdata)
                self.addMessage("File %s loaded: %i bytes" % (f.encode('utf-8'), len(rawdata)))
                self.addMessage("Detected encoding: %s\n" % detector)
                text += '%s [%s]\n%s' % (segmenter.Segmenter.sectionBreakChar, f, str(rawdata, detector["encoding"]))
            except UnicodeDecodeError as e:
                self.addMessage("%s error while loading file %s: failed to decode from encoding '%s'. Filesize was %d" % (type(e), f, detector["encoding"], len(rawdata)))
                
        
        self.text = text
        return self.text

    def SummarizeResults(self, updatefunction=None):
        self.summary = ''
        self.results = []

        self.addMessage("Analyzing text ...")

        self.summary += "Length of text = %d" % len(self.text) + "\n"
        results = self.seg.segment(self.text, updatefunction, None) #"ReversedLongestMatch"
        self.summary += "Results.tokens (%d)" % len(results.tokens) + "\n"

        self.tokens = ' | '.join(t.text for t in results.tokens)

        wordctGross = 0
        wordctNet = 0
        wordUniqueGross = 0
        wordUniqueNet = 0

        for lex in results.lexList:
            word = results.words[lex.text]
            if word == None:
                continue
            else:
                wordctGross += len(lex.indexes)
                wordUniqueGross += 1
                if lex.text not in self.filterwords:
                    freq_per_million = 0
                    try:
                        freq_per_million = float(word.getStatistic('Word freq-Leeds internet corpus'))
                    except:
                        pass

                    pinyin = convertPinyin(word.definition.pinyin)
                    english = word.definition.english
                    count_in_corpus = len(lex.indexes)

                    self.results.append(RachelsCategories(datetime.datetime.now(), lex.text, pinyin, english, freq_per_million, count_in_corpus))

        
        self.summary += "\n\nTotal count of Chinese words in text: %d" % wordctGross + "\n"
        self.summary += "Total count of filtered Chinese words: %d" % wordctNet + "\n"
        self.summary += "\nTotal count of unique Chinese words: %d" % wordUniqueGross + "\n"
        self.summary += "Total count of unique filtered Chinese words: %d" % wordUniqueNet + "\n"

        # Sort results by count_in_corpus, then by freq_per_million
        self.results.sort(key=lambda x: (x.count_in_corpus, x.freq_per_mil), reverse=True)

    def GetFileItems(self, directory):
        import stat

        choices = []
        for filename in os.listdir(directory):
            try:
                st = os.stat(os.path.join(directory, filename))
            except os.error:
                continue
            if stat.S_ISREG(st.st_mode):
                choices.append(filename)
        return choices

class RachelsCategories:
    # Separate with pipes since text can have spaces, commas, semicolons, slashes
    csv_header = "date\toriginal_word\tpinyin\tenglish\tfreq_per_mil\tcount_in_corpus"
    def __init__(self, date, orig_word, pinyin, english, freq_per_mil, count_in_corpus):
        self.date = date
        self.orig_word = orig_word
        self.pinyin = pinyin
        self.english = english
        self.freq_per_mil = freq_per_mil
        self.count_in_corpus = count_in_corpus

    def is_valid(self):
        return self.orig_word != '' and self.pinyin != '' and self.english != ''

    def csv_line(self):
        return '{}\t{}\t{}\t{}\t{}\t{}'.format(self.date.strftime("%b %d %Y"), self.orig_word, self.pinyin, self.english, self.freq_per_mil, self.count_in_corpus)

    def __repr__(self):
        return self.csv_line()

# Pinyin numbers to tone marks. From https://stackoverflow.com/questions/8200349/convert-numbered-pinyin-to-pinyin-with-tone-marks
import re

pinyinToneMarks = {
    u'a': u'āáǎà', u'e': u'ēéěè', u'i': u'īíǐì',
    u'o': u'ōóǒò', u'u': u'ūúǔù', u'ü': u'ǖǘǚǜ',
    u'A': u'ĀÁǍÀ', u'E': u'ĒÉĚÈ', u'I': u'ĪÍǏÌ',
    u'O': u'ŌÓǑÒ', u'U': u'ŪÚǓÙ', u'Ü': u'ǕǗǙǛ'
}

def convertPinyinCallback(m):
    tone=int(m.group(3))%5
    r=m.group(1).replace(u'v', u'ü').replace(u'V', u'Ü')
    # for multple vowels, use first one if it is a/e/o, otherwise use second one
    pos=0
    if len(r)>1 and not r[0] in 'aeoAEO':
        pos=1
    if tone != 0:
        r=r[0:pos]+pinyinToneMarks[r[pos]][tone-1]+r[pos+1:]
    return r+m.group(2)

def convertPinyin(s):
    return re.sub(r'([aeiouüvÜ]{1,3})(n?g?r?)([012345])', convertPinyinCallback, s, flags=re.IGNORECASE)