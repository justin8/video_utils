import unittest

from video_utils import misc

class test_get_codec(unittest.TestCase):
    def test_get_codec_x265(self):
        self.assertEqual(misc.getCodecFromFormat("HEVC"), "libx265")
        self.assertEqual(misc.getCodecFromFormat("HEVC", codecType="pretty"), "x265")


    def test_get_codec_x264(self):
        self.assertEqual(misc.getCodecFromFormat("AVC"), "h264")
        self.assertEqual(misc.getCodecFromFormat("AVC", codecType="pretty"), "x264")


    def test_get_codec_other(self):
        self.assertEqual(misc.getCodecFromFormat("foo"), "Other")
        self.assertEqual(misc.getCodecFromFormat("foo", codecType="pretty"), "Other")
