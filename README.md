# What The Dot

A tool for identifying dotfiles in a home directory.

## Usage

Run `wtd.py` to scan your home directory.  Pass `-c` to force colourful output if your terminal supports it.  You can set an alternative start directory with `-r <new root>`.  Only files that exist will be shown, use `-a` to skip existence checks.

The default output format is a tree of files, though you can list by program with `-f programs`.

## Known files

The list of identified files is stored in `known.json`.  This is a single JSON object structured to match an actual home directory.  Keys are file or directory names, where directory contents are provided as a nested dictionary.

The format for an individual file may look like the following:

```
filename: {"program": program, "type": type, "files": {directory contents}]
```

All fields are optional, though directories must specify a nested `files` object (it can be empty).

For files used by multiple programs, specify a `programs` attribute with a list of names instead.

### File types

| Type      | Description                       | Examples                            |
| --------- | --------------------------------- | ----------------------------------- |
| `cache`   | temporary, cache or lock files    | `.gksu.lock`, `.thumbnails`         |
| `config`  | user-configurable settings file   | `.bashrc`, `.vimrc`                 |
| `history` | shell or interpreter history      | `.bash_history`, `.mysql_history`   |
| `install` | program files or binaries         | `.gem`, `.steam`                    |
| `key`     | auth files, private keys/keyrings | `.gnupg/pubring.kbx`, `.ssh/id_rsa` |
| `log`     | debug or installation log files   | `.irssi/away.log`, `.pip/pip.log`   |
| `session` | auto-generated cookies/keys       | `.pulse-cookie`, `.Xauthority`      |

### Conditions for inclusion

Entries in `known.json` should represent *default* locations for files created or read by other programs.  The program does not necessarily have to use them by default (for example, a log file may be created at the given location if logging is enabled by the user), though custom locations should not be included (for example, if a command-line switch to set the file path is used).  This includes conventional locations that a program does not know about by default.
