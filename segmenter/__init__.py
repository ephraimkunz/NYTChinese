'''
Copyright 2011 by Chad Redman <chad at zhtoolkit.com>
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
'''

import re, os
from segmenter.plugins import SegmentMethodPlugin

class CJK:
    #http://en.wikipedia.org/wiki/CJK_Unified_Ideographs
    cjkUnifiedIdeographs = '\u4E00-\u9FFF'
    cjkUnifiedIdeographsExtA = '\u3400-\u4DBF'
    #cjkUnifiedIdeographsExtB = u'\u20000-2A6DF'
    #cjkEnclosedLettersAndMonths = u'\u3200-\u32FF'
    cjkCompatibilityIdeographs = '\uF900-\uFAFF'
    
    #Non-CJK characters used in simplified/traditional field 
    #Some of these are covered in Halfwidth and Fullwidth Forms. But this makes a stricter filter
    cjkMiddleDot = '\u00B7'
    cjkFullwidthComma = '\uFF0C'
    cjkLingZero = '\u3007'
    cjkFullwidthLatin = '\uFF21-\uFF3A\uFF41-\uFF5A'
    cjkKatakanaMiddleDot = '\u30FB'
    
    #Bopomofo and zhuyin
    cjkBopomofo = '\u3105-\u312D\u31A0-\u31A5\u02EA\u02EB\u02CA\u02C7\u02CB\u02D9'


class DictionaryWord:
    '''
    A single word of a dictionary, with expression, reading, and meaning
    '''

    simplified = None
    traditional = None
    pinyin = None
    english = None

    def __init__(self, traditional, simplified, pinyin, english):
        '''
        Constructor
        '''
        self.simplified = simplified
        self.traditional = traditional
        self.pinyin = pinyin
        self.english = english
    
    def __str__(self):
        return '%s\t%s\t%s\t/%s/' % (self.traditional, self.simplified, self.pinyin, self.english)




