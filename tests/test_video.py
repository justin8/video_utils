import pytest
import os
from os import path
from mock import patch
import pickle

from video_utils import Video, Codec


def test_minimal():
    v = Video("foo.mkv", "/not-a-real-path/bar")
    assert v.name == "foo.mkv"
    assert v.dir_path == "/not-a-real-path/bar"


def test_full_path():
    v = Video("foo.mkv", "/not-a-real-path/bar")
    assert v.full_path == "/not-a-real-path/bar/foo.mkv"


def test_equality():
    instance = Video("foo.mkv", "/not-a-real-path/bar")
    duplicate = Video("foo.mkv", "/not-a-real-path/bar")
    different_video = Video("bar.mkv", "/not-a-real-path/bar")
    different_path = Video("foo.mkv", "/not-a-real-path/baz")
    not_a_video = "I'm not a video!"

    assert instance == duplicate
    assert instance != different_video
    assert instance != different_path
    with pytest.raises(AssertionError):
        assert instance == not_a_video


def test_dir_path_setter():
    v = Video("foo.mkv", "./foo")
    assert v.dir_path == f"{os.getcwd()}/foo"


def test_quality_setter_default():
    v = Video("foo.mkv", "./foo")
    v.quality = None
    assert v.quality == "Unknown"


def test_quality_setter_happy_path():
    v = Video("foo.mkv", "./foo")
    v.quality = "1080p"
    assert v.quality == "1080p"
    v.quality = "720p"
    assert v.quality == "720p"
    v.quality = "SD"
    assert v.quality == "SD"


def test_quality_setter_failure():
    v = Video("foo.mkv", "./foo")
    with pytest.raises(AttributeError):
        v.quality = "not-a-real-quality"


def test_codec_setter_invalid_type():
    v = Video("foo.mkv", "./foo")
    with pytest.raises(TypeError):
        v.codec = "not-a-codec"


def test_codec_setter():
    v = Video("foo.mkv", "./foo")
    codec = Codec("foo", "bar", "baz")
    v.codec = codec
    assert v.codec == codec


def metadata_return():
    current_dir = path.dirname(path.abspath(__file__))
    test_data_dir = path.join(current_dir, "testData")
    metadata_file = path.join(test_data_dir, "metadata.pickle")
    with open(metadata_file, "rb") as f:
        return pickle.load(f)


def stat_return():
    def mock_st_size(): return None
    setattr(mock_st_size, "st_size", 12345)
    return mock_st_size


@patch("video_utils.video.MediaInfo", autospec=True)
@patch("os.stat", autospec=True)
@patch("video_utils.validators.Validator", autospec=True)
def test_refresh(mock_validator, mock_stat, mock_media_info):
    expected_codec = Codec("HEVC")
    mock_stat.return_value = stat_return()
    mock_media_info.parse.return_value = metadata_return()
    mock_validator().quality_similar_to.return_value = "1080p"

    v = Video("foo.mkv", "/not-a-real-path/bar")
    v.refresh()

    assert v.codec == expected_codec
    assert v.quality == "1080p"
    assert v.size == 12345


@patch("video_utils.video.MediaInfo", autospec=True)
@patch("os.stat", autospec=True)
@patch("video_utils.validators.Validator", autospec=True)
def test_refresh_failure(mock_validator, mock_stat, mock_media_info):
    mock_stat.return_value = stat_return()
    metadata = metadata_return()
    for track in metadata.tracks:
        track.track_type = "not-video"
    mock_media_info.parse.return_value = metadata
    mock_validator().quality_similar_to.return_value = "1080p"

    v = Video("foo.mkv", "/not-a-real-path/bar")
    with pytest.raises(RuntimeError):
        v.refresh()
