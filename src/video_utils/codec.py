from typing import Optional

# TODO: Add automatic creation of additional info about codecs to here instead of validators?

# Key is the codec format returned by MediaInfo
CODEC_DATA = {
    "AV1": {"ffmpeg_names": {"software": "libaom-av1"}, "pretty_name": "av1"},
    "HEVC": {
        "ffmpeg_names": {
            "software": "libx265",
            "nvidia": "hevc_nvenc",
            "intel": "hevc_qsv",
        },
        "pretty_name": "HEVC",
    },
    "AVC": {
        "ffmpeg_names": {
            "software": "h264",
            "nvidia": "h264_nvenc",
            "intel": "h264_qsv",
        },
        "pretty_name": "h264",
    },
    "AAC": {"ffmpeg_names": {"software": "aac"}, "pretty_name": "aac"},
}


class Codec:
    def __init__(
        self,
        format_name: str,
        ffmpeg_name: Optional[str] = None,
        pretty_name: Optional[str] = None,
    ) -> None:
        self.format_name = format_name
        self._ffmpeg_name = ffmpeg_name
        self.pretty_name = pretty_name
        self._autodetect()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Codec):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.format_name == other.format_name

    def __repr__(self) -> str:
        return f"<Codec format_name={self.format_name}>"

    def __str__(self) -> str:
        return self.__repr__()

    def _autodetect(self) -> None:
        try:
            self._data = CODEC_DATA[self.format_name]
            self.pretty_name = (
                self.pretty_name if self.pretty_name else self._data["pretty_name"]
            )
        except KeyError:
            pass  # No match found

    def get_ffmpeg_name(self, encoder: str = "software") -> Optional[str]:
        if self._ffmpeg_name:
            return self._ffmpeg_name
        try:
            return self._data["ffmpeg_names"][encoder]
        except:  # noqa
            return None
