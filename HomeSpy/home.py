#!/usr/bin/env python

import json
import os
import sys

py3 = sys.version_info.major == 3
vstr = str if py3 else basestring

usecolour = False
def colour(code, text):
    return "\033[{0}m{1}\033[0m".format(code, text) if usecolour else text

def walk(root, files):
    for fname in sorted(files, key=lambda s: s.lower()):
        # Look for known files in current directory.
        fparts = root + (fname,)
        fpath = os.path.join(os.getcwd(), *fparts)
        if os.path.exists(fpath):
            isdir = isinstance(files[fname][-1], dict)
            if not isdir == os.path.isdir(fpath):
                # Expecting one of file/dir, got the other...
                continue
            label = colour(33 if isdir else 34, fname)
            parts = files[fname][:-1] if isinstance(files[fname][-1], dict) else files[fname]
            if len(parts):
                # Show the program name.
                label += ": {0}".format(colour(36, parts[0]))
                if len(parts) > 1:
                    # Show any tags.
                    label += " {0}".format(", ".join(parts[1:]))
            print("{0}{1}".format("   " * len(root), label))
            if isdir:
                # Recurse into subdirectory.
                walk(fparts, files[fname][-1])

if __name__ == "__main__":

    import argparse

    known = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "known.json"), "r"))

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--colour", action="store_true", help="colorise output")
    parser.add_argument("-r", "--root", default=os.path.expanduser("~"), help="override start directory")
    args = parser.parse_args()

    usecolour = args.colour
    os.chdir(args.root)
    walk((), known)
