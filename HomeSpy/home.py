#!/usr/bin/env python

import json
import os
import sys

py3 = sys.version_info.major == 3
vstr = str if py3 else basestring

usecolour = False
def colour(code, text):
    return "\033[{0}m{1}\033[0m".format(code, text) if usecolour else text

def walk(root, files, showall):
    for fname in sorted(files, key=lambda s: s.lower()):
        # Look for known files in current directory.
        fparts = root + (fname,)
        fpath = os.path.join(os.getcwd(), *fparts)
        if showall or os.path.exists(fpath):
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
                walk(fparts, files[fname][-1], showall)

def progs(root, files, found, showall):
    for fname in sorted(files, key=lambda s: s.lower()):
        # Look for known files in current directory.
        fparts = root + (fname,)
        fpath = os.path.join(os.getcwd(), *fparts)
        if showall or os.path.exists(fpath):
            isdir = isinstance(files[fname][-1], dict)
            if not isdir == os.path.isdir(fpath):
                # Expecting one of file/dir, got the other...
                continue
            parts = files[fname][:-1] if isinstance(files[fname][-1], dict) else files[fname]
            if len(parts):
                finfo = (os.path.join(*fparts), isdir, parts[1:])
                if parts[0] in found:
                    found[parts[0]].append(finfo)
                else:
                    found[parts[0]] = [finfo]
            if isdir:
                # Recurse into subdirectory.
                progs(fparts, files[fname][-1], found, showall)
    return found

if __name__ == "__main__":

    import argparse

    known = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "known.json"), "r"))

    parser = argparse.ArgumentParser(description="Identify dotfiles in a home directory.",
                                     epilog="File types can be one of: cache, config, history, install, key, log, session.")
    parser.add_argument("-c", "--colour", action="store_true", help="colorise output")
    parser.add_argument("-r", "--root", default=os.path.expanduser("~"), help="override start directory")
    parser.add_argument("-p", "--programs", action="store_true", help="organise by program, with info")
    parser.add_argument("-a", "--all", action="store_true", help="just show all known files")
    args = parser.parse_args()

    usecolour = args.colour
    os.chdir(args.root)
    if args.programs:
        pfiles = progs((), known, {}, args.all)
        for prog in sorted(pfiles):
            print(colour(36, prog))
            for fname, isdir, parts in pfiles[prog]:
                label = "   {0}".format(colour(33 if isdir else 34, fname))
                if len(parts):
                    # Show any tags.
                    label += ": {0}".format(", ".join(parts))
                print(label)
    else:
        walk((), known, args.all)
