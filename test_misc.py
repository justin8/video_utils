from video_utils import misc


def test_get_videos_in_list():
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

    assert misc.getVideosInFileList(test_data) == expected_result


def test_is_video():
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
        assert misc.isVideo(filename) == True

    for filename in nonVideoFilenames:
        assert misc.isVideo(filename) == False


def test_get_codec_x265():
    assert misc.getCodecFromFormat("HEVC") == "libx265"
    assert misc.getCodecFromFormat("HEVC", codecType="pretty") == "x265"


def test_get_codec_x264():
    assert misc.getCodecFromFormat("AVC") == "h264"
    assert misc.getCodecFromFormat("AVC", codecType="pretty") == "x264"


def test_get_codec_other():
    assert misc.getCodecFromFormat("foo") == "Other"
    assert misc.getCodecFromFormat("foo", codecType="pretty") == "Other"


def testGetQualityWidth1080p():
    testData = [1900, 1920, 1930]

    for width in testData:
        def track(): return None
        track.width = width
        track.height = 0
        quality = misc.getTrackQuality(track)
        assert quality == "1080p"


def testGetTrackQualityWidth720p():
    testData = [1200, 1280, 1290]

    for width in testData:
        def track(): return None
        track.width = width
        track.height = 0
        quality = misc.getTrackQuality(track)
        assert quality == "720p"


def testGetTrackQualityWidthSD():
    testData = [400, 800, 999]

    for width in testData:
        def track(): return None
        track.width = width
        track.height = 0
        quality = misc.getTrackQuality(track)
        assert quality == "SD"


def testGetTrackQualityWidthOther():
    testData = [1100, 2500]

    for width in testData:
        def track(): return None
        track.width = width
        track.height = 0
        quality = misc.getTrackQuality(track)
        assert quality == "Unknown"


def testGetTrackQualityHeight1080p():
    testData = [1000, 1080, 1100]

    for height in testData:
        def track(): return None
        track.height = height
        track.width = 0
        quality = misc.getTrackQuality(track)
        assert quality == "1080p"


def testGetTrackQualityHeight720p():
    testData = [650, 720, 730]

    for height in testData:
        def track(): return None
        track.height = height
        track.width = 0
        quality = misc.getTrackQuality(track)
        assert quality == "720p"
