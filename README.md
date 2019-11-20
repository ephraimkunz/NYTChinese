# NYTChinese
Extract top articles from Chinese NYT and create lists of words for practice.
Everything is running on Python 3.7.

To package for distribution:
`sudo pyinstaller main.spec`. The result is the `dist` folder with a main folder + main binary inside.

However, just double-clicking the `main` binary probably will open a terminal with the wrong cwd. You 
need to either execute it after navigating to it's containing folder via the commandline, or create a 
script that does `cd -- "$(dirname "$BASH_SOURCE")"` right after the shebang and before calling `main`.
I've included a file that does this that should be copied into the same directory as the main executable 
called DoubleClickMe.command.
