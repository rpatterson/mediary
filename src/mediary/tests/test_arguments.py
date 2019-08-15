"""
Tests for mediary command-line argument handling.
"""

import unittest

from .. import arguments


class TestMediaryArgs(unittest.TestCase):
    """
    Test the mediary command-line argument handling.
    """

    def test_generate_parser(self):
        """
        Test generating argument parsers from arbitrary arguments.
        """
        parser, args = arguments.generate_parser(args=[
            '--foo', 'qux', 'grault', '--corge', '--bar', 'garply'])
        self.assertEqual(
            vars(args), dict(foo=['qux', 'grault'], corge=True, bar='garply'),
            'Wrong parsed arguments')


if __name__ == '__main__':
    unittest.main()
