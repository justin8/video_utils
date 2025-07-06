import os
import sqlite3
import tempfile
from unittest.mock import patch

import pytest

from video_utils import fileMap
from video_utils.video import Video


@pytest.fixture
def target():
    # Clean up any existing cache files
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "video_utils")
    cache_file = os.path.join(cache_dir, "cache.db")
    if os.path.exists(cache_file):
        os.remove(cache_file)

    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = os.path.join(temp_dir, "test_videos")
        os.makedirs(test_dir, exist_ok=True)
        storage = fileMap._FileMapStorage(test_dir)
        yield storage


def test_storage(target):
    assert "test_videos" in target.directory


@patch("os.path.expanduser", autospec=True)
@patch("os.makedirs", autospec=True)
def test_storage_path(mock_makedirs, mock_expanduser, target):
    mock_expanduser.return_value = "/home/some-user"
    expected_storage_path = "/home/some-user/.cache/video_utils"
    result = target.storage_path
    assert result == expected_storage_path + "/cache.db"
    mock_makedirs.assert_called_with(expected_storage_path, exist_ok=True)


def test_storage_load_cache(target):
    # Create test video and save it
    test_video = Video("test.mkv", target.directory)
    test_videos = [test_video]
    target.save_videos(test_videos)

    # Load and verify
    result = target.load()
    assert target.directory in result
    assert len(result[target.directory]) == 1
    assert result[target.directory][0].name == "test.mkv"


def test_storage_load_empty_database(target):
    # Load from empty database
    result = target.load()
    assert result == {}


def test_storage_load_no_cache(target):
    # This test is no longer relevant since cache is always used
    pass


def test_storage_load_corrupt_database(target):
    # Corrupt the database by writing invalid data
    with open(target.storage_path, "w") as f:
        f.write("invalid sqlite data")

    # Should handle corruption gracefully
    result = target.load()
    assert result == {}


def test_storage_save(target):
    test_video = Video("test.mkv", target.directory)
    test_videos = [test_video]

    # Save should not raise an exception
    target.save_videos(test_videos)

    # Verify data was saved by loading it back
    result = target.load()
    assert target.directory in result
    assert len(result[target.directory]) == 1
    assert result[target.directory][0].name == "test.mkv"


def test_storage_remove_existing_files(target):
    # Create and save test videos
    video1 = Video("test1.mkv", target.directory)
    video2 = Video("test2.mkv", target.directory)
    test_videos = [video1, video2]
    target.save_videos(test_videos)

    # Remove one file
    files_to_remove = {video2.full_path}
    target.remove_existing_files(files_to_remove)

    # Verify only the remaining file exists
    result = target.load()
    assert target.directory in result
    assert len(result[target.directory]) == 1
    assert result[target.directory][0].name == "test1.mkv"


def test_database_schema(target):
    # Verify the database schema was created correctly
    with sqlite3.connect(target.storage_path) as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor]
        assert "video_cache" in tables

        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor]
        assert "idx_directory" in indexes
