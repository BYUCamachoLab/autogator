#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the MIT License
# (see autogator/__init__.py for details)

"""
Tool that converts all .ui and .qrc files in the autogator.resources folder to
python files in autogator.compiled.

Usage:
$ python3 ui2py.py
"""

import sys
import os
import subprocess

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

path = "autogator"
res = os.path.join(path, "resources")
dest = os.path.join(path, "compiled")

for root, directories, filenames in os.walk(res):
    for filename in filenames:
        item = os.path.join(root, filename)
        if item.endswith(".ui"):
            name, _ = os.path.splitext(filename)
            rename = name + "_ui" + ".py"
            path2dest = os.path.join(dest, rename)
            print(*["pyside2-uic", "--from-imports", item, "-o", path2dest])
            subprocess.call(["pyside2-uic", "--from-imports", item, "-o", path2dest])
        if item.endswith(".qrc"):
            name, _ = os.path.splitext(filename)
            rename = name + "_rc" + ".py"
            path2dest = os.path.join(dest, rename)
            args = ["pyside2-rcc", item, "-o", path2dest]
            print(*args)
            subprocess.call(args)
