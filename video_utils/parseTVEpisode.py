import os
import re
import logging
 
log = logging.getLogger()

def _splitData(filename):
    results = re.findall("(.*?)\ ?(?:\-\ ?)?\[?(?:[Ss](?=\d+[eE]\d+))?(\d+)[XxeE](\d+)\]?(?:\ ?\-)?\ ?(.*)", filename)
    if results:
        return results[0]
    return (None, None, None, None)


def parseTVEpisode(filename):
    shortname = os.path.basename(filename)
    shortname = os.path.splitext(shortname)[0]
    showName, season, episode, episodeName = _splitData(shortname)
    try:
        season = int(season)
        episode = int(episode)
    except:
        pass
    result = {
            "showName": showName,
            "episode": episode,
            "season": season,
            "episodeName": episodeName,
        }
    log.debug("Parsed %s from %s" % (filename, str(result)))
    return result
