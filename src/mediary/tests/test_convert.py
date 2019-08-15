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

    INPUT_FILE = os.path.join(os.path.dirname(__file__), 'in.mp4')

    @classmethod
    def setUpClass(class_):
        """
        Conditionally generate a test input video.
        """
        if not os.path.exists(class_.INPUT_FILE):
            subprocess.check_call([
                'ffmpeg',
                '-f', 'lavfi',
                '-i', 'testsrc=duration=2:size=4k:rate=60',
                '-f', 'lavfi',
                '-i', 'sine=frequency=220:beep_factor=4:duration=2',
                '-ac', '2',
                class_.INPUT_FILE])

    def test_convert_copy(self):
        """
        Videos that meet the requirements aren't processed.
        """
        with (
                open(self.INPUT_FILE)) as input_file, (
                tempfile.NamedTemporaryFile(mode='w')) as output_file:
            args = convert.convert(input_file, output_file)
            self.assertEqual(
                os.stat(output_file.name).st_size, 0,
                'Output for video with no conversion written to')
        self.assertIn(
            '-codec copy', ' '.join(args),
            'Wrong return type for no proecessing required')


if __name__ == '__main__':
    unittest.main()
