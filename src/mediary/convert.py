"""
Convert media to the optimal format for the library.
"""

import collections
import logging
import argparse
import subprocess

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


def convert(
        input_file, output_file):
    """
    Convert media to the optimal format for the library.
    """
    input_kwargs = dict()
    output_kwargs = {
        # Include all streams by default
        'map': '0', 'copy_unknown': True,
        # Copy streams by default, IOW don't transcode unless we need to
        'codec': 'copy',
        # The MP4 container is the most compatible
        'f': 'mp4'}
    required_kwargs = {
        # Most compatible stream type codecs
        'codec:v': 'h264', 'codec:a': 'aac', 'codec:s': 'webvtt',
        # Must include a stereo audio stream
        'ac': '2',
        # Most compatible pixel format
        'pix_fmt': 'yuv420p'}

    # Process each stream in the input
    input_probed = ffmpeg.probe(input_file.name)
    stream_types = dict()
    channels_streams = dict()
    streams_multi_kwargs = []
    stream_resources = {}
    for stream in input_probed['streams']:
        codec_type = stream['codec_type']
        stream_type = codec_type[0]
        codec_kwarg = 'codec:' + stream_type
        stream_codec_kwarg = 'codec:{0}'.format(stream['index'])
        multi_kwargs = []
        streams_multi_kwargs.append(multi_kwargs)

        # Gather streams by type for type specific processing later
        stream_types.setdefault(stream['codec_type'], []).append(stream)
        # Gather streams by number of channels for channel-specific processing
        # later, e.g. adding a stereo stream if absent
        if 'channels' in stream:
            channels_streams.setdefault(
                str(stream['channels']), []).append(stream['index'])

        # Detect what acceleration options can be used
        if (
                codec_kwarg in required_kwargs and
                stream['codec_name'] != required_kwargs[codec_kwarg]):
            codecs_kwargs = ffmpeg.detect_codecs(
                    stream['codec_name'], required_kwargs[codec_kwarg])
            for codec_kwargs in codecs_kwargs:
                for kwargs in codec_kwargs.values():
                    if 'codec' in kwargs:
                        kwargs[stream_codec_kwarg] = kwargs.pop('codec')
                if stream_codec_kwarg not in codec_kwargs['output']:
                    # Restore the encoder if it was excluded because it's not
                    # in the ffmpeg codecs' list of encoders
                    codec_kwargs['output'][
                        stream_codec_kwarg] = required_kwargs[codec_kwarg]

                if (
                        'pix_fmt' in stream and
                        required_kwargs.get('pix_fmt') != stream['pix_fmt']):
                    codec_kwargs['output']['pix_fmt:{0}'.format(
                        stream['index'])] = required_kwargs['pix_fmt']

            # Collect multiple sets of options for successive attempts
            multi_kwargs.extend(codecs_kwargs)

            # Note which system process this command will be bound by.
            # Any remuxing will be disk itensive regardless of whether there
            # will be trancoding.
            stream_resources.setdefault(
                'disk', set()).add(stream['index'])
            if codec_type == 'video':
                # Transcoding video is GPU and/or CPU bound.
                stream_resources.setdefault(
                    'processors', set()).add(stream['index'])

    # If there isn't a stereo audio stream, copy the first stream with the
    # most channels and downmix it to stereo
    required_channels = required_kwargs.get('ac')
    if (
            required_channels is not None and
            required_channels not in channels_streams):
        stereo_source_stream = stream_types['audio'][0]
        for audio_stream in stream_types['audio'][1:]:
            if (
                    int(audio_stream['channels']) >
                    int(stereo_source_stream['channels'])):
                stereo_source_stream = audio_stream
        stereo_stream_idx = len(streams_multi_kwargs)
        kwargs = dict(output=collections.OrderedDict([
            ('map', '0:1'),
            ('ac:{0}'.format(stereo_stream_idx), required_channels)]))
        if 'codec:a' in required_kwargs:
            kwargs['output']['codec:{0}'.format(
                stereo_stream_idx)] = required_kwargs['codec:a']
        streams_multi_kwargs.append([kwargs])
        stream_resources.setdefault(
            'disk', set()).add(stereo_stream_idx)

    # Normalize options to lists in order to support multiple instance of the
    # same option per-type below
    input_args = []
    output_args = []
    for kwargs, args in (
            (input_kwargs, input_args), (output_kwargs, output_args)):
        for option, value in kwargs.items():
            if isinstance(value, bool):
                args.append('-{0}'.format(option))
            else:
                args.extend(('-{0}'.format(option), value))

    if stream_resources:
        logger.info('Processing requires resources: %s', stream_resources)
    else:
        logger.info('No processing required')

    # Try each set of possible arguments for each stream in turn
    for attempt_idx in range(max(
            len(multi_kwargs) for multi_kwargs in streams_multi_kwargs)):
        attempt_input_args = input_args[:]
        attempt_output_args = output_args[:]

        for multi_kwargs in streams_multi_kwargs:
            for kwarg_group, args in (
                    ('input', attempt_input_args),
                    ('output', attempt_output_args)):
                kwargs = multi_kwargs[:attempt_idx + 1][-1].get(
                    kwarg_group, {})
                for option, value in kwargs.items():
                    if isinstance(value, bool):
                        args.append('-{0}'.format(option))
                    else:
                        args.extend(('-{0}'.format(option), value))

        args = (
            ['ffmpeg', '-hide_banner'] +
            attempt_input_args + ['-i', input_file.name] +
            attempt_output_args + [output_file.name, '-y'])
        cmd_line = ' '.join(args)
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
