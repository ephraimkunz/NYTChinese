import re
from segmenter import CJK, SegmenterResults
from segmenter.plugins import SegmentMethodPlugin

cls = "SegmentMethodReverseLongest"

class SegmentMethodReverseLongest(SegmentMethodPlugin):

    key = "ReversedLongestMatch"
    name = "Reversed longest match"
    description = "Longest matching, working backward from the end of the text"

    def __init__(self):
        pass

    def segment(self, segmenter, text, updatefunction=None):
        if segmenter.tokenMatchType == 'cjk':
            tokenPattern = ''.join((CJK.cjkUnifiedIdeographs, CJK.cjkUnifiedIdeographsExtA, CJK.cjkMiddleDot, CJK.cjkKatakanaMiddleDot, CJK.cjkLingZero, CJK.cjkBopomofo, segmenter.sectionBreakChar))
        elif segmenter.tokenMatchType == 'cjk_plus_az':
            tokenPattern = ''.join((CJK.cjkUnifiedIdeographs, CJK.cjkUnifiedIdeographsExtA, CJK.cjkMiddleDot, CJK.cjkKatakanaMiddleDot, CJK.cjkLingZero, CJK.cjkFullwidthLatin, CJK.cjkBopomofo, segmenter.sectionBreakChar))
        else:
            #TODO add a self.messages and display it in the log tab
            #print "Unknown token match type %s" % self.tokenMatchType
            return None

        notTokenPattern = "[^%s]+$" % tokenPattern
        sectionBreakPattern = segmenter.sectionBreakPattern + "$"

        results = SegmenterResults(text=text)
        length = len(text)
        idx = length - 1

        while idx > 0:
            if updatefunction:
                updatefunction((length - idx) * 100 / length)
            m = re.search(notTokenPattern, text[0:idx + 1])
            if m:
                results.addLexical(m.group(0), idx - len(m.group(0)), isCJK=False)
                idx -= len(m.group(0))
                continue
            m = re.search(sectionBreakPattern, text[0:idx + 1])
            if m:
                results.addLexical(m.group(0), idx - len(m.group(0)), segmenter.getWord(m.group(0)), isCJK = True)
                idx -= len(m.group(0))
                
            else:
                #j = (length - idx) if (idx + 8 > length) else 0
                j = idx - 8 if idx - 8 > 0 else 0
                while j < idx:
                    tmpword = text[j:idx + 1]
                    if segmenter.getWord(tmpword):
                        results.addLexical(tmpword, j, segmenter.getWord(tmpword), isCJK=True)
                        ###results.addWord(tmpword, segmenter.getWord(tmpword))
                        idx = j - 1
                        #continue
                        j = idx + 1 # No *&^*@# labeled loops in Python
                        continue
                    j += 1

                if j == idx:
                    'TODO can this be folded with the loop above?'
                    tmpword = text[idx:idx+1]
                    results.addLexical(tmpword, idx, segmenter.getWord(tmpword), isCJK=True)
                    '''this is an unknown word; i.e., a token with no associated dictionary word'''
                    idx -= 1
        
        results.tokens.reverse()
        results.lexList.reverse()
        print "<SegmenterResults>\n\ttokens = %d,\n\tlexList = %d,\n\tlexicals = %d,\n\twords = %d\n\tSentences = %d" % ( len(results.tokens), len(results.lexList), len(results.lexicals), len(results.words), len(results.sentences))  

        segmenter.segmentBySentence(results, text)
        print "<SegmenterResults>\n\ttokens = %d,\n\tlexList = %d,\n\tlexicals = %d,\n\twords = %d\n\tSentences = %d" % ( len(results.tokens), len(results.lexList), len(results.lexicals), len(results.words), len(results.sentences))  
        return results
