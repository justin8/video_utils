import os
import re
import logging

log = logging.getLogger(__name__)


def _split_data(filename):
    results = re.findall(
        r"(.*?)\ ?(?:\-\ ?)?\[?(?:[Ss](?=\d+[eE]\d+))?(\d+)[XxeE](\d+)\]?(?:\ ?\-)?\ ?(.*)", filename)
    if results:
        return results[0]
    return (None, None, None, None)


def parse_episode(filename):
    shortname = os.path.basename(filename)
    shortname = os.path.splitext(shortname)[0]
    showName, season, episode, episodeName = _split_data(shortname)
    try:
        season = int(season)
        episode = int(episode)
    except TypeError:
        log.info("Failed to parse season or episode number")
    result = {
        "showName": showName,
        "episode": episode,
        "season": season,
        "episodeName": episodeName,
    }
    log.debug("Parsed %s from %s" % (filename, str(result)))
    return result
