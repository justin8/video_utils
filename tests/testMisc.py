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

    def testIsVideo(self):
        videoFilenames = ["test file 123x124 - name.avi",
                           "test file 123x124 - name.mkv",
                           "test file 123x124 - name.mp4",
                           "test file 123x124 - name.mpg",
                           "test file 123x124 - name.mpeg",
                           "test file 123x124 - name.mov",
                           "test file 123x124 - name.MOV",
                           "test file 123x124 - name.m4v",
                           "test file 123x124 - name.flv",
                           "test file 123x124 - name.FLV",
                           "test file 123x124 - name.divx",
                           "test file 123x124 - name.ts",
                           "test file 123x124 - name.wmv",
        ]

        nonVideoFilenames = ["test file 123x124 - name.foo",
                               "test file 123x124 - name.bar",
                               "test file 123x124 - name.txt",
                               "test file 123x124 - name.jpg",
        ]

        for filename in videoFilenames:
            self.assertTrue(misc.isVideo(filename))

        for filename in nonVideoFilenames:
            self.assertFalse(misc.isVideo(filename))
