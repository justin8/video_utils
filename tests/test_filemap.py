import os
import pickle
from os import path

import pytest
from mock import patch

from video_utils import fileMap


@pytest.fixture
def os_walk():
    return [
        ("/tmp", ["foo", "bar"], ["metadata.pickle"]),
        (
            "/tmp/foo",
            [],
            [
                "not-a-video.txt",
                "test episode - 02x03 - this is 720p.mkv",
                "test episode - 02x02 - another in 1080p.mkv",
                "test episode - 01x02 - another in 1080p.mkv",
                "an-image.jpg",
                "test episode - 01x03 - another in 1080p.mkv",
                "test episode - 01x01 - another in 1080p.mkv",
                "test episode - 02x01 - this is 1080p.avi",
            ],
        ),
        (
            "/tmp/bar",
            [],
            [
                "test episode - 02x03 - this is 720p.mkv",
                "test episode - 02x02 - another in 1080p.mkv",
                "test episode - 02x01 - this is 1080p.mkv",
                "test episode - 01x02 - another in 1080p.mkv",
                "test episode - 01x03 - another in 1080p.mkv",
                "test episode - 01x01 - another in 1080p.mkv",
            ],
        ),
    ]


@pytest.fixture
def mock_contents():
    current_dir = path.dirname(path.abspath(__file__))
    test_data_dir = path.join(current_dir, "testData")
    contents_file = path.join(test_data_dir, "contents.pickle")
    with open(contents_file, "rb") as f:
        return pickle.load(f)


@pytest.fixture
def target():
    return fileMap.FileMap("/foo")


def test_init(target):
    pass


def test_init_failure():
    # This test is no longer relevant since use_cache parameter was removed
    pass


def test_init_validator(target):
    # This test is no longer relevant since use_cache was removed
    pass


def test_init_validator_reverse(target):
    # This test is no longer relevant since use_cache was removed
    pass


def test_directory_setter(target):
    f = fileMap.FileMap("./foo")
    assert f.directory == f"{os.getcwd()}/foo"


@patch("video_utils.fileMap._FileMapStorage")
@patch.object(fileMap.FileMap, "_update_content")
def test_load(mock_update_content, mock_storage, target):
    target.load()
    assert mock_update_content.called
    assert mock_storage.called
    assert mock_storage().load.called


@patch("video_utils.fileMap._FileMapStorage")
@patch.object(fileMap.FileMap, "_update_content")
def test_load_skips_update(mock_update_content, mock_storage, target):
    target.update = False
    target.load()
    assert not mock_update_content.called
    assert mock_storage.called
    assert mock_storage().load.called


@patch.object(fileMap.FileMap, "_prune_missing_files")
@patch.object(fileMap.FileMap, "_update_video")
@patch.object(fileMap.FileMap, "_file_tree")
@patch("video_utils.validators.Filter")
def test_update_content_prunes_on_cache_use(
    mock_filter, mock_file_tree, mock_update_video, mock_prune, target
):
    target._update_content()
    assert not mock_prune.called  # Prune is now called in load(), not _update_content()


@patch.object(fileMap.FileMap, "_prune_missing_files")
@patch.object(fileMap.FileMap, "_update_video")
@patch.object(fileMap.FileMap, "_file_tree")
@patch("video_utils.validators.Filter")
def test_update_content_no_cache_fork(
    mock_filter, mock_file_tree, mock_update_video, mock_prune, target
):
    # Prune is now called in load(), not _update_content()
    target._update_content()
    assert not mock_prune.called


@patch.object(fileMap.FileMap, "_prune_missing_files")
@patch.object(fileMap.FileMap, "_update_video")
@patch("video_utils.validators.Filter")
def test_update_content(mock_filter, mock_update_video, mock_prune, target, os_walk):
    target._file_tree = lambda: os_walk
    target._update_content()

    files = [
        "test episode - 02x03 - this is 720p.mkv",
        "test episode - 02x02 - another in 1080p.mkv",
        "test episode - 01x02 - another in 1080p.mkv",
        "test episode - 01x03 - another in 1080p.mkv",
        "test episode - 01x01 - another in 1080p.mkv",
        "test episode - 02x01 - this is 1080p.avi",
        "test episode - 02x03 - this is 720p.mkv",
    ]

    for f in files:
        mock_update_video.assert_any_call("/tmp/foo", f)


