#!/usr/bin/env python3

"""A tool to help you remember to use alternative tools.

This tool exists as a little script to help you try to use alternative command line tools.
terminalist.py creates symlinks for command line tools that have alternatives that you choose, and,
instead of running the old tool, reminds you to run the new tool, and gives you some tips for
translating command line arguments.

For example, the tool `fd` (https://github.com/sharkdp/fd) is a modern take on the venerable `find`.
In order to learn how to use `fd`, it is beneficial to start using it daily. But, muscle memory from
years of using `find` makes it difficult to remember to use something new. That's where
terminalist.py comes in. It works by making itself a symlink to `find`, so that if you type `find`,
it runs *this script* instead. The tool then reports how to use `fd` instead, offering translations
for (a subset of) the `find` command line arguments. In this way, this tool acts as sort of an
interstitial between the "old" tool, the user, and the alternative tool.

Installation:
1. Download `terminalist.py` and put it in your PATH. Make sure it's executable (chmod +x ...).
   Usually, this is done by putting it in $HOME/bin/, and ensuring $HOME/bin/ is first in your
   $PATH.
2. Run `terminalist.py` and follow the instructions there for setting up tool alternates.
"""

# This script must run in vanilla python3.6+, so no external dependencies.
import argparse
import builtins
import collections
import functools
import os
import pathlib
import textwrap
import sys

from typing import Any, Callable, Dict, List, Mapping, NamedTuple, TextIO


TERMINALIST_SOURCE_URL_RAW = "https://github.com/dshahbaz/terminalist/terminalist.py"
CURL_UPDATE_COMMAND = "curl -o {output} {url}"
USAGE = """Terminalist Habit Maker

This tool creates symlinks in your $PATH to prevent you from using an old tool and encourage you to
learn to use a new tool. For example, if you would like to use `fd`[1] instead of `find`, you can
create an interceptor that reminds you how to run `fd` instead of `find`:

    %(prog)s --install find

This will make executing `find` run %(prog)s instead, and it will remind you how to translate `find`
arguments into their `fd` equivalents.

[1]: https://github.com/sharkdp/fd

Installation:
    Copy %(prog)s to a *writable* directory in your $PATH. Ideally this should be in $HOME/bin/
    (which is hopefully in your $PATH already). %(prog)s will create symlinks (interceptors) in this
    directory so that these files are executed instead of the tool you're trying to unlearn. For
    more, see https://github.com/dshahbaz/terminalist/blob/main/README.md

List existing installed interceptions:
    %(prog)s --list-installed

List available interceptions:
    %(prog)s --list-available

Add a new interception:
    %(prog)s --install find

Remove an existing interception:
    %(prog)s --remove find

Brought to you with 🏄 from https://www.terminalist.tips/
"""


# Simple mapping between old arguments (from original command) and new arguments (from alternative
# command).
class SimpleMapping(NamedTuple):
    """Class describing the translation of a flag from the original tool to the new tool."""

    # The original tool's flag to be translated.
    orig_flag: str
    # The new tool's alternative flag that provides similar or identical functionality to the
    # original flag.
    new_flag: str
    # Additional context about the flag translation, such as added details about the new behavior.
    comment: str
    # If the original tool's orig_flag consumed some number of arguments after the flag, this count
    # represents how many arguments to consume (skip). This is just a slight optimization so that
    # flag values are not misinterpreted as subsequent flags.
    consume_next: int


class AlternativeSpec(NamedTuple):
    """Class describing an alternative for an original tool (.original) to a new tool (.alternate).

    The attribute flag_mappings describes a list of mappings from original arguments to alternate
    arguments (for use in the alternate tool).
    """

    original: str
    alternate: str
    flag_mappings: List[SimpleMapping]
    further_reading_url: str


# Shorthands for the above, which bind consume_next to some number, so that the mapping can consume
# (skip) the next N arguments.
S0 = functools.partial(SimpleMapping, consume_next=0)
S1 = functools.partial(SimpleMapping, consume_next=1)
S2 = functools.partial(SimpleMapping, consume_next=2)
S3 = functools.partial(SimpleMapping, consume_next=3)


KNOWN_TOOL_ALTERNATIVES: Dict[str, AlternativeSpec] = {}


