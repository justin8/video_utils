#!/usr/bin/env python3
import unittest
import os
from copy import deepcopy

from video_utils import fileMap

testDataDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testData")
foo = {
        'test episode - 01x01 - another in 1080p.mkv': {'codec': 'x265',
            'format': 'HEVC',
            'quality': '1080p',
            'size': 2305},
        'test episode - 01x02 - another in 1080p.mkv': {'codec': 'x265',
            'format': 'HEVC',
            'quality': '1080p',
            'size': 2305},
        'test episode - 01x03 - another in 1080p.mkv': {'codec': 'x265',
            'format': 'HEVC',
            'quality': '1080p',
            'size': 2305},
        'test episode - 02x01 - this is 1080p.avi': {'codec': 'Other',
            'format': 'MPEG-4 Visual',
            'quality': '1080p',
            'size': 10652},
        'test episode - 02x02 - another in 1080p.mkv': {'codec': 'x265',
            'format': 'HEVC',
            'quality': '1080p',
            'size': 2305},
        'test episode - 02x03 - this is 720p.mkv': {'codec': 'x265',
            'format': 'HEVC',
            'quality': '720p',
            'size': 2303}
        }
bar = {
        'test episode - 01x01 - another in 1080p.mkv': {'codec': 'x265',
            'format': 'HEVC',
            'quality': '1080p',
            'size': 2305},
        'test episode - 01x02 - another in 1080p.mkv': {'codec': 'x265',
            'format': 'HEVC',
            'quality': '1080p',
            'size': 2305},
        'test episode - 01x03 - another in 1080p.mkv': {'codec': 'x265',
            'format': 'HEVC',
            'quality': '1080p',
            'size': 2305},
        'test episode - 02x01 - this is 1080p.mkv': {'codec': 'x265',
            'format': 'HEVC',
            'quality': '1080p',
            'size': 2305},
        'test episode - 02x02 - another in 1080p.mkv': {'codec': 'x265',
            'format': 'HEVC',
            'quality': '1080p',
            'size': 2305},
        'test episode - 02x03 - this is 720p.mkv': {'codec': 'x265',
            'format': 'HEVC',
            'quality': '720p',
            'size': 2303}
        }

class testMisc(unittest.TestCase):


    def setUp(self):
        self.testDataMap = fileMap.getFileMap(testDataDir, useCache=False)


    def testGetFileMap(self):
        self.maxDiff = None
        expectedResult = None
        for path in self.testDataMap.keys():
            if path.endswith('foo'):
                expectedResult = foo
            elif path.endswith('bar'):
                expectedResult = bar
            self.assertEqual(self.testDataMap[path], expectedResult)


    def testGetFileMapCache(self):
        cachedResult = fileMap.getFileMap(testDataDir, useCache=True)
        self.assertDictEqual(self.testDataMap, cachedResult)


    def testPruneMissingFromFileMapEmptyDir(self):
        invalidTestDataMap = deepcopy(self.testDataMap)
        invalidTestDataMap["/foo/bar/this/hopefully/doesnot/exist"] = {}

        self.assertDictEqual(fileMap._pruneMissingFromFileMap(invalidTestDataMap), self.testDataMap)


    def testPruneMissingFromFileMapMissingFile(self):
        invalidTestDataMap = deepcopy(self.testDataMap)
        firstPath = next(iter(invalidTestDataMap.keys()))

        invalidTestDataMap[firstPath]["file that doesn't exist.mkv"] = {}

        self.assertDictEqual(fileMap._pruneMissingFromFileMap(invalidTestDataMap), self.testDataMap)


    def testVideoInCache(self):
        firstPath = next(iter(self.testDataMap.keys()))
        firstFile = next(iter(self.testDataMap[firstPath].keys()))
        self.assertTrue(fileMap._videoInCache(firstFile, firstPath, self.testDataMap))


    def testVideoInCacheBadFilename(self):
        firstPath = next(iter(self.testDataMap.keys()))
        self.assertFalse(fileMap._videoInCache("foo bar baz", firstPath, self.testDataMap))


    def testVideoInCacheBadPath(self):
        firstPath = next(iter(self.testDataMap.keys()))
        firstFile = next(iter(self.testDataMap[firstPath].keys()))
        self.assertFalse(fileMap._videoInCache(firstFile, "/foo/bar/baz/something/something", self.testDataMap))


    def testVideoInCacheBadSize(self):
        localTestDataMap = deepcopy(self.testDataMap)
        firstPath = next(iter(localTestDataMap.keys()))
        firstFile = next(iter(localTestDataMap[firstPath].keys()))
        localTestDataMap[firstPath][firstFile]["size"] = 10000000
        self.assertFalse(fileMap._videoInCache(firstFile, firstPath, localTestDataMap))
