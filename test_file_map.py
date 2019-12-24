import os
from pytest import fixture
from copy import deepcopy

from video_utils import fileMap

current_dir = os.path.dirname(os.path.abspath(__file__))
test_data_dir = os.path.join(current_dir, "testData")
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


@fixture
def data_map():
    return fileMap.getFileMap(test_data_dir, useCache=False)


def testGetFileMap(data_map):
    expectedResult = None
    for path in data_map.keys():
        if path.endswith('foo'):
            expectedResult = foo
        elif path.endswith('bar'):
            expectedResult = bar
        assert data_map[path] == expectedResult


def testGetFileMapSingleFile():
    expectedResult = {'test episode - 02x03 - this is 720p.mkv':
                      {'codec': 'x265',
                          'format': 'HEVC',
                          'quality': '720p',
                          'size': 2303
                       }
                      }
    videoPath = os.path.join(
        test_data_dir, 'foo/test episode - 02x03 - this is 720p.mkv')
    rawResult = fileMap.getFileMap(videoPath, useCache=False)
    result = next(iter(rawResult.values()))
    assert result == expectedResult


def testGetFileMapCache(data_map):
    cachedResult = fileMap.getFileMap(test_data_dir, useCache=True)
    assert data_map == cachedResult


def testPruneMissingFromFileMapEmptyDir(data_map):
    invalidTestDataMap = deepcopy(data_map)
    invalidTestDataMap["/foo/bar/this/hopefully/doesnot/exist"] = {}

    assert fileMap._pruneMissingFromFileMap(
        invalidTestDataMap) == data_map


def testPruneMissingFromFileMapMissingFile(data_map):
    invalidTestDataMap = deepcopy(data_map)
    firstPath = next(iter(invalidTestDataMap.keys()))

    invalidTestDataMap[firstPath]["file that doesn't exist.mkv"] = {}

    assert fileMap._pruneMissingFromFileMap(
        invalidTestDataMap) == data_map


def testVideoInCache(data_map):
    firstPath = next(iter(data_map.keys()))
    firstFile = next(iter(data_map[firstPath].keys()))
    assert fileMap._videoInCache(firstFile, firstPath, data_map)


def testVideoInCacheBadFilename(data_map):
    firstPath = next(iter(data_map.keys()))
    result = fileMap._videoInCache("foo bar baz", firstPath, data_map)
    assert result == False


def testVideoInCacheBadPath(data_map):
    firstPath = next(iter(data_map.keys()))
    firstFile = next(iter(data_map[firstPath].keys()))
    result = fileMap._videoInCache(
        firstFile, "/foo/bar/baz/something/something", data_map)
    assert result == False


def testVideoInCacheBadSize(data_map):
    localTestDataMap = deepcopy(data_map)
    firstPath = next(iter(localTestDataMap.keys()))
    firstFile = next(iter(localTestDataMap[firstPath].keys()))
    localTestDataMap[firstPath][firstFile]["size"] = 10000000
    result = fileMap._videoInCache(firstFile, firstPath, localTestDataMap)
    assert result == False
