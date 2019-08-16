"""
Command-line option and argument handling.
"""

import os
import argparse


class FileNameType(argparse.FileType):
    """
    Ensure the file can be opened and return it's name.
    """

    def __call__(self, string):
        """
        Return the name from the opened file and close it.
        """
        with super(FileNameType, self).__call__(string) as opened:
            return opened.name


class ArgsFromFileAction(argparse._AppendAction):
    """
    Collect arguments from files like argparse's `fromfile_prefix_chars`.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Read args from the file and collect into the namespace.
        """
        if not getattr(self, 'reset_dest', False):
            setattr(namespace, self.dest, [])
            self.reset_dest = True
        items = getattr(namespace, self.dest)
        for value in values:
            arg_strings = parser._read_args_from_files([
                parser.fromfile_prefix_chars + value])
        items.extend(arg_strings)
        setattr(namespace, self.dest, items)


def parse_arg_set(arg_set):
    """
    Load an argument set from the predefined package sets or as a file.
    """
    if os.path.exists(arg_set):
        return arg_set
    else:
        return os.path.join(os.path.dirname(__file__), arg_set)


def generate_parser(parser=None, args=None, **kwargs):
    """
    Generate an argument parser from arbitrary command-line arguments.
    """
    if parser is None:
        parser = argparse.ArgumentParser(**kwargs)

    args, unknown_argv = parser.parse_known_args(args)
    args = vars(args)
    arg_idx = 1
    argv = unknown_argv[:]
    while argv:
        arg = argv[0]
        next_argv = argv[1:]
        arg_kwargs = {}

        # Non-option argument
        if not arg.startswith('-'):
            parser.add_argument('arg_{0}'.format(arg_idx))
            arg_idx += 1

            args, argv = parser.parse_known_args(unknown_argv)
            continue

        # Option argument
        # Determine how many arguments the option takes
        nargs = 0
        while next_argv:
            next_arg = next_argv[0]
            if next_arg.startswith('-'):
                break
            next_argv = next_argv[1:]
            nargs += 1
        if not nargs:
            arg_kwargs['action'] = 'store_true'
        elif nargs > 1:
            arg_kwargs['nargs'] = nargs
        parser.add_argument(arg, **arg_kwargs)
        args, argv = parser.parse_known_args(unknown_argv)

    return parser, args
