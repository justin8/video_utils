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


def test_duration_init():
    v = Video("foo.mkv", "/not-a-real-path/bar", duration=120000)
    assert v.duration == 120000


def test_duration_init_none():
    v = Video("foo.mkv", "/not-a-real-path/bar")
    assert v.duration is None


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
    def mock_st_size():
        return None

    setattr(mock_st_size, "st_size", 12345)
    return mock_st_size


@patch("video_utils.video.MediaInfo", autospec=True)
@patch("video_utils.validators.Validator", autospec=True)
@patch("video_utils.video.Video._get_size", autospec=True, return_value=12345)
@patch("video_utils.video.Video._needs_refresh", autospec=True, return_value=True)
def test_refresh(mock_needs_refresh, mock_get_size, mock_validator, mock_media_info):
    expected_codec = Codec("HEVC")
    mock_media_info.parse.return_value = metadata_return()
    mock_validator().quality_similar_to.return_value = "1080p"

    v = Video("foo.mkv", "/not-a-real-path/bar")
    v.refresh()

    assert v.codec == expected_codec
    assert v.quality == "1080p"
    assert v.size_b == 12345
    assert v.duration == 1436031.0


@patch("video_utils.video.MediaInfo.parse")
@patch("video_utils.validators.Validator", autospec=True)
@patch("video_utils.video.Video._needs_refresh", autospec=True, return_value=False)
def test_refresh_not_required(mock_needs_refresh, mock_validator, mock_parse):
    v = Video("foo.mkv", "/not-a-real-path/bar")
    v.refresh()
    assert mock_parse.called is False


@patch("video_utils.video.Video._get_size", autospec=True, return_value=12345)
def test_needs_refresh_no_size(mock_stat):
    mock_stat.return_value = stat_return()
    v = Video("foo.mkv", "/not-a-real-path/bar")
    assert v._needs_refresh() is True


@patch("video_utils.video.Video._get_size", autospec=True, return_value=12345)
def test_needs_refresh_size_different(mock_stat):
    mock_stat.return_value = stat_return()
    v = Video("foo.mkv", "/not-a-real-path/bar", size_b=1)
    assert v._needs_refresh() is True


@patch("video_utils.video.Video._get_size", autospec=True, return_value=12345)
def test_needs_refresh_false(mock_stat):
    mock_stat.return_value = 12345
    v = Video("foo.mkv", "/not-a-real-path/bar", size_b=12345)
    assert v._needs_refresh() is False


@patch("os.stat", autospec=True)
def test_get_size(mock_stat):
    mock_stat.return_value = stat_return()
    v = Video("foo.mkv", "/not-a-real-path/bar", size_b=555)
    assert v._get_size() == 12345


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


@patch("video_utils.video.MediaInfo", autospec=True)
@patch("os.stat", autospec=True)
@patch("video_utils.validators.Validator", autospec=True)
def test_subtitle_languages(mock_validator, mock_stat, mock_media_info):
    mock_stat.return_value = stat_return()
    metadata = metadata_return()
    mock_media_info.parse.return_value = metadata

    v = Video("foo.mkv", "/not-a-real-path/bar")
    v.refresh()
    assert v.subtitle_languages == ["eng", "eng"]


@patch("video_utils.video.MediaInfo", autospec=True)
@patch("os.stat", autospec=True)
@patch("video_utils.validators.Validator", autospec=True)
def test_audio_languages(mock_validator, mock_stat, mock_media_info):
    mock_stat.return_value = stat_return()
    metadata = metadata_return()
    mock_media_info.parse.return_value = metadata

    v = Video("foo.mkv", "/not-a-real-path/bar")
    v.refresh()
    assert v.audio_languages == ["jpn"]