class Dictionary:
    '''
    Parses a file containing lexical entries
    '''

    formatTypes = ('cedict', 'edict', 'sqlite3', 'tab')
    characterTypes = ('simplified', 'traditional')

    def getWordCount(self):
        return len(self.words)

    def readCedictLine(self, line, lineno):
        if re.match('\\s*#', line):
            #A comment line
            return None

        cjkRange = '%s%s%s%s%s%s%s%s' % (CJK.cjkKatakanaMiddleDot, CJK.cjkFullwidthComma, CJK.cjkLingZero, CJK.cjkUnifiedIdeographsExtA, CJK.cjkUnifiedIdeographs, CJK.cjkCompatibilityIdeographs, CJK.cjkFullwidthLatin, CJK.cjkBopomofo)

        # Allow semicolons in pinyin, because the chardict has them that way
        #pat = u'([%s]+)[ \t]([%s]+)[ \t]\[([a-zA-Z0-9,\xb7: ]+)\][ \t]/(.*)/\s*$' % (cjkRange, cjkRange)
        pat = '([%s]+)[ \t]([%s]+)[ \t]\[([a-zA-Z0-9,\xb7:; ]+)\][ \t]/(.*)/\s*$' % (cjkRange, cjkRange)

        m = re.match(pat, str(line))
        if m:
            return DictionaryWord(m.group(1),m.group(2),m.group(3),m.group(4))
        else:
            if self.verbose:
                self.messages.append('Warning: Invalid CEDICT entry in line %d of %s: "%s"' % (lineno, self.filename, str(line)))
                
            return None

    def readEdictLine(self, line, lineno, character):
        if re.match('\\s*#', line):
            #A comment line
            return None

        cjkRange = '%s%s%s%s%s%s%s%s' % (CJK.cjkKatakanaMiddleDot, CJK.cjkFullwidthComma, CJK.cjkLingZero, CJK.cjkUnifiedIdeographsExtA, CJK.cjkUnifiedIdeographs, CJK.cjkCompatibilityIdeographs, CJK.cjkFullwidthLatin, CJK.cjkBopomofo)

        pat = '([%s]+) \[([a-zA-Z0-9,\xb7: ]+)\] /(.*)/\s*$' % (cjkRange, cjkRange)

        m = re.match(pat, str(line))
        if m:
            if character == 'simplified':
                return DictionaryWord(m.group(1), None, m.group(2), m.group(3))
            elif character == 'traditional':
                return DictionaryWord(None, m.group(1), m.group(2), m.group(3))
        else:
            if self.verbose:
                self.messages.append('Warning: Invalid EDICT entry in line %d of %s: "%s"' % (lineno, self.filename, str(line)))
            return None

    def readCedictFile(self,filename,updatefunction):
        '''
        The CEDICT format is traditional simplified [pinyin] english
        throws: IOError
        '''
        progresspct = 0
        try:
            filebytes = os.path.getsize(filename)
            fh = open(filename)  #throws IOError
        except (OSError, IOError) as e:
            print("Warning: Failed to load dictionary %s: %s" % (filename, e))
            return
        try:
            lineno = 0
            for line in fh.read().splitlines():
                lineno += 1
                # This doesn't exactly equal 100% due to unicode vs. byte comparisons
                progresspct += len(line)*100.0/filebytes
                if updatefunction and progresspct > 0:
                    updatefunction(progresspct)

                #if lineno > 100: break  #TODO temp debugging delete
                word = self.readCedictLine(line, lineno)
                if word != None:
                    self.words.append(word)
        finally:
            fh.close()
        

    def readEdictFile(self, filename, character):
        '''
        The EDICT format is chinese [pinyin] english
        throws: IOError
        '''
        fh = open(filename)  #throws IOError
        try:
            lineno = 0
            for line in fh.read().splitlines():
                lineno += 1
                if lineno > 100: break  #TODO temp debugging delete
                word = self.readEdictLine(line, lineno, character)
                if word != None:
                    self.words.append(word)
        finally:
            fh.close()
        
    def readTabFile(self, filename):
        '''
        The tab format is traditional simplified pinyin english
        The field format is roughly the same as CC-CEDICT, but less strict in matching 
        throws: IOError
        '''
        fh = open(filename)  #throws IOError
        try:
            lineno = 0
            for line in fh.read().splitlines():
                line = str(line)
                if re.match('\\s*#', line):
                    # These are comment lines
                    continue
                ar = line.split('\t')
                if len(ar) == 4:
                    # TODO change ar[0]..., what's the correct way?
                    word = DictionaryWord(ar[0], ar[1], ar[2], ar[3])
                    if word:
                        self.words.append(word)
                else:
                    if self.verbose:
                        self.messages.append('Warning: Invalid tab entry in line %d of %s: "%s"' % (lineno, self.filename, str(line)))

                lineno += 1
        finally:
            fh.close()

    def __init__(self, filename, format, character=None, dataType = 'words', description=None, tag=None, verbose=False, updatefunction=None):
        '''
        Constructor
        '''

        self.words = []
        self.messages = []
        self.filename = filename
        if not format in self.formatTypes:    # why does this say formatTypes is not defined
            self.messages.append("Unknown dictionary format %s" % format)
            raise Exception("Unknown dictionary format %s" % format)
        else:
            self.format = format

        self.dataType = dataType

        if description == None:
            self.description = self.filename
        else:
            self.description = description

        self.tag = tag
        self.verbose = verbose

        if (format == 'cedict'):
            self.readCedictFile(filename, updatefunction)
        elif (format == 'edict'):
            if not character in self.characterTypes:
                self.messages.append("Dictionary format 'edict' requires to define traditional/simplified")
                raise Exception("Dictionary format 'edict' requires to define traditional/simplified")
            self.readEdictFile(filename, character)
        elif (format == 'tab'):
            self.readTabFile(filename)
        else :
            self.messages.append("Unknown dictionary format '%s'" % format)
            raise Exception("Unknown dictionary format '%s'" % format)

    def __str__(self):
        return 'Dictionary %s (%s), %d Entries' % (self.description, self.filename, len(self.words))



class Statistics:
    '''
    For the storage of a list of words and an associated value
    '''
    characterSets = ('simplified', 'traditional', 'combined')
