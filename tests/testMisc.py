import unittest

from video_utils import misc

class testMisc(unittest.TestCase):


    def testGetVideosInList(self):
        test_data = [
                "foo.mkv",
                "bar.avi",
                "fdsfs fsda f.flv",
                "fdsa -5234 fdsafs .sssfds .vcx.ts",
                "baz.jpg",
                "something.xml",
                ]

        expected_result = [
                "bar.avi",
                "fdsa -5234 fdsafs .sssfds .vcx.ts",
                "fdsfs fsda f.flv",
                "foo.mkv",
                ]

        self.assertEqual(misc.getVideosInFileList(test_data), expected_result)
