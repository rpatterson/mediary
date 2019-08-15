"""
Tests for mediary conversion tools.
"""

import os
import tempfile
import subprocess
import unittest

from .. import convert


class TestMediaryConvert(unittest.TestCase):
    """
    Test the mediary convert command.
    """

    INPUT_ARGS = [
        'ffmpeg',
        '-f', 'lavfi', '-i', 'testsrc=duration=2:size=4k:rate=60',
        '-f', 'lavfi', '-i', 'sine=frequency=220:beep_factor=4:duration=2']

    INPUT_NOOP_ARGS = ['-ac', '2']
    INPUT_NOOP = os.path.join(os.path.dirname(__file__), 'in.mp4')

    INPUT_HEVC_ARGS = ['-codec:v', 'hevc', '-ac', '8']
    INPUT_HEVC = os.path.join(os.path.dirname(INPUT_NOOP), 'in.mkv')

    @classmethod
    def setUpClass(class_):
        """
        Conditionally generate a test input video.
        """
        for input_type in ['NOOP', 'HEVC']:
            input_file = getattr(class_, 'INPUT_' + input_type)
            input_args = getattr(class_, 'INPUT_' + input_type + '_ARGS')
            if not os.path.exists(input_file):
                subprocess.check_call(
                    class_.INPUT_ARGS + input_args + [input_file])

    def test_convert_copy(self):
        """
        Videos that meet the requirements aren't processed.
        """
        with (
                open(self.INPUT_NOOP)) as input_file, (
                tempfile.NamedTemporaryFile(mode='w')) as output_file:
            args = convert.convert(input_file, output_file)
            self.assertEqual(
                os.stat(output_file.name).st_size, 0,
                'Output for video with no conversion written to')

        self.assertIn(
            '-codec copy', ' '.join(args),
            'Unprocessed video missing the copy option')
        self.assertNotIn(
            '-codec:v', ' '.join(args),
            'Unprocessed video includes codec option')

    def test_convert_hevc(self):
        """
        Videos that require conversion are transcoded.
        """
        with (
                open(self.INPUT_HEVC)) as input_file, (
                tempfile.NamedTemporaryFile(mode='w')) as output_file:
            args = convert.convert(input_file, output_file)
            self.assertTrue(
                os.stat(output_file.name).st_size,
                'Output for transacted video not written to')
            output_probed = convert.probe(output_file)

        self.assertIn(
            '-codec:0 h264', ' '.join(args),
            'Transcoded video missing codec option')
        self.assertIn(
            '-ac:2 2', ' '.join(args),
            'Video without stereo stream missing channels option')

        self.assertEqual(
            len(output_probed['streams']), 3,
            'Wrong number of transcoded streams')
        self.assertEqual(
            output_probed['streams'][0]['codec_name'], 'h264',
            'Wrong transcoded video stream codec')
        self.assertEqual(
            output_probed['streams'][1]['codec_name'], 'aac',
            'Wrong transcoded audio stream codec')
        self.assertEqual(
            output_probed['streams'][2]['codec_name'], 'aac',
            'Wrong transcoded audio stream codec')
        self.assertEqual(
            output_probed['streams'][2]['channels'], 2,
            'Wrong number of added audio stereo stream channels')


if __name__ == '__main__':
    unittest.main()
