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
parser.add_argument(
    'output_codec',
    help='The codec in which to encode the converted media')


def convert(
        input_file, output_file, output_codec):
    """
    Convert media to the optimal format for the library.
    """
    # TODO acodec
    # TODO subtitles
    input_probed = ffmpeg.probe(input_file.name)
    for stream in input_probed['streams']:
        if stream['codec_type'] == 'video':
            vdecoder = stream['codec_name']
            break
    else:
        raise ValueError('Could not find a video stream in the input')
    vencoder = output_codec

    codecs_kwargs = ffmpeg.detect_codecs(vdecoder, vencoder)
    for codec_kwargs in codecs_kwargs:
        for kwargs_key in ('input', 'output'):
            if 'codec' in codec_kwargs[kwargs_key]:
                codec_kwargs[kwargs_key][
                    'vcodec'] = codec_kwargs[kwargs_key].pop('codec')
        stream = ffmpeg.input(input_file.name, **codec_kwargs['input'])
        stream = stream.output(
            output_file.name, **codec_kwargs['output']).overwrite_output()

        logger.info('ffmpeg arguments: %s', ' '.join(stream.get_args()))
        try:
            return stream.run()
        except Exception:
            logger.exception('ffmpeg failed: %s', ' '.join(stream.get_args()))

parser.set_defaults(func=convert)


def main(args=None):
    """
    Convert media to the optimal format for the library.
    """
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args(args)
    return convert(**{
        key: value for key, value in vars(args).items()
        if key not in {'level', 'func'}})


if __name__ == '__main__':
    main()
