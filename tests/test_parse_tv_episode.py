import pytest

from video_utils.parse_episode import parse_episode


def test_sXXeXX():
    filenames = [
        "Stargate Atlantis s01e04 foo bar.mkv",
        "Stargate Atlantis S01e04 foo bar.mkv",
        "Stargate Atlantis s01E04 foo bar.mkv",
        "Stargate Atlantis S01E04 foo bar.mkv",
        "Stargate Atlantis - s01e04 foo bar.mkv",
        "Stargate Atlantis s01e04 - foo bar.mkv",
        "Stargate Atlantis - s01e04 - foo bar.mkv",
        "Stargate Atlantis S1E04 foo bar.mkv",
        "Stargate Atlantis S01E4 foo bar.mkv",
    ]

    expectedResult = {
        "season": 1,
        "episode": 4,
        "showName": "Stargate Atlantis",
        "episodeName": "foo bar",
    }

    for filename in filenames:
        result = parse_episode(filename)
        assert result["season"] == expectedResult["season"]
        assert result["episode"] == expectedResult["episode"]
        assert result["showName"] == expectedResult["showName"]
        assert result["episodeName"] == expectedResult["episodeName"]


def test_SSxEE():
    filenames = [
        "One Two Three 20x04 Four Five.mkv",
        "One Two Three 20X04 Four Five.mkv",
        "One Two Three - 20x04 Four Five.mkv",
        "One Two Three 20x04 - Four Five.mkv",
        "One Two Three - 20x04 - Four Five.mkv",
        "One Two Three - 20x4 - Four Five.mkv",
        "One Two Three - 020x04 - Four Five.mkv",
    ]

    expectedResult = {
        "season": 20,
        "episode": 4,
        "showName": "One Two Three",
        "episodeName": "Four Five",
    }

    for filename in filenames:
        result = parse_episode(filename)
        assert result["season"] == expectedResult["season"]
        assert result["episode"] == expectedResult["episode"]
        assert result["showName"] == expectedResult["showName"]
        assert result["episodeName"] == expectedResult["episodeName"]


def test_squareBrackets():
    filenames = [
        "One Two Three [20x04] Four Five.mkv",
        "One Two Three [20X04] Four Five.mkv",
        "One Two Three - [20x04] Four Five.mkv",
        "One Two Three [20x04] - Four Five.mkv",
        "One Two Three - [20x04] - Four Five.mkv",
        "One Two Three - [20x4] - Four Five.mkv",
        "One Two Three - [020x04] - Four Five.mkv",
    ]

    expectedResult = {
        "season": 20,
        "episode": 4,
        "showName": "One Two Three",
        "episodeName": "Four Five",
    }

    for filename in filenames:
        result = parse_episode(filename)
        assert result["season"] == expectedResult["season"]
        assert result["episode"] == expectedResult["episode"]
        assert result["showName"] == expectedResult["showName"]
        assert result["episodeName"] == expectedResult["episodeName"]


def test_badFilename():
    testFilename = "Star Trek (2009).mkv"

    with pytest.raises(ValueError):
        parse_episode(testFilename)
