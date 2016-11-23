import unittest

import video_utils

class testParseTVEpisode(unittest.TestCase):

    def test_sXXeXX(self):
        filenames = ["Stargate Atlantis s01e04 foo bar.mkv",
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
            result = video_utils.parseTVEpisode(filename)
            self.assertEqual(result['season'], expectedResult['season'])
            self.assertEqual(result['episode'], expectedResult['episode'])
            self.assertEqual(result['showName'], expectedResult['showName'])
            self.assertEqual(result['episodeName'], expectedResult['episodeName'])


    def test_SSxEE(self):
        filenames = ["One Two Three 20x04 Four Five.mkv",
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
            result = video_utils.parseTVEpisode(filename)
            self.assertEqual(result['season'], expectedResult['season'])
            self.assertEqual(result['episode'], expectedResult['episode'])
            self.assertEqual(result['showName'], expectedResult['showName'])
            self.assertEqual(result['episodeName'], expectedResult['episodeName'])


    def test_squareBrackets(self):
        filenames = ["One Two Three [20x04] Four Five.mkv",
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
            result = video_utils.parseTVEpisode(filename)
            self.assertEqual(result['season'], expectedResult['season'])
            self.assertEqual(result['episode'], expectedResult['episode'])
            self.assertEqual(result['showName'], expectedResult['showName'])
            self.assertEqual(result['episodeName'], expectedResult['episodeName'])
