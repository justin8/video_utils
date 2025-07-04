import pytest
from mock import mock_open, patch

from video_utils import fileMap


@pytest.fixture
def target():
    return fileMap._FileMapStorage("/foo/bar")


def test_storage(target):
    assert target.directory == "/foo/bar"


@patch("os.path.expanduser", autospec=True)
@patch("os.makedirs", autospec=True)
@patch("hashlib.md5")
def test_storage_path(mock_md5, mock_makedirs, mock_expanduser, target):
    mock_expanduser.return_value = "/home/some-user"
    mock_md5().hexdigest.return_value = "12345"
    expected_storage_path = "/home/some-user/.local/share/video_utils"
    result = target.storage_path
    assert result == expected_storage_path + "/12345"
    mock_md5.assert_called_with(b"/foo/bar")
    assert mock_md5().hexdigest.called
    mock_makedirs.assert_called_with(expected_storage_path, exist_ok=True)


@patch("os.path.expanduser", autospec=True)
@patch("os.makedirs", autospec=True)
@patch("pickle.load", autospec=True)
@patch("os.path.exists", autospec=True, return_value=True)
def test_storage_load_cache(
    mock_exists, mock_load, mock_makedirs, mock_expanduser, target
):
    mock_expanduser.return_value = "/home/some-user"
    m = mock_open()
    mock_load.return_value = {"asdfg": 1234}
    with patch("builtins.open", m):
        result = target.load()
        assert result == {"asdfg": 1234}


@patch("pickle.load", autospec=True)
@patch("os.path.exists", autospec=True, return_value=False)
def test_storage_load_no_file(mock_exists, mock_load, target):
    m = mock_open()
    mock_load.return_value = {"asdfg": 1234}
    with patch("builtins.open", m):
        result = target.load()
        assert result == {}


@patch("pickle.load", autospec=True)
@patch("os.path.exists", autospec=True, return_value=True)
def test_storage_load_no_cache(mock_exists, mock_load, target):
    m = mock_open()
    mock_load.return_value = {"asdfg": 1234}
    with patch("builtins.open", m):
        result = target.load(use_cache=False)
        assert result == {}


@patch("pickle.load", autospec=True)
@patch("os.path.exists", autospec=True, return_value=True)
def test_storage_load_corrupt_file(mock_exists, mock_load, target):
    m = mock_open()
    mock_load.side_effect = EOFError
    with patch("builtins.open", m):
        result = target.load()
        assert result == {}


@patch("pickle.dump", autospec=True)
def test_storage_save(mock_dump, target):
    m = mock_open()
    with patch("__main__.open", m):
        target.save("asdf")
    mock_dump.assert_called()
