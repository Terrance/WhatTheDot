#!/usr/bin/env python

import os
import sys

py3 = sys.version_info.major == 3
vstr = str if py3 else basestring

treesort = lambda s: tuple(x.lower().lstrip(".") for x in s)

usecolour = False
def colour(code, text):
    return "\033[{0}m{1}\033[0m".format(30 + code, text) if usecolour else text

class File(object):
    def __init__(self, name, isdir, progs=None, type=None, secure=None, isold=False):
        self.name = name
        self.isdir = isdir
        self.progs = progs
        self.type = type
        self.secure = secure
        self.isold = isold
    def __str__(self):
        label = colour(1 if self.isold else (3 if self.isdir else 4), self.name)
        if self.isold:
            label = "{0} (old?)".format(label)
        if self.progs:
            label = "{0}: {1}".format(label, colour(6, ", ".join(self.progs)))
            if self.type:
                label = "{0} {1}".format(label, self.type)
        if self.secure:
            label = "{0} {1}".format(label, colour(2, "[secure]"))
        elif self.secure == False:
            label = "{0} {1}".format(label, colour(1, "[insecure]"))
        return label

def walk(root, known, found, args):
    for fname in known:
        # Look for known files in current directory.
        fparts = root + (fname,)
        fpath = os.path.join(os.getcwd(), *fparts)
        finfo = known[fname]
        isdir = "files" in finfo
        if args.all or (os.path.exists(fpath) and isdir == os.path.isdir(fpath)):
            progs = finfo.get("programs", [finfo["program"]] if "program" in finfo else None)
            secure = None
            if args.secure and os.path.exists(fpath) and finfo.get("type") in ("history", "key"):
                # Group and world permissions should be zero for private history.
                secure = (os.stat(fpath).st_mode & 0o77 == 0)
            found[fparts] = File(fname, isdir, progs, finfo.get("type"), secure)
            if isdir:
                # Recurse into subdirectory.
                walk(fparts, finfo["files"], found, args)
        if args.old:
            for btmpl in ("{0}~", "{0}.bak", "{0}.old", "{0}.swp"):
                bname = btmpl.format(fname)
                bparts = root + (bname,)
                bpath = os.path.join(os.getcwd(), *bparts)
                if os.path.exists(os.path.join(os.getcwd(), *bparts)):
                    found[bparts] = File(bname, isdir, finfo.get("prog"), finfo.get("type"), True)
    return found

def printTree(found):
    for fparts in sorted(found, key=treesort):
        print("{0}{1}".format("   " * (len(fparts) - 1), found[fparts]))

def printProgs(found, programs):
    byprog = {}
    for fparts in sorted(found, key=treesort):
        progs = found[fparts].progs or []
        for prog in progs:
            if prog not in byprog:
                byprog[prog] = []
            byprog[prog].append((fparts[:-1], found[fparts]))
    for prog in sorted(byprog):
        if programs and prog not in programs:
            continue
        print(colour(6, prog))
        for fparent, file in byprog[prog]:
            print("   {0}{1}".format(os.path.join(os.path.join(*fparent), "") if fparent else "", file))

if __name__ == "__main__":

    import argparse
    import json

    known = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "known.json"), "r"))

    parser = argparse.ArgumentParser(description="Identify dotfiles in a home directory.",
                                     epilog="File types can be one of: cache, config, history, install, key, log, session.")
    parser.add_argument("-c", "--colour", action="store_true", default=None, help="colorise output")
    parser.add_argument("-C", "--no-colour", action="store_false", dest="colour", help="don't colorise output")
    parser.add_argument("-r", "--root", default=os.path.expanduser("~"), help="override start directory")
    parser.add_argument("-p", "--programs", nargs="*", metavar="PROG", help="display as program list rather than tree")
    parser.add_argument("-s", "--secure", action="store_true", help="check private files are readable only by current user")
    parser.add_argument("-a", "--all", action="store_true", help="don't check if files exist")
    parser.add_argument("-o", "--old", action="store_true", help="look for possible old or backup files")
    args = parser.parse_args()

    usecolour = args.colour
    if usecolour is None:
        # Try to auto-detect colour availability.
        usecolour = (hasattr(sys.stdout, "isatty") and sys.stdout.isatty())

    os.chdir(args.root)

    found = walk((), known, {}, args)
    if args.programs is None:
        printTree(found)
    else:
        printProgs(found, args.programs)
