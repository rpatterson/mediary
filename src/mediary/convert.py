"""
Convert media to the optimal format for the library.
"""

import argparse

from . import command

parser = command.subparsers.add_parser('convert', help=__doc__)
parser.add_argument(
    'input_file', type=argparse.FileType('r'),
    help='The media file to convert')
parser.add_argument(
    'output_file', type=argparse.FileType('w'),
    help='The file to write the converted media to')


def convert(input_file, output_file):
    """
    Convert media to the optimal format for the library.
    """
    return output_file

parser.set_defaults(func=convert)


def main(args=None):
    """
    Convert media to the optimal format for the library.
    """
    args = parser.parse_args(args)
    convert(**vars(args))


if __name__ == '__main__':
    main()
