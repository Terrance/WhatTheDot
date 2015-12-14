#!/usr/bin/env python

import json
import os
import sys

py3 = sys.version_info.major == 3
vstr = str if py3 else basestring

usecolour = False
def colour(code, text):
    return "\033[{0}m{1}\033[0m".format(30 + code, text) if usecolour else text

class File(object):
    def __init__(self, name, isdir, prog=None, tags=(), isold=False):
        self.name = name
        self.isdir = isdir
        self.prog = prog
        self.tags = tags
        self.isold = isold
    def __str__(self):
        label = colour(1 if self.isold else (3 if self.isdir else 4), self.name)
        if self.isold:
            label = "{0} (old?)".format(label)
        if self.prog:
            label = "{0}: {1}".format(label, colour(6, self.prog))
            if self.tags:
                label = "{0} {1}".format(label, ", ".join(self.tags))
        return label

def walk(root, files, found, showall, showold):
    for fname in files:
        # Look for known files in current directory.
        fparts = root + (fname,)
        fpath = os.path.join(os.getcwd(), *fparts)
        prog = None
        tags = files[fname][:-1] if isinstance(files[fname][-1], dict) else files[fname]
        if tags:
            prog, tags = tags[0], tags[1:]
        isdir = isinstance(files[fname][-1], dict)
        if showall or (os.path.exists(fpath) and isdir == os.path.isdir(fpath)):
            found[fparts] = File(fname, isdir, prog, tags)
            if isdir:
                # Recurse into subdirectory.
                walk(fparts, files[fname][-1], found, showall, showold)
        if showold:
            for btmpl in ("{0}~", "{0}.bak", "{0}.old", "{0}.swp"):
                bname = btmpl.format(fname)
                bparts = root + (bname,)
                bpath = os.path.join(os.getcwd(), *bparts)
                if os.path.exists(os.path.join(os.getcwd(), *bparts)):
                    found[bparts] = File(bname, isdir, prog, tags, True)
    return found

def printTree(found):
    for fparts in sorted(found, key=lambda s: tuple(x.lower() for x in s)):
        print("{0}{1}".format("   " * (len(fparts) - 1), found[fparts]))

def printProgs(found):
    byprog = {}
    for fparts in sorted(found, key=lambda s: tuple(x.lower() for x in s)):
        prog = found[fparts].prog
        if prog:
            if prog not in byprog:
                byprog[prog] = []
            byprog[prog].append((fparts[:-1], found[fparts]))
    for prog in sorted(byprog):
        print(colour(6, prog))
        for fparent, file in byprog[prog]:
            print("   {0}{1}".format(os.path.join(os.path.join(*fparent), "") if fparent else "", file))

if __name__ == "__main__":

    import argparse

    known = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "known.json"), "r"))

    parser = argparse.ArgumentParser(description="Identify dotfiles in a home directory.",
                                     epilog="File types can be one of: cache, config, history, install, key, log, session.")
    parser.add_argument("-c", "--colour", action="store_true", help="colorise output")
    parser.add_argument("-r", "--root", default=os.path.expanduser("~"), help="override start directory")
    parser.add_argument("-p", "--programs", action="store_true", help="organise by program, with info")
    parser.add_argument("-a", "--all", action="store_true", help="just show all known files")
    parser.add_argument("-o", "--old", action="store_true", help="look for possible old or backup files")
    args = parser.parse_args()

    usecolour = args.colour
    os.chdir(args.root)

    found = walk((), known, {}, args.all, args.old)
    if args.programs:
        printProgs(found)
    else:
        printTree(found)
