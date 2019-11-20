import os, sys, csv

import datafetch
from segmenterhelper import SegmenterHelper, RachelsCategories
from config import Config

NUM_NEW_WORDS_PER_RUN = 20
INPUT_FILE_PATH = os.path.expanduser("/tmp/corpus.txt")
OUTPUT_FILE_PATH = os.path.expanduser("~/Desktop/out.tsv")
CONFIG_FILE_PATH = "config.db"

def dedupe_and_dump_results(segHelper):
    try:
        all_words = set()

        if os.path.exists(OUTPUT_FILE_PATH):
            print ("Found existing wordlist file, reading list...")
            with open(OUTPUT_FILE_PATH, 'r+') as tsvfile:
                reader = csv.DictReader(tsvfile, dialect='excel-tab')
                for row in reader:
                    all_words.add(row["original_word"])

        with open(OUTPUT_FILE_PATH, 'a+') as tsvfile:
            if len(all_words) == 0:
                print ("Starting new word list file...")
                tsvfile.write(RachelsCategories.csv_header)

            new_words = []

            print("Deduping wordlists, writing to file...")
            for word in segHelper.results:
                if word.orig_word not in all_words:
                    new_words.append(word)

                if len(new_words) == NUM_NEW_WORDS_PER_RUN:
                    break

            tsvfile.write("\n")
            results = '\n'.join([str(x) for x in new_words])
            tsvfile.write(results)
    except (OSError, IOError) as e:
        print("Warning: Failed to write to output file {}: {}".format(OUTPUT_FILE_PATH, e))
    
def main():
    # Fetch Chinese text and write to input file
    print("NYT Chinese Word Extractor\nBy Ephraim Kunz\n\n")

    print("Fetching text from cn.nytimes.com...")
    text = datafetch.get_concatenated_text()

    print("Writing fetched text to temporary file...")
    with open(INPUT_FILE_PATH, 'w+') as input_file:
        input_file.write(text)

    # Build SegmenterHelper
    print("Loading configurations, dictionaries, wordlists...")
    runningDir=os.path.dirname(os.path.abspath(__file__))
    segHelper = SegmenterHelper(runningDir)

    # Run the segmenter
    config = Config(str(os.path.abspath(CONFIG_FILE_PATH)))
    config.appDir = segHelper.runningDir

    segHelper.config = config
    segHelper.LoadData()
    segHelper.LoadKnownWords()
    segHelper.LoadExtraColumns()

    print("Reading fetched text from temporary file...")
    segHelper.ReadFiles( [INPUT_FILE_PATH])

    segHelper.SummarizeResults()

    print("\n")
    print(segHelper.summary)

    # Dedup words and write new output file
    print("Deduping results and dumping new wordlist file...")
    dedupe_and_dump_results(segHelper)

    print("Done! Output file written to {}".format(OUTPUT_FILE_PATH))

    input("Press enter to exit...")

if __name__ == "__main__":
    main()