#    statisticsTypes = ('hsk_level', 'frequency_per_million', 'is_chengyu')
    formatTypes = ('tab')

    class Statistic:
        def __init__(self, word, value):
            self.word = word
            self.value = value

    def __init__(self, filename, formatType, character):
        '''note: charset 'combined' here means 3 columns: trad-expression simp-expression value
           Charsets traditional or simplified means that the columns are expression value
           TODO: make statistics type a list so that multiple fields can be defined 
        '''
        self.statisticType = filename

        if not character in self.characterSets:
            raise Exception("Unknown character type %s" % character)
        self.character = character

        if not formatType in self.formatTypes:
            raise Exception("Unknown formatType %s" % formatType)
        self.formatType = formatType
        
        self.filename = filename

        self.words = []
        fh = open(self.filename)  #throws IOError
        try:
            curline = 0
            for line in fh.read().splitlines():
                curline +=1
                line = str(line)
                if formatType == 'tab':
                    m = re.match('^# Heading: ', line)
                    if m:
                        self.statisticType = line[m.end():]
                        continue
                    if re.match('\\s*#', line):
                        # These are comment lines
                        continue
                    ar = line.split('\t')
                    if len(ar) >= 2:
                        self.words.append(self.Statistic(ar[0], ar[1]))
                    else:
                        #TODO add self.messages to pass errors to the message tab
                        #self.messages.append("Warning: statistic in %s, line %d is missing a value" % (self.filename, curline))
                        pass
                    
        finally:
            fh.close()

    def __repr__(self):
        return "<Statistics> Filename '%s', heading '%s', %d entries" % (self.filename, self.statisticType, len(self.words)) 


class SegmenterResults:
    '''
    Stores results of segmentation
    '''
    
    class Token:
        def __init__(self, text, index):
            self.text = text
            self.index = index
            
        def __repr__(self):
            return "<Token> '%s' (%d)" % (self.text, self.index)
            
    class Lexical:
        def __init__(self, text):
            self.text = text
            self.indexes = []
        
        def __repr__(self):
            return "<Lexical> %s (%d tokens)" % (self.text, len(self.indexes))

    class Sentence:
        def __init__(self, text, idx):
            self.text = text
            self.start_idx = idx
            self.end_idx = idx + len(text) - 1

        def contains(self, idx):
            return (idx >= self.start_idx and idx <= self.end_idx)

        def __repr__(self):
            return "<Sentence> (index %d -> %d) %s" % (self.start_idx, self.end_idx, self.text)

    def __init__(self, text):
        self.text = text
        self.tokens = []     #  : Token[]
        self.lexList = []    # : Lexical[]. The unique Chinese words in the order of first index (shadowing lexicals for performace) 
        self.lexicals = {}       # : {string => Lexical} 
        self.words = {}       # : {string => Segmenter::Word} 
        self.sentences = []   # : Sentence[] 
        # note words are only set when the Segmenter had it in it's dictionary. So it's not for foreign words
        
        self.debugCountSize = 0

    def __str__(self):
        return "<SegmenterResults>\n\ttokens = %s,\n\tlexList = %s,\n\tlexicals = %s,\n\twords = %s" % (self.tokens, self.lexList, self.lexicals, self.words)  

    def filterWords(self, wordArray):
        pass

    def addSentence(self, text, position):
        lex = self.Sentence(text, position)
        #print "Found sentence: %s" % lex
        self.sentences.append(lex)

    def addLexical(self, text, position, segword=None, isCJK=True):
        'public method called by Segmenter.'
        self.debugCountSize += len(text)
        if self.debugCountSize > 1000:
            #print "#",
            self.debugCountSize = 0

        self.tokens.append(self.Token(text, position))

        #if segword != None:
        if isCJK:
            'lexicals are Chinese words, so only store them when a definition (Segmenter::Word) exists for them'
            lex = None  #TODO need this?

            if text in self.lexicals and segword.__class__.__name__ != 'SectionBreakWord':
                'we want to add all section breaks to the word list, not just the first instance'
                lex = self.lexicals[text]
            else:
                lex = self.Lexical(text)
                self.lexicals[text] = lex
                self.lexList.append(lex)
                #if segword != None:
                if True:
                    self.words[text] = segword

            lex.indexes.append(position)

    def findFirstSentence(self, lex):
        for sentence in self.sentences:
            if sentence.contains(lex.indexes[0]):
                m = re.search(lex.text, sentence.text)
                result = "*ERROR: Sentence not found"
                if m:
                    result = sentence.text[:m.start()] + '*' + sentence.text[m.start():m.end()] + '*' + sentence.text[m.end():]  
                else:
                    result = sentence.text
                # do a cheap escape of initial quote, in case importing into Excel
                if result[0] == '"':
                    return ' ' + result
                else:
                    return result
        #return None
        return ''

