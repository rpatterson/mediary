"""
Tests for mediary conversion tools.
"""

import os
import tempfile
import unittest

from .. import convert


class TestMediaryConvert(unittest.TestCase):
    """
    Test the mediary convert command.
    """

    INPUT_FILE = os.path.join(os.path.dirname(__file__), 'in.mp4')

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
