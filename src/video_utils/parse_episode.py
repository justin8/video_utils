import os
import re
import logging
from typing import Optional, Tuple, Dict

log = logging.getLogger(__name__)


def _split_data(filename: str) -> Tuple[str, str, str, str]:
    results = re.findall(
        r"(.*?)\ ?(?:\-\ ?)?\[?(?:[Ss](?=\d+[eE]\d+))?(\d+)[XxeE](\d+)\]?(?:\ ?\-)?\ ?(.*)",
        filename,
    )
    if results:
        return results[0]
    raise ValueError


def parse_episode(filename: str) -> Dict[str, Optional[str]]:
    shortname = os.path.basename(filename)
    shortname = os.path.splitext(shortname)[0]
    showName, season, episode, episodeName = _split_data(shortname)

    try:
        season = int(season)
        episode = int(episode)
    except TypeError:
        log.debug("Failed to parse season or episode number")
    result = {
        "showName": showName,
        "episode": episode,
        "season": season,
        "episodeName": episodeName,
    }
    log.debug("Parsed %s from %s" % (filename, str(result)))
    return result
