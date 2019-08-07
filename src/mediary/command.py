"""
Commmand-line handling common to all sub-commands.
"""

import logging
import argparse

import servicelogging

import mediary

# create the top-level parser
parser = argparse.ArgumentParser(description=mediary.__doc__)
parser.add_argument(
    '--level', default=logging.INFO,
    help='The level of messages to log at or above')
subparsers = parser.add_subparsers()


def main(args=None):
    """
    Convert media to the optimal format for the library.
    """
    args = parser.parse_args(args)
    servicelogging.basicConfig(level=args.level)
    args.func(**{
        key: value for key, value in vars(args).items()
        if key not in {'level', 'func'}})


if __name__ == '__main__':
    main()
