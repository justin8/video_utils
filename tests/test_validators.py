import pytest

from video_utils import validators


@pytest.fixture
def target():
    return validators.Validator()


def test_is_video(target):
    video_filenames = ["test file 123x124 - name.avi",
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
    for video in video_filenames:
        assert target.is_video(video)


def test_is_not_video(target):
    non_video_filenames = ["test file 123x124 - name.foo",
                           "test file 123x124 - name.bar",
                           "test file 123x124 - name.txt",
                           "test file 123x124 - name.jpg",
                           ]
    for video in non_video_filenames:
        assert not target.is_video(video)


class StubTrack:
    def __init__(self, width, height):
        self.width = width
        self.height = height


def test_quality_similar_to(target):
    tests = [
        {"input": StubTrack(1920, 1080), "expected_output": "1080p"},
        {"input": StubTrack(1920, 10), "expected_output": "1080p"},
        {"input": StubTrack(10, 1080), "expected_output": "1080p"},
        {"input": StubTrack(1850, 900), "expected_output": "1080p"},
        {"input": StubTrack(1280, 720), "expected_output": "720p"},
        {"input": StubTrack(1280, 10), "expected_output": "720p"},
        {"input": StubTrack(10, 720), "expected_output": "720p"},
        {"input": StubTrack(1100, 650), "expected_output": "720p"},
        {"input": StubTrack(800, 600), "expected_output": "SD"},
        {"input": StubTrack(100000, 100000), "expected_output": "Unknown"},

    ]
    for test in tests:
        result = target.quality_similar_to(test["input"])
        print(
            f"Testing quality_similar_to for input: {test['input'].width}x{test['input'].height}. Expected result: {test['expected_output']}")
        assert result == test["expected_output"]


def test_quality(target):
    valid_qualities = ["1080p", "720p", "SD", "Unknown"]
    for quality in valid_qualities:
        target.quality(quality)  # Shouldn't raise an exception


def test_quality_failure(target):
    invalid_qualities = ["not-a-quality", "some-other-thing", "etc"]
    for quality in invalid_qualities:
        with pytest.raises(AttributeError):
            target.quality(quality)


def test_filter_only_videos():
    f = validators.Filter()
    filenames = ["test file 123x124 - name.foo",
                 "test file 123x124 - name.bar",
                 "test file 123x124 - name.txt",
                 "test file 123x124 - name.jpg",
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

    result = f.only_videos(filenames)
    assert len(result) == 10
