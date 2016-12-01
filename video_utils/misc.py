validCodecs = {
        "HEVC": { "ffmpeg": "libx265", "pretty": "x265"},
        "AVC": { "ffmpeg": "h264", "pretty": "x264"}
    }


def getCodecFromFormat(formatString, codecType="ffmpeg"):
    try:
        return validCodecs[formatString][codecType]
    except:
        return "Other"


def getPrettyCodecFromFFMPEGCodec(codec):
    for validCodec in validCodecs.values():
        if validCodec['ffmpeg'] == codec:
            return validCodec['pretty']
    raise Exception("Unable to parse codec")

def listParsableCodecs(codecType="ffmpeg"):
    output = []
    for codec in validCodecs.values():
        output.append(codec[codecType])
    return output


def isFormatStringParsable(formatString):
    if formatString in validCodecs.values():
        return True
    raise Exception("Unsupported format string requested")


def isVideo(f):
    videoExtensions = ("avi", "divx", "mkv", "mp4", "mpg", "mpeg", "mov", "m4v", "flv", "ts", "wmv")
    return f.lower().endswith(videoExtensions)


def getVideosInFileList(fileList):
    videos = []
    for filename in fileList:
        if isVideo(filename):
            videos.append(filename)
    videos.sort()
    return videos


def _isSimilarTo(value, target):
    return target * 0.9 <= value <= target * 1.1


def getTrackQuality(track):
    if _isSimilarTo(track.width, 1920):
        return "1080p"
    if _isSimilarTo(track.height, 1080):
        return "1080p"
    if _isSimilarTo(track.width, 1280):
        return "720p"
    if _isSimilarTo(track.height, 720):
        return "720p"
    if track.width < 1000:
        return "SD"
    return "Unknown"
