# terminalist.py

A command line tool to help you remember to use different command line tools.

This tool exists as a little script to help you try to use alternative command line tools.
`terminalist.py` creates symlinks for command line tools that have alternatives that you choose, and,
instead of running the old tool, reminds you to run the new tool, and gives you some tips for
translating command line arguments. It exists as a way to break habits and form new ones.

For example, the tool `fd` ([https://github.com/sharkdp/fd](https://github.com/sharkdp/fd)) is a modern take on the venerable `find`.
In order to learn how to use `fd`, it is beneficial to start using it daily. But, muscle memory from
years of using `find` makes it difficult to remember to use something new. That's where
`terminalist.py` comes in. It works by making itself a symlink to `find`, so that if you type `find`,
it runs *this script* instead. Running `find` then reports how to use `fd` instead, offering
translations for (a subset of) the `find` command line arguments that you specified. In this way,
this tool acts as sort of an interjection between the "old" tool, the user, and the alternative
tool.

## Requirements

`terminalist.py` is designed to work wherever python3.6 (and above) exists. It has no dependencies
and is a standalone file.

## Installation

1. You *must* have a `$HOME/bin/` directory, and it *must* be first in your `$PATH`. (How to do this
   varies by systems and by shells. For bash, see [askubuntu](https://askubuntu.com/questions/60218/how-to-add-a-directory-to-the-path). For zsh, see [stackoverflow](https://stackoverflow.com/questions/11530090/adding-a-new-entry-to-the-path-variable-in-zsh). For fish, see [docs](https://fishshell.com/docs/current/cmds/fish_add_path.html).)
1. Download `terminalist.py` and put it in your `$HOME/bin`. Make sure it's executable.
   ```
   $ curl -o $HOME/bin/terminalist.py https://github.com/dshahbaz/terminalist/terminalist.py
   $ chmod +x $HOME/bin/terminalist.py
   ```
1. Run `terminalist.py` and follow the instructions there for setting up tool alternates.

## Usage

### List installed interceptions

This will print the installed interceptions (ie, the symlinks that point to the `terminalist.py`
script).

```
terminalist.py --list-installed
```

### List available interceptions

```
terminalist.py --list-available
```

### Add a new interception

Add an interception. This example will create a symlink from `find -> terminalist.py` in the same
directory that `terminalist.py` resides (namely, `$HOME/bin/`). Note that it will not overwrite any
files.

```
terminalist.py --install find
```

Of course, the argument above must be one of the handled interceptions listed with
`--list-available`.

### Remove an existing interception

Remove an installed interception. This simply removes the symlink created with `--install`. Note
that this does *not* remove any files that are not `terminalist.py` managed symlinks.

```
terminalist.py --remove find
```

### Updating

From time to time, there may be additional interceptions added to the upstream version of the
script. Run this to update:

```
terminalist.py --self-update
```

