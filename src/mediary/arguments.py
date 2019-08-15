"""
Command-line option and argument handling.
"""

import argparse


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
