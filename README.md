# NYTChinese
Extract top articles from Chinese NYT and create lists of words for practice.
Everything is running on Python 3.7.

To package for distribution:
`sudo pyinstaller main.spec`. The result is the `dist` folder with a main folder + main binary inside.

However, just double-clicking the `main` binary probably will open a terminal with the wrong cwd. You 
need to either execute it after navigating to it's containing folder via the commandline, or create a 
script that does `cd -- "$(dirname "$BASH_SOURCE")"` right after the shebang and before calling `main`.
I've included a file that does this that should be copied into the same directory as the main executable 
called DoubleClickMe.command. You can do all of the above and package a nice zip file with `./createZip`.

## Instructions I gave Rachel for setup:
One time setup
1. Download the zip file here: https://gofile.io/?c=adK4dX
2. Open the folder that downloaded.
3. Open Terminal: command + space, type terminal, select the black terminal app.
4. Enter this in terminal: cd ~/Downloads/main && chmod +x DoubleClickMe.command
5. It will probably want your password. Type it in (no letters will show).
6. Close terminal.

Every time
1. Double click “DoubleClickMe.command”
2. The updated out.tsv file will be written to the Desktop.
3. You can open this file in Excel. Open Excel.
4. command + o
5. Check the Delimited box. Under File Origin select “Unicode (UTF - 8)”. Click next.
6. Tab should be the only delimiter selected. Click Next -> Finish

Each time you run DoubleClickMe.command, it will fetch the article data from NYT at that moment and open this file, adding 20 more unique words to the end. So don’t move it from the Desktop or else it will create new one, starting over (and forgetting words you’ve seen before).

## Example Output
A tab separated value file is produced / appended to. Here's the format of the file:

date | original_word | pinyin | english | freq_per_mil | count_in_corpus
--- | --- | --- | --- | --- | ---
Nov 19 2019 | 香港 | Xiāng gǎng | Hong Kong | 187.0 | 50
Nov 19 2019	| 特	| tè | special/unique/distinguished/especially/unusual/very |	237.0 |	32
Nov 19 2019 |	朗	| lǎng	| clear/bright |	15.0	| 31
Nov 19 2019 |	普 |pǔ |	general/popular/everywhere/universal |	58.0 |	30

## Original Workflow / Specs
From Rachel Finlayson via email: "I've been wanting to create a spreadsheet that "reads" the top 5 articles in the World section of the New York Times in Chinese for the past week (https://cn.nytimes.com/world/) and creates one 20-word vocabulary list based on the most commonly used words in those articles. Ideally the next week, when it makes a new 20-character list, it "reads" the past list(s) and ignores any repeats from past weeks in choosing the next top 20.

I found this tool that makes the kind of list I'd want when you paste text in. -  http://www.zhtoolkit.com/apps/wordlist/create-list.cgi?rm=makevocabform
It reads pasted text and creates the categories I want in the vocabulary list which are Original word, Pinyin-tone marks, English, Freq. per 1 million words, No. occurrences. It even is smart enough to know when characters are part of word sets, idioms, or are meant to be on their own (some tools I've seen only look at unique characters, so for example instead of 可以they list 可 and 以 on their own, which isn't helpful).

The flow manually: go to the NYT website and highlight/copy/paste from five articles to input text, go to the Chinese dictionary website above, select the output options, take the top 20 and copy-paste into an Excel, reading it myself to see which words are repeated from prior weeks. It would be cool to figure out a way to do that automatically if that's possible."

## Credits
The Chinese segmentation code, word frequency, and dictionary information all comes from source code that originally powered http://www.zhtoolkit.com/apps/chinese_word_extractor/. Source code is here: https://github.com/cer28/ChineseWordExtractor

I used [PyInstaller](https://www.pyinstaller.org) to package all the code for distribution.