class Segmenter:
    '''
    This class parses dictionaries and statistics files, and stores the resulting
    lexical entries. It then can accept any arbirtary text, parse it into tokens,
    and return the result set to the caller
    '''

    characterSets = ('simplified', 'traditional', 'combined')  ## NOTE not yet sure if combined logically will work
    #TODO refactor segmentationMethods into plugin arch
    segmentationMethods = ('simpleLongestMatch', 'longestMatchPlusTransliterations', 'longestMatchPlusTranslitPlusChNames')
    tokenMatchTypes = ('cjk', 'cjk_plus_az')
    #at some point maybe this can converted to an open text tag, or a mutable list
    dictionaryOperationTypes = ('replace', 'append', 'addifempty')
    dataTypes = ('words', 'chinese_names', 'foreign_names', 'chinese_place_names', 'chengyu')

    sectionBreakChar = '\u00A7' #(Section Sign)
    sectionBreakPattern = "%s\\s*(\\[([^\\]]*)\\])?" % sectionBreakChar


    class Word:
        '''
        A general word class. Type is EITHER simplified or traditional. Stores
        multiple trad/simp/pinyin/english, and the dictionary source it was found in
        '''
    
        def __init__(self, key, character):
            self.key = key
            self.character = character  #TODO check the value
            self.stats = {}
            self.definitions = []
            self.definition = DictionaryWord(None, None, None, None)
    
        def isSectionBreak(self):
            return False

        def addStatistic(self, statisticType, value):
            #TODO make sure we're adding for the right charSet
            self.stats[statisticType] = value
            
        def getStatistic(self, statisticType):
            #TODO make sure we're adding for the right charSet
            return self.stats[statisticType] if statisticType in self.stats else '' 

        def addDictionaryWord(self, dictWord, operationType):
            #TODO make sure we're adding for the right charSet
            #TODO handle operation types. For now, just default to append
            self.definitions.append(dictWord)

