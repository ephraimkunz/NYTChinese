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

Let me know if you have any problems or questions.
