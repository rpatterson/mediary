"""
Convert media to the optimal format for the library.
"""

import logging
import argparse

import ffmpeg

from . import command

logger = logging.getLogger(__name__)

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
    stream = ffmpeg.input(input_file.name)
    stream = stream.output(output_file.name).overwrite_output()
    return stream.run()

parser.set_defaults(func=convert)


def main(args=None):
    """
    Convert media to the optimal format for the library.
    """
    logging.basicConfig()
    args = parser.parse_args(args)
    logger.info(
        convert(**vars(args)))


if __name__ == '__main__':
    main()
