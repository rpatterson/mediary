"""
Convert media to the optimal format for the library.
"""

import json
import collections
import logging
import argparse
import subprocess

from . import arguments
from . import command

logger = logging.getLogger(__name__)

parser = command.subparsers.add_parser(
    'convert', help=__doc__, fromfile_prefix_chars='@')

parser.add_argument(
    'input_file', type=argparse.FileType('r'),
    help='The media file to convert')
parser.add_argument(
    'output_file', type=argparse.FileType('w'),
    help='The file to write the converted media to')

# Options for preserving as much of the original file as possible and doing
# as little transcoding as possible:
# - Include all streams by default
# - Copy streams by default, IOW don't transcode unless we need to
PRESERVE_ARGS = parser._read_args_from_files([
    parser.fromfile_prefix_chars + arguments.parse_arg_set(
        'ffmpeg-preserve.txt')])

# Options for producing output files that are as compatible as possible
# across various players: HTML 5, iOS, Android, etc.  Useful to avoiding
# transcoding when being streamed:
# - Most compatible codecs
# - Must include a stereo audio stream
# - Most compatible pixel format
# - The most compatible container
# - Enable streaming quickly
COMPATIBLE_ARGS = parser._read_args_from_files([
    parser.fromfile_prefix_chars + arguments.parse_arg_set(
        'ffmpeg-compatible.txt')])
# Sacrifice some compatibility for outputs that are as compressed as possible.
COMPACT_ARGS = parser._read_args_from_files([
    parser.fromfile_prefix_chars + arguments.parse_arg_set(
        'ffmpeg-compact.txt')])

# Options for a reasonable trade-off of longer encodng time for higher quality
# for resulting file size:
# - Default to high quality, only when transcoding
QUALITY_ARGS = parser._read_args_from_files([
    parser.fromfile_prefix_chars + arguments.parse_arg_set(
        'ffmpeg-quality.txt')])

parser.add_argument(
    '--output-args',
    type=arguments.parse_arg_set, action=arguments.ArgsFromFileAction,
    default=PRESERVE_ARGS + QUALITY_ARGS, nargs='+', help="""
The name one of the predefined sets of arguments for ffmpeg or a file
containing ffmpeg arguments, one per line.  Will be used as the output
defaults. May be given multiple times to combine multiple sets.
(default: %(default)s)""")
parser.add_argument(
    '--required-args',
    type=arguments.parse_arg_set, action=arguments.ArgsFromFileAction,
    default=COMPATIBLE_ARGS, nargs='+', help="""
The name one of the predefined sets of arguments for ffmpeg or a file
containing ffmpeg arguments, one per line.  Will be used as output
requirements to determine whether to transcode or remux the input. May be
given multiple times to combine multiple sets.
(default: %(default)s)""")


FFPROBE_ARGS = ['ffprobe', '-show_format', '-show_streams', '-of', 'json']


def probe(input_file):
    """
    Probe the input file with ffprobe and return the JSON deserialized.
    """
    probe_out = subprocess.check_output(FFPROBE_ARGS + [input_file.name])
    return json.loads(
        probe_out, object_pairs_hook=collections.OrderedDict)


def convert(
        input_file, output_file,
        output_args=parser.get_default('output_args'),
        required_args=parser.get_default('required_args')):
    """
    Convert media to the optimal format for the library.
    """
    # Process required ffmpeg arguments for lookup
    required_kwargs = vars(arguments.generate_parser(args=required_args)[1])

    # Process each stream in the input
    stream_types = dict()
    channels_streams = dict()
    stream_resources = {}
    input_probed = probe(input_file)
    for stream in input_probed['streams']:
        codec_type = stream['codec_type']
        stream_type = codec_type[0]
        codec_kwarg = 'codec:' + stream_type
        stream_codec_opt = '-codec:{0}'.format(stream['index'])

        # Gather streams by type for type specific processing later
        stream_types.setdefault(stream['codec_type'], []).append(stream)
        # Gather streams by number of channels for channel-specific processing
        # later, e.g. adding a stereo stream if absent
        if 'channels' in stream:
            channels_streams.setdefault(
                str(stream['channels']), []).append(stream['index'])

        # Transcode if the required codec is  different from the input
        if (
                codec_kwarg in required_kwargs and
                stream['codec_name'] != required_kwargs[codec_kwarg]):
            output_args.extend((
                stream_codec_opt, required_kwargs[codec_kwarg]))

            if (
                    'pix_fmt' in required_kwargs and 'pix_fmt' in stream and
                    required_kwargs['pix_fmt'] != stream['pix_fmt']):
                output_args.extend(('-pix_fmt:{0}'.format(
                    stream['index']), required_kwargs['pix_fmt']))

            # Note which system process this command will be bound by.
            # Any remuxing will be disk itensive regardless of whether there
            # will be trancoding.
            stream_resources.setdefault(
                'disk', set()).add(stream['index'])
            if codec_type == 'video':
                # Transcoding video is processor bound
                stream_resources.setdefault(
                    'processor', set()).add(stream['index'])

    # If there isn't a stereo audio stream, copy the first stream with the
    # most channels and downmix it to stereo
    required_channels = required_kwargs.get('ac')
    if (
            required_channels is not None and
            required_channels not in channels_streams):
        # Default to copying the first audio stream
        stereo_source_stream = stream_types['audio'][0]
        # Use the first audio stream with the most channels
        for audio_stream in stream_types['audio'][1:]:
            if (
                    int(audio_stream['channels']) >
                    int(stereo_source_stream['channels'])):
                stereo_source_stream = audio_stream
        stereo_stream_idx = len(input_probed['streams'])
        output_args.extend((
            '-map', '0:1',
            '-ac:{0}'.format(stereo_stream_idx), required_channels))
        if 'codec:a' in required_kwargs:
            output_args.extend(('-codec:{0}'.format(
                stereo_stream_idx), required_kwargs['codec:a']))
        stream_resources.setdefault(
            'disk', set()).add(stereo_stream_idx)

    args = (
        ['ffmpeg', '-hide_banner'] +
        ['-i', input_file.name] +
        output_args + [output_file.name, '-y'])
    cmd_line = ' '.join(args)
    if not stream_resources:
        logger.info('No processing required')
        return args

    logger.info('Processing requires resources: %s', stream_resources)
    logger.info('Running: %s', cmd_line)
    subprocess.check_call(args)
    return args

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
