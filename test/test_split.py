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
        splitter.split(self.__path(FILE), max=1)
        self.__verify_files()

    def test_point_split(self):
        splitter = PointSplitter(self.writer)
        splitter.logger.setLevel(logging.DEBUG)
        splitter.split(self.__path(FILE), max=30)
        self.__verify_files()

    def __verify_files(self):
        length = 2
        files = self.__files()
        self.assertEqual(length, len(files))
        for i in range(0, length):
            self.assertTrue(files[i].endswith(f"_{i+1}.gpx"))


if __name__ == '__main__':
    unittest.main()