# Remorselessly stolen from:
# https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def _color_print(
    to_print: Any,
    *,
    color: str,
    end: str = "\n",
    file: TextIO = sys.stdout,
    _environ: Mapping[str, str] = os.environ,
) -> None:
    """A function to print in specific terminal colors.

    The colored output is always terminated with Colors.ENDC.

    If the NO_COLOR environment variable is present, colors are stripped.

    Args:
        to_print: The string to print.
        color: The color code (from Colors, above) to use.
        end: The end character (similar to `print`).
        file: The output file.
        _environ: Where to look for NO_COLOR environment variable. Supplied here for tests to use.
    """
    # Respect NO_COLOR if it's there. https://no-color.org/
    if "NO_COLOR" in _environ:
        print(to_print, file=file, end=end)
        return

    try:
        print(color, file=file, end="")
        print(to_print, file=file, end=end)
    finally:
        print(Colors.ENDC, file=file, end="")


print_blue: Callable = functools.partial(_color_print, color=Colors.OKBLUE)
print_cyan: Callable = functools.partial(_color_print, color=Colors.OKCYAN)
print_green: Callable = functools.partial(_color_print, color=Colors.OKGREEN)


def register_alternative(
    *, original: str, alternate: str, further_reading_url: str, flag_mappings: List[SimpleMapping]
) -> None:
    """Create and register an AlternativeSpec into KNOWN_TOOL_ALTERNATIVES.

    Args:
    """
    alternative = AlternativeSpec(original, alternate, flag_mappings, further_reading_url)
    KNOWN_TOOL_ALTERNATIVES[alternative.original] = alternative


register_alternative(
    # Mapping `find` to `fd`:
    original="find",
    alternate="fd",
    further_reading_url="https://TODO",
    flag_mappings=[
        S1(
            "-name",
            "<name>",
            textwrap.dedent(
                """
                The name argument does not have a flag, e.g., `fd my_needle.txt`.
                """
            ),
        ),
        S1(
            "-depth",
            "--exact-depth",
            "",  # No comment.
        ),
        S1(
            "-path",
            "-p",
            textwrap.dedent(
                """
                Causes a match against the full path, rather than file name.
                """
            ),
        ),
        S0(
            "-mount",
            "--mount",
            "",  # No comment.
        ),
        S0(
            "-empty",
            "-t empty",
            "",  # No comment.
        ),
        S0(
            "-x",
            "--xdev",
            "",  # No comment.
        ),
        S1(
            "-maxdepth",
            "-d",
            "",  # No comment.
        ),
        S1(
            "-print0",
            "-0",
            "",  # No comment.
        ),
        S1(
            "-mindepth",
            "--mindepth",
            "",  # No comment.
        ),
        S0(
            "-L",
            "-L",
            "",  # No comment.
        ),
        S0(
            "-ls",
            "-l",
            textwrap.dedent(
                """
                This is the closest approximation in spirit. Technically, `-ls` is
                not identical to `-l` (see alternative below)."""
            ),
        ),
        S0(
            "-ls",
            "-x ls -dgils",
            textwrap.dedent(
                """
                (Execute `ls -dgils` for each result). This is the most precise mapping of find's
                `-ls` for fd, giving output that is identical to `-ls`. See alternative mapping
                above for an argument that is closer in spirit."""
            ),
        ),
        S1(
            "-exec",
            "-x",
            textwrap.dedent(
                """
            Where {} expands to path; {/} basename; {//} parent directory; {.} path
            without file extension; {/.} basename without file extension."""
            ),
        ),
        S1(
            "-type",
            "-t",
            textwrap.dedent(
                """
            f, file
            d, directory
            l, symlink
            x, executable
            e, empty
            s, socket
            p, pipe
            """
            ),
        ),
    ],
)


def print_curl_update_command(this_file: pathlib.Path):
    print("To update terminalist.py, run:")
    print(CURL_UPDATE_COMMAND.format(output=this_file, url=TERMINALIST_SOURCE_URL_RAW))


def print_header(alternative: AlternativeSpec):
    print("Terminalist Habit Maker")
    print("Instead of:")
    print_blue(f"{alternative.original}")
    print("use:")
    print_cyan(f"\t{alternative.alternate}")
    print()
    print("Suggested argument replacements (may not be exhaustive):")


def print_footer(this_file: pathlib.Path):
    print()
    print(
        textwrap.dedent(
            f"""
        You're seeing this because `terminalist.py` is configured to show you this alternate
        tool. To disable this, run `terminalist.py` by itself, located at
        {this_file}.
        Brought to you with 🏄 from https://www.terminalist.tips/
        """
        )
    )


