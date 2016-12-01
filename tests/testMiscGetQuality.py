import unittest

from video_utils import misc

class testGetTrackQuality(unittest.TestCase):
    def testGetQualityWidth1080p(self):
        testData = [ 1900, 1920, 1930 ]

        for width in testData:
            track = lambda: None
            track.width = width
            track.height = 0
            quality = misc.getTrackQuality(track)
            self.assertEqual(quality, "1080p")


    def testGetTrackQualityWidth720p(self):
        testData = [ 1200, 1280, 1290 ]

        for width in testData:
            track = lambda: None
            track.width = width
            track.height = 0
            quality = misc.getTrackQuality(track)
            self.assertEqual(quality, "720p")


    def testGetTrackQualityWidthSD(self):
        testData = [ 400, 800, 999 ]

        for width in testData:
            track = lambda: None
            track.width = width
            track.height = 0
            quality = misc.getTrackQuality(track)
            self.assertEqual(quality, "SD")


    def testGetTrackQualityWidthOther(self):
        testData = [ 1100, 2500 ]

        for width in testData:
            track = lambda: None
            track.width = width
            track.height = 0
            quality = misc.getTrackQuality(track)
            self.assertEqual(quality, "Unknown")


    def testGetTrackQualityHeight1080p(self):
        testData = [ 1000, 1080, 1100 ]

        for height in testData:
            track = lambda: None
            track.height = height
            track.width = 0
            quality = misc.getTrackQuality(track)
            self.assertEqual(quality, "1080p")


    def testGetTrackQualityHeight720p(self):
        testData = [ 650, 720, 730 ]

        for height in testData:
            track = lambda: None
            track.height = height
            track.width = 0
            quality = misc.getTrackQuality(track)
            self.assertEqual(quality, "720p")
