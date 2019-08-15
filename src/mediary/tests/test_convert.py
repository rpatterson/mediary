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
                'ffmpeg', '-f', 'lavfi',
                '-i', 'testsrc=duration=1:size=4k:rate=60',
                '-pix_fmt', 'yuv420p',
                class_.INPUT_FILE])

    def test_convert_basic(self):
        """
        Test that the tests run.
        """
        with (
                open(self.INPUT_FILE)) as input_file, (
                tempfile.NamedTemporaryFile(mode='w')) as output_file:
            convert.convert(input_file, output_file)


if __name__ == '__main__':
    unittest.main()
