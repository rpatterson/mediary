"""
Commmand-line handling common to all sub-commands.
"""

import argparse

import mediary

# create the top-level parser
parser = argparse.ArgumentParser(description=mediary.__doc__)
subparsers = parser.add_subparsers()


def main(args=None):
    """
    Convert media to the optimal format for the library.
    """
    args = parser.parse_args(args)
    args.func(**vars(args))


if __name__ == '__main__':
    main()
