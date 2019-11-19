'''
Created on Jun 20, 2012

@author: cer28

Step 1_NO: Download the latest Unihan database (Unihan.zip) from http://www.unicode.org/Public/UNIDATA/ (this is not current)
Step 1_YES: Download the latest Unihan database (Unihan.zip) from ftp://unicode.org/Public/6.2.0/ucd/
Step 2: Extract
 
 
http://unicode.org/faq/han_cjk.html
Q: What's the best way to find out how to pronounce an ideograph in Mandarin?

A: The best way is to use the kHanyuPinlu, kXHC1983, and kHanyuPinyin fields in
that order. The kMandarin field may have some readings the other three do not but
should be used with caution. The kHanyuPinlu field lists the most common readings
for ideographs in order of frequency of use and is the most useful for most
purposes. The kXHC1983 field contains the most important readings for characters
in modern use, and the kHanyuPinyin field contains an exhaustive set of readings
for a large set of characters, but includes obscure readings of historic interest
only.

'''

import os
import sys
import re

#unihanDir = 'G:/Home/Chinese/Dictionaries/Unihan/Unihan-2011-08-08'
unihanDir = 'G:/Home/Chinese/Dictionaries/Unihan/unicode.org_Public_6.2.0_ucd/Unihan'

filename = os.path.join(unihanDir, "Unihan_Readings.txt")

#TODO handle u:
#TODO handle m and ng (which are not really valid because they are Cantonese or other)
tones = {
         "\u0101":("a", "1"),
         "\u00e1":("a", "2"),
         "\u01ce":("a", "3"),
         "\u00e0":("a", "4"),
         "\u0113":("e", "1"),
         "\u00e9":("e", "2"),
         "\u011b":("e", "3"),
         "\u00e8":("e", "4"),
         "\u012b":("i", "1"),
         "\u00ed":("i", "2"),
         "\u01d0":("i", "3"),
         "\u00ec":("i", "4"),
         "\u014d":("o", "1"),
         "\u00f3":("o", "2"),
         "\u01d2":("o", "3"),
         "\u00f2":("o", "4"),
         "\u016b":("u", "1"),
         "\u00fa":("u", "2"),
         "\u01d4":("u", "3"),
         "\u00f9":("u", "4"),
         "\u01d6":("v", "1"),
         "\u01d8":("v", "2"),
         "\u01da":("v", "3"),
         "\u01dc":("v", "4"),
         "\u0100":("A", "1"),
         "\u00c1":("A", "2"),
         "\u01cd":("A", "3"),
         "\u00c0":("A", "4"),
         "\u0112":("E", "1"),
         "\u00c9":("E", "2"),
         "\u011a":("E", "3"),
         "\u00c8":("E", "4"),
         "\u012a":("I", "1"),
         "\u00cd":("I", "2"),
         "\u01cf":("I", "3"),
         "\u00cc":("I", "4"),
         "\u014c":("O", "1"),
         "\u00d3":("O", "2"),
         "\u01d1":("O", "3"),
         "\u00d2":("O", "4"),
         "\u016a":("U", "1"),
         "\u00da":("U", "2"),
         "\u01d3":("U", "3"),
         "\u00d9":("U", "4"),
         "\u01d5":("V", "1"),
         "\u01d7":("V", "2"),
         "\u01d9":("V", "3"),
         "\u01db":("V", "4"),
         }

tonestring = "".join(list(tones.keys()))


def Tone2Number(tonepy):
    m = re.match("^([^%s]*)([%s])([^%s]*)$" % (tonestring, tonestring, tonestring), tonepy)
    if m and tones.get(m.group(2)):
        newpy = m.group(1) + tones.get(m.group(2))[0] + m.group(3) + tones.get(m.group(2))[1] 
    else:
        newpy = tonepy
        #sys.exit(9)

    return re.sub("\u00fc", "u:", newpy)

try:
    fh = open(filename)  #throws IOError
    lines = str(fh.read()).splitlines()
    fh.close()
except (IOError) as e:
    print("Error: Failed to load source file %s: %s" % (filename, e.message))
    sys.exit(1)

pinyin = {}
defs = {}

for line in lines:
    m = re.match('U\+([^\s]+)\s+kMandarin\s+(.*)', line)
    if m:
        left = m.group(1)
        right = m.group(2)

        py = right.split(",")
        right = "; ".join([Tone2Number(py1) for py1 in py])
        pinyin[left] = right
        print(right.encode("utf-8"))

for line in lines:
    m = re.match('U\+([^\s]+)\s+kHanyuPinyin\s+(.*)', line)
    if m:
        left = m.group(1)
        right = m.group(2)
        m = re.match('.*?:(.*)', right)
        if m:
            right = m.group(1)
            py = right.split(",")
            right = "; ".join([Tone2Number(py1) for py1 in py])
        pinyin[left] = right
 
for line in lines:
    m = re.match('U\+([^\s]+)\s+kXHC1983\s+(.*)', line)
    if m:
        left = m.group(1)
        right = m.group(2)
        py = re.findall('.*?:([^ ]+)', right)
        right = "; ".join([Tone2Number(py1) for py1 in py])
        pinyin[left] = right

for line in lines:
    m = re.match('U\+([^\s]+)\s+kHanyuPinlu\s+(.*)', line)
    if m:
        left = m.group(1)
        right = m.group(2)
        right = re.sub("\u00fc", "u:", right)
        py = re.findall('(.*?)\(\d+\) ?', right)
        right = "; ".join(py)
        pinyin[left] = right

for line in lines:
    m = re.match('U\+([^\s]+)\s+kDefinition\s+(.*)', line)
    if m:
        left = m.group(1)
        right = m.group(2)
        defs[left] = right


# There are more pinyin than defs, so use those keys as the better list
codepoints = list(pinyin.keys())
codepoints.sort()

fh = open("../dict/chardict-unihan_readingsX.u8", "w")

for cp in codepoints:
    if int(cp, 16) < 65536:
        fh.write(" ".join([chr(int(cp, 16)), chr(int(cp, 16)), "[" + pinyin.get(cp) + "]", "/" + (defs.get(cp) or '<no definition>') + "/"]).encode('utf-8'))
        fh.write("\n")