#        def addDefinition(self, dictWord, operationType):
#            if operationType == 'replace':
#                self.definition.simplified = dictWord.simplified
#                self.definition.traditional = dictWord.traditional
#                self.definition.pinyin = dictWord.pinyin
#                self.definition.english = dictWord.english
            
        def mergeDefinitions(self):
            simp = []
            trad = []
            pinyin = []
            english = []
            
            for d in self.definitions:
                if d.simplified not in simp:
                    simp.append(d.simplified)
                if d.traditional not in trad:
                    trad.append(d.traditional)
                if d.pinyin not in pinyin:
                    pinyin.append(d.pinyin)
                if d.english not in english:
                    english.append(d.english)

    
            self.definition.simplified = '; '.join(simp)
            self.definition.traditional = '; '.join(trad)
            self.definition.pinyin = '; '.join(pinyin)
            self.definition.english = '; '.join(english)
    
        def getDefinition(self):
            #TODO make sure we're adding for the right charSet
            return self.definition.__str__()   # using str(self.definition) just gives: UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-1

        def __str__(self):
            return 'Word:\n\tkey=%s,\n\tcharacter=%s\n\tstatistics={%s}, definitions=[%s]' % (self.key, self.character, self.stats, self.definitions)

    class SectionBreakWord(Word):
        def __init__(self, key, character):
            Segmenter.Word.__init__(self, key, character)

        def isSectionBreak(self):
            return True

    def __init__(self, character, dictArray, statDict, method='simpleLongestMatch', tokenMatchType='cjk', dictionaryOperationType='replace', verbose=False):
        '''
        Constructor
        Note that the Segmenter knows whether to allow just CJK or CJK + A-Z,
        but the dictionary has it's own separate regexp for what is a valid character string.
        '''
        if not character in self.characterSets:
            raise Exception("Unknown character type '%s'" % character)
        else:
            self.character = character

        if not method in self.segmentationMethods:    # why does this say formatTypes is not defined
            raise Exception("Unknown segmentation method %s" % method)
        else:
            self.segmentationMethod = method

        if not tokenMatchType in self.tokenMatchTypes:    # why does this say formatTypes is not defined
            raise Exception("Unknown token match type %s" % tokenMatchType)
        else:
            self.tokenMatchType = tokenMatchType

        self.dictionaries = dictArray
        self.statistics = statDict
        self.verbose = verbose

        if not dictionaryOperationType in self.dictionaryOperationTypes:    # why does this say formatTypes is not defined
            raise Exception("Unknown dictionaryOperationType %s" % dictionaryOperationType)
        else:
            self.dictionaryOperationType = dictionaryOperationType

        self.loadPlugins("segmenter/plugins")

        self.words = {}
        self._buildWordList()
        self._buildStatistics()

    def setStatistics(self, statDict):
        self.statistics = statDict
        self._buildStatistics()

    def _buildWordList(self):
        for dict in self.dictionaries:
            'note: words in the same dictionary get merged, while words in different dictionaries are handled depending on dictionaryOperationType'
            for dictword in dict.words:
                if self.character in ('simplified', 'combined'):
                    #print word.simplified
                    self._addWord(dictword.simplified, dict.description, dictword)
                if self.character in ('traditional', 'combined'):
                    self._addWord(dictword.traditional, dict.description, dictword)
                    #print word.traditional
                else:
                    pass
        for word in self.words:
            self.getWord(word).mergeDefinitions()
        
        # if some wiseacre tries to define the section break, override it
        
        self.words[self.sectionBreakChar] = self.SectionBreakWord(self.sectionBreakChar, self.character) 

    def _buildStatistics(self):
        #TODO verify character set matches
        for statItem in list(self.statistics.values()):
            for stat in statItem.words:
                word = self.getWord(stat.word)
                if word:
                    word.addStatistic(statItem.statisticType, stat.value)



    def getWord(self, key, autoCreate=False):
        if not key in self.words:
            if autoCreate:
                self.words[key] = self.Word(key, self.character)
            else:
                return None

        return self.words[key]
        
        

    def _addWord(self, key, dict, word):
        '''
        The format of the words data structure is words{key} : Word
        Each Chinese word can be found in multiple dictionaries, and even in the same dictionary multiple times
        It will be up to output functions to format the data here into a compact formatted string
        '''

#        if not key in self.words:
#            self.words[key] = {}
#        
#        if not dict in self.words[key]:
#            self.words[key][dict] = []

        #self.getWord(key).[dict].append(word)
        self.getWord(key, True).addDictionaryWord(word, self.dictionaryOperationType)
        ###self.getWord(key, True).addDefinition(word, self.dictionaryOperationType)


    

    def segmentBySentence(self, segResults, text):

        # For now, we will assume no hard wrapping; i.e., linefeeds can mark the end of a sentence
        #notTokens = u"(([.!?????]+)|[ \t]{2,}|\s+)"
        notTokens = "(([\.!\?\"\uFF0E\u3002\uFF1F\uFF01\u201d]+)|[ \t]{2,}|\s+)"
        "Note: the stop delimiters are group 2; add these to the original sentence if found"

        idx = 0
        length = len(text)

        while idx < length:
