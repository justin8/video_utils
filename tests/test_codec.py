import pytest

from video_utils import Codec


def test_codec():
    c = Codec("AVC", "h264", "x264")
    assert c.format_name == "AVC"
    assert c.ffmpeg_name == "h264"
    assert c.pretty_name == "x264"


def test_codec_minimal():
    c = Codec("foo")
    assert c.format_name == "foo"
    assert c.ffmpeg_name == None
    assert c.pretty_name == None


def test_codec_autodetect():
    c = Codec("HEVC")
    assert c.format_name == "HEVC"
    assert c.ffmpeg_name == "libx265"
    assert c.pretty_name == "x265"


def test_codec_equality():
    dummy_codec = Codec("AVC", ffmpeg_name="h264", pretty_name="x264")
    different_codec = Codec("HEVC", ffmpeg_name="libx265", pretty_name="x265")
    same_codec = Codec("AVC", ffmpeg_name="h264", pretty_name="x264")
    not_a_codec = "I'm ralph, not a codec"

    assert dummy_codec == same_codec
    assert dummy_codec != different_codec
    with pytest.raises(AssertionError):
        assert dummy_codec == not_a_codec
