from distutils.core import setup
import py2exe
from glob import glob

# from http://stackoverflow.com/questions/6378673/executable-made-with-py2exe-doesnt-run-on-windows-xp-32bit
#data_files = [("VC90", '..\Microsoft.VC90.CRT.manifest'),
#            ("VC90", '..\msvcm90.dll'),
#            ("VC90", '..\msvcp90.dll'),
#            ("VC90", '..\msvcr90.dll')
#]

data_files = [
	("data/simplified", glob(r"data/simplified/*")),
	("data/traditional", glob(r"data/traditional/*")),
	("dict", glob(r"dict/*")),
	("filter", glob(r"filter/*")),
	("samples", glob(r"samples/*")),
	(".", glob(r"Microsoft.VC90.CRT.manifest")),
	(".", glob(r"msvcm90.dll")),
	(".", glob(r"msvcp90.dll")),
	(".", glob(r"msvcr90.dll")),
	(".", glob(r"application-icon.ico"))
]

# setup(console=['main.py'])



# Notes on icons as resources:
#  - The settings I have that seem to work well are a combination of 64x64, 48x48, 32x32, and 16x16. Using 256 colors
#       seems to be adequate.
#  - The sizes in the icon set need to be sorted from largest size to smallest.

setup(
    data_files=data_files,
    windows = [
        {
            "script": "main.py",
            "icon_resources": [(0, "application-icon.ico")]
        }
    ],
)