def print_command_alternatives_details(this_file: pathlib.Path, command: str, args: List[str]):
    alternative = KNOWN_TOOL_ALTERNATIVES[command]

    print_header(alternative)

    # Create a mapping between flags (old tool) and (possibly more than one) flag descriptors (new
    # tool). Since this mapping can be 1-to-many, this mapping uses a list for its values. In other
    # words, each original flag can map to multiple different alternate flags, depending on the
    # context (explained via comment).
    flag_mapping = collections.defaultdict(list)
    for mapping in alternative.flag_mappings:
        flag_mapping[mapping.orig_flag].append(mapping)

    # Use a separate arg iterator, so that we can consume (skip) flag values for flags that take
    # values (set via the consume_next attribute).
    args_iter = iter(args)
    for orig_arg in args_iter:
        if orig_arg in flag_mapping:
            print_blue(orig_arg)
        else:
            continue

        # Get a list (if there are multiple) of the alternate flags for the given orig_arg.
        for alternate_flag in flag_mapping.get(orig_arg, []):
            print_cyan(f"\t{alternate_flag.new_flag}")
            print_cyan(textwrap.indent(alternate_flag.comment.lstrip(), "\t\t"))

    print_footer(this_file)


def manage(this_file: pathlib.Path):
    parser = argparse.ArgumentParser(usage=USAGE)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-l",
        "--list-installed",
        help="List the tools that are being intercepted by terminalist.",
        action="store_true",
    )
    group.add_argument(
        "-L",
        "--list-available",
        help="List the tools that terminalist knows how to intercept.",
        action="store_true",
    )
    group.add_argument(
        "-i",
        "--install",
        choices=KNOWN_TOOL_ALTERNATIVES,
        help="Install terminalist for intercepting the given tool.",
    )
    group.add_argument(
        "-r",
        "--remove",
        choices=KNOWN_TOOL_ALTERNATIVES,
    )
    group.add_argument(
        "--self-update",
        action="store_true",
    )

    args = parser.parse_args()

    if args.list_installed:
        print("Installed terminalist.py interceptions:")
        for child in this_file.parent.iterdir():
            if child.is_symlink() and child.resolve() == this_file:
                print(f"\t{child.name}")
    if args.list_available:
        print("Available interceptions:")
        for tool, spec in KNOWN_TOOL_ALTERNATIVES.items():
            print(f"\t{tool} (alternative: {spec.alternate})")
    elif args.remove:
        # Delete the interceptor iff it is actually a symlink to this_file.
        possible_interceptor = this_file.parent / args.remove
        if possible_interceptor.resolve() == this_file:
            possible_interceptor.unlink()
            print(f"Removed interception of {args.remove}")
        else:
            print(f"{args.remove} was not an existing interception; nothing done.")
    elif args.install:
        # Add an interceptor for the given argument. The argument is guaranteed to be one of the
        # known tools from KNOWN_TOOL_ALTERNATIVES.
        new_interceptor = this_file.parent / args.install
        if new_interceptor.exists():
            print(f"{new_interceptor} already exists! Not replacing.")
            return

        if not os.access(new_interceptor.parent, os.W_OK):
            print(f"{new_interceptor.parent} is not writable! This is a requirement. Exiting.")
            sys.exit(1)
            return

        new_interceptor.symlink_to(this_file)
        print(f"Added interception for {args.install}; try running `{args.install}` now.")
    elif args.self_update:
        print_curl_update_command(this_file)


def main():
    # If this tool is exec'ed via a symlink, script_exec_path will be the path to that symlink.
    # Otherwise, script_exec_path will be the path to `terminalist.py`.
    script_exec_path: pathlib.Path = pathlib.Path(sys.argv[0])

    # Dereference symlinks, if any. This will *always* result in a Path object referring to *this
    # file* (terminalist.py).
    this_file: pathlib.Path = script_exec_path.resolve()

    # Determine the command name. This will be the basename of script_exec_path, either referring to
    # the tool being intercepted or *this file's basename* ("terminalist.py").
    command: str = script_exec_path.name
    if command == "terminalist.py":
        # Tool was run directly, not via a symlink. Run the management subroutine.
        return manage(this_file)

    if command not in KNOWN_TOOL_ALTERNATIVES:
        # This is a bizarre circumstance, meaning that a symlink was created erroneously. The
        # symlink is NOT one of the handled alternatives. This should never happen, but it's easy
        # enough to handle the case here.
        print(
            textwrap.dedent(
                f"""Unknown command: {command}.  Can't find any alternatives for {command}.
                Expecting to find results? Maybe this script needs updating."""
            )
        )
        print_curl_update_command(this_file)
    else:
        args: List[str] = sys.argv[1:]
        print_command_alternatives_details(this_file, command, args)

        # Make sure we exit 1, because terminalist.py actually intercepted the call to the old tool
        # without running anything.
        sys.exit(1)


if __name__ == "__main__":
    main()
