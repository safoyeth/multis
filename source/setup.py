#! usr/bin/python
# -*- coding: utf-8 -*-

import sys
from cx_Freeze import setup, Executable

build_exe_options = {"icon": "shape.ico", 'includes': ['atexit']}
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name = "Multis",
      version = "1.0.7",
      author = "Safoyeth",
      description = "Simple image manipulator",
      options = {"build_exe": build_exe_options},
      executables = [Executable("converter.py", base = base, targetName = "Multis.exe",
                                shortcutName = "Multis", shortcutDir = "DesktopFolder",
                                compress = True)])