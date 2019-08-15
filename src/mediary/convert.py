"""
Convert media to the optimal format for the library.
"""

import json
import collections
import logging
import argparse
import subprocess

from . import command

logger = logging.getLogger(__name__)

parser = command.subparsers.add_parser('convert', help=__doc__)
parser.add_argument(
    'input_file', type=argparse.FileType('r'),
    help='The media file to convert')
parser.add_argument(
    'output_file', type=argparse.FileType('w'),
    help='The file to write the converted media to')


def convert(
        input_file, output_file):
    """
    Convert media to the optimal format for the library.
    """
    input_args = []
    output_args = [
        # Include all streams by default
        '-map', '0', '-copy_unknown',
        # Copy streams by default, IOW don't transcode unless we need to
        '-codec', 'copy',
        # Default to high quality, only when transcoding
        '-preset', 'slow', '-crf', '20', '-profile:v', 'high',
        # The MP4 container is the most compatible
        '-f', 'mp4', '-movflags', 'faststart']
    required_kwargs = collections.OrderedDict([
        # Most compatible stream type codecs
        ('-codec:v', 'h264'), ('-codec:a', 'aac'), ('-codec:s', 'webvtt'),
        # Must include a stereo audio stream
        ('-ac', '2'),
        # Most compatible pixel format
        ('-pix_fmt', 'yuv420p')])

    # Process each stream in the input
    probe_out = subprocess.check_output([
        'ffprobe', '-show_format', '-show_streams', '-of', 'json',
        input_file.name])
    input_probed = json.loads(
        probe_out, object_pairs_hook=collections.OrderedDict)
    stream_types = dict()
    channels_streams = dict()
    stream_resources = {}
    for stream in input_probed['streams']:
        codec_type = stream['codec_type']
        stream_type = codec_type[0]
        codec_opt = '-codec:' + stream_type
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
                codec_opt in required_kwargs and
                stream['codec_name'] != required_kwargs[codec_opt]):
            output_args.extend((stream_codec_opt, required_kwargs[codec_opt]))

            if (
                    'pix_fmt' in required_kwargs and 'pix_fmt' in stream and
                    required_kwargs['pix_fmt'] != stream['pix_fmt']):
                output_args.extend(('pix_fmt:{0}'.format(
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
        input_args + ['-i', input_file.name] +
        output_args + [output_file.name, '-y'])
    cmd_line = ' '.join(args)
    if not stream_resources:
        logger.info('No processing required')
        return args

    logger.info('Processing requires resources: %s', stream_resources)
    logger.info('Running: %s', cmd_line)
    try:
        subprocess.check_call(args)
    except subprocess.CalledProcessError:
        logger.exception('Failed: %s', ' '.join(args))
    else:
        return args

parser.set_defaults(func=convert)


def main(args=None):
    """
    Convert media to the optimal format for the library.
    """
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args(args)
    convert(**{
        key: value for key, value in vars(args).items()
        if key not in {'level', 'func'}})


if __name__ == '__main__':
    main()
