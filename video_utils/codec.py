# TODO: Add automatic creation of additional info about codecs to here instead of validators?

CODEC_DATA = {
    "HEVC": {"ffmpeg_name": "libx265", "pretty_name": "x265"},
    "AVC": {"ffmpeg_name": "h264", "pretty_name": "x264"},
    "AAC": {"ffmpeg_name": "aac", "pretty_name": "aac"},
}


class Codec:

    def __init__(self, format_name, ffmpeg_name=None, pretty_name=None):
        self.format_name = format_name
        self.ffmpeg_name = ffmpeg_name
        self.pretty_name = pretty_name
        self._autodetect()

    def __eq__(self, other):
        if not isinstance(other, Codec):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.format_name == other.format_name

    def __repr__(self):
        return f"<Codec format_name={self.format_name}>"

    def __str__(self):
        return self.__repr__()

    def _autodetect(self):
        try:
            data = CODEC_DATA[next(
                x for x in CODEC_DATA if x == self.format_name)]
            self.ffmpeg_name = self.ffmpeg_name if self.ffmpeg_name else data["ffmpeg_name"]
            self.pretty_name = self.pretty_name if self.pretty_name else data["pretty_name"]
        except StopIteration:
            pass  # No match found
