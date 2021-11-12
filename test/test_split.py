import logging
import unittest
import os
import glob

from gpx_split.split import PointSplitter, LengthSplitter
from gpx_split.writer import Writer

OUT = os.getcwd() + '/test/out/'
FILE = 'test.gpx'

class TestSplitter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        #create the output if not present
        if not os.path.exists(OUT):
            os.makedirs(OUT)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(OUT):
            os.rmdir(OUT)

    def setUp(self):
        self.writer = Writer(OUT)

    def tearDown(self):
        for f in self.__files():
            os.remove(f)

    def __path(self, name):
        f = 'test/resources/' + name
        return os.path.realpath(f)

    def __files(self):
        return glob.glob(OUT + '*')

    def test_length_split(self):
        splitter = LengthSplitter(self.writer)
        splitter.logger.setLevel(logging.DEBUG)
        splitter.split(self.__path(FILE), 1)
        self.assertEqual(2, len(self.__files()))

    def test_point_split(self):
        splitter = PointSplitter(self.writer)
        splitter.logger.setLevel(logging.DEBUG)
        splitter.split(self.__path(FILE), 30)
        self.assertEqual(2, len(self.__files()))


if __name__ == '__main__':
    unittest.main()