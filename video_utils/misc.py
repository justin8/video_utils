validCodecs = {
        "HEVC": { "ffmpeg": "libx265", "pretty": "x265"},
        "AVC": { "ffmpeg": "h264", "pretty": "x264"}
    }


def getCodecFromFormat(formatString, codecType="ffmpeg"):
    try:
        return validCodecs[formatString][codecType]
    except:
        return "Other"

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


def getTrackQuality(track):
    if track.width >= 1900 and track.width <= 1930:
        return "1080p"
    if track.height >= 1000 and track.height <= 1100:
        return "1080p"
    if track.width >= 1200 and track.width <= 1290:
        return "720p"
    if track.height >= 650 and track.height <= 730:
        return "720p"
    if track.width < 1000:
        return "SD"
    return "Unknown"
