"""
Media library processing and management utilities
"""

import argparse

# create the top-level parser
parser = argparse.ArgumentParser(__doc__)
subparsers = parser.add_subparsers(help='sub-command help')


def main(args=None):
    """
    Convert media to the optimal format for the library.
    """
    args = parser.parse_args(args)


if __name__ == '__main__':
    main()