#            m = re.match(notTokens, text[idx:])
#            if m:
#                segResults.addSentence(m.group(1), idx)
#                idx += len(m.group(1))
#                continue
            m = re.search(notTokens, text[idx:])
            if m:
                "There is a possible sentence, and a definite stopchar"
                tmptext = ''
                if m.start(1):
                    tmptext = text[idx:idx+m.start(1)]
                    if m.end(2) > 0:
                        "ending punctuation"
                        tmptext += m.group(2)
                    segResults.addSentence(tmptext, idx)
                if len(tmptext) != m.end(1):
                    segResults.addSentence(text[idx+len(tmptext):idx+m.end(1)], idx+len(tmptext))
                idx += m.end(1)
            else:
                "There is no stopchar, so the remaining text is the final sentence"
                segResults.addSentence(text[idx:], idx)
                idx = length
        
        return
    
    def segment(self, text, updatefunction=None, method=None):  #"ReversedLongestMatch"
        if method == None:
            return self.segmentMethodBuiltin(text, updatefunction)
        else:
            methods = {}
            for m in SegmentMethodPlugin.__subclasses__():
                methods[m.key] = m
            print(methods)
            cls = methods[method]
            seg = cls()
            return seg.segment(self, text, updatefunction)

    def segmentMethodBuiltin(self, text, updatefunction=None):
        if self.tokenMatchType == 'cjk':
            tokenPattern = ''.join((CJK.cjkUnifiedIdeographs, CJK.cjkUnifiedIdeographsExtA, CJK.cjkMiddleDot, CJK.cjkKatakanaMiddleDot, CJK.cjkLingZero, CJK.cjkBopomofo, self.sectionBreakChar))
        elif self.tokenMatchType == 'cjk_plus_az':
            tokenPattern = ''.join((CJK.cjkUnifiedIdeographs, CJK.cjkUnifiedIdeographsExtA, CJK.cjkMiddleDot, CJK.cjkKatakanaMiddleDot, CJK.cjkLingZero, CJK.cjkFullwidthLatin, CJK.cjkBopomofo, self.sectionBreakChar))
        else:
            #TODO add a self.messages and display it in the log tab
            #print "Unknown token match type %s" % self.tokenMatchType
            return None

        notTokenPattern = "[^%s]+" % tokenPattern

        results = SegmenterResults(text=text)
        idx = 0
        length = len(text)

        while idx < length:
            if updatefunction:
                updatefunction(idx * 100 / length)
            m = re.match(notTokenPattern, text[idx:])
            if m:
                results.addLexical(m.group(0), idx, isCJK=False)
                idx += len(m.group(0))
                continue
            m = re.match(self.sectionBreakPattern, text[idx:])
            if m:
                results.addLexical(m.group(0), idx, self.getWord(m.group(0)), isCJK = True)
                idx += len(m.group(0))
                
            else:
                j = (length - idx) if (idx + 8 > length) else 8
                while j > 1:
                    tmpword = text[idx:idx+j]
                    if self.getWord(tmpword):
                        results.addLexical(tmpword, idx, self.getWord(tmpword), isCJK=True)
                        ###results.addWord(tmpword, self.getWord(tmpword))
                        idx += j
                        #continue
                        j = -666 # No *&^*@# labeled loops in Python
                        continue
                    j-=1

                if j == 1:
                    'TODO can this be folded with the loop above?'
                    tmpword = text[idx:idx+1]
                    results.addLexical(tmpword, idx, self.getWord(tmpword), isCJK=True)
                    '''this is an unknown word; i.e., a token with no associated dictionary word'''
                    idx += 1
        
        self.segmentBySentence(results, text)
        return results

    def loadPlugins(self, pluginFolder):
        import sys
        loadedPlugins = []
        print(pluginFolder)
        if not os.path.exists(pluginFolder):
            print("Plugin folder does not exist")
            return loadedPlugins
        sys.path.insert(0, pluginFolder)
        #plugins = self.enabledPlugins()
        print(os.listdir(pluginFolder))
        plugins = [i for i in os.listdir(pluginFolder) if i.endswith(".py") and i != "__init__.py"]
        plugins.sort()
        for plugin in plugins:
            try:
                nopy = plugin.replace(".py", "")
                __import__(nopy)
                #self.addMessage("Plugin %s loaded" % (plugin))
                loadedPlugins.append(nopy)
                print("Segmenter plugin %s loaded" % (plugin))
                
            except:
                #print "Error in %s" % plugin
                print("Plugin %s failed to load: %s" % (plugin, sys.exc_info()[0]))
                import traceback
                traceback.print_exc()