@patch.object(fileMap, "Video")
def test_update_video(mock_video, target):
    target._update_video("/tmp", "foo.mkv")
    assert mock_video().refresh.called
    assert target.contents["/tmp"]
    assert len(target.contents["/tmp"]) == 1
    assert len(target.contents) == 1


@patch("os.walk")
@patch("os.path.isfile")
def test_file_tree_directory(mock_isfile, mock_walk, target, os_walk):
    mock_walk.return_value = os_walk
    mock_isfile.return_value = False
    target._file_tree()
    assert target._file_tree() == os_walk


@patch("os.walk")
@patch("os.path.isfile")
def test_file_tree_file(mock_isfile, mock_walk, target, os_walk):
    mock_walk.return_value = os_walk
    mock_isfile.return_value = True
    target._file_tree()
    assert target._file_tree() == [("/", [], ["foo"])]


@patch("os.path.exists")
def test_prune_missing_files_no_directory(mock_exists, target, mock_contents):
    def isexists_return(file_path):
        if file_path == "/home/justin/git/video_utils/tests/testData/bar":
            return False
        return True

    target.contents = mock_contents
    mock_exists.side_effect = isexists_return
    target._prune_missing_files()
    assert "/home/justin/git/video_utils/tests/testData/foo" in target.contents.keys()
    assert (
        "/home/justin/git/video_utils/tests/testData/bar" not in target.contents.keys()
    )
    assert len(target.contents.keys()) == 1
    assert len(target.contents["/home/justin/git/video_utils/tests/testData/foo"]) == 18


@patch("os.path.exists")
@patch(
    "video_utils.fileMap._FileMapStorage.storage_path",
    new_callable=lambda: property(lambda self: "/tmp/test_cache.db"),
)
def test_prune_missing_files_no_file(
    mock_storage_path, mock_exists, target, mock_contents
):
    missing_file = "/home/justin/git/video_utils/tests/testData/bar/test episode - 01x01 - another in 1080p.mkv"

    def isexists_return(file_path):
        if file_path == missing_file:
            return False
        return True

    target.contents = mock_contents
    mock_exists.side_effect = isexists_return
    target._prune_missing_files()
    assert "/home/justin/git/video_utils/tests/testData/foo" in target.contents.keys()
    assert "/home/justin/git/video_utils/tests/testData/bar" in target.contents.keys()
    assert len(target.contents.keys()) == 2
    assert (
        missing_file
        not in target.contents["/home/justin/git/video_utils/tests/testData/bar"]
    )
    assert len(target.contents["/home/justin/git/video_utils/tests/testData/foo"]) == 18
    assert len(target.contents["/home/justin/git/video_utils/tests/testData/bar"]) == 15


def test_subdirectory_filtering():
    """Test that FileMap for subdirectory only loads files from that subdirectory"""
    current_dir = path.dirname(path.abspath(__file__))
    test_data_dir = path.join(current_dir, "testData")

    # First load the parent directory to populate cache
    parent_filemap = fileMap.FileMap(test_data_dir, progress_bar=False)
    parent_filemap.load()

    # Now load just the foo subdirectory
    foo_dir = path.join(test_data_dir, "foo")
    foo_filemap = fileMap.FileMap(foo_dir, progress_bar=False)
    foo_filemap.load()

    # Should only have files from foo directory
    assert foo_dir in foo_filemap.contents
    bar_dir = path.join(test_data_dir, "bar")
    assert bar_dir not in foo_filemap.contents

    # Verify all files in contents are from foo directory
    for directory, videos in foo_filemap.contents.items():
        assert directory.startswith(foo_dir)
        for video in videos:
            assert video.full_path.startswith(foo_dir)
