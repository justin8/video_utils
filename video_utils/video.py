import logging
import os
from os import path
from typing import List

from pymediainfo import MediaInfo
from iso639 import to_iso639_2

from .validators import Validator
from .codec import Codec

log = logging.getLogger(__name__)


class Video:
    def __init__(self, name, dir_path, codec=None, quality=None, size=None, video_track=None, audio_tracks=None, text_tracks=None):
        self.name = name
        self.dir_path = dir_path
        self.codec = codec
        self.quality = quality
        self.size = size
        self.video_track = video_track
        self.audio_tracks = audio_tracks
        self.text_tracks = text_tracks

    def __eq__(self, other):
        if not isinstance(other, Video):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.full_path == other.full_path

    def __repr__(self):
        return f"<Video name={self.name} codec={self.codec} quality={self.quality}>"

    def __str__(self):
        return self.__repr__()

    @property
    def subtitle_languages(self) -> List[str]:
        if self.text_tracks:
            return [to_iso639_2(x.language) for x in self.text_tracks]
        return []

    @property
    def audio_languages(self) -> List[str]:
        if self.audio_tracks:
            return [to_iso639_2(x.language) for x in self.audio_tracks]
        return []

    @property
    def dir_path(self) -> str:
        return self._dir_path

    @dir_path.setter
    def dir_path(self, value):
        self._dir_path = path.realpath(value)

    @property
    def full_path(self) -> str:
        return path.join(self.dir_path, self.name)

    @property
    def codec(self):
        return self._codec

    @codec.setter
    def codec(self, value):
        if value is not None and not isinstance(value, Codec):
            raise TypeError("An object of type Codec must be specified")
        self._codec = value

    @property
    def quality(self):
        return self._quality

    @quality.setter
    def quality(self, value):
        if value is None:
            value = "Unknown"
        Validator().quality(value)
        self._quality = value

    def _needs_refresh(self):
        if self.size != self._get_size():
            return True
        log.debug(f"Skipping refresh on '{self.full_path}'")
        return False

    def _get_size(self):
        return os.stat(self.full_path).st_size

    def refresh(self):
        """
        Reads the metadata for the given filename and path from the filesystem and saves it to this instance
        """
        if self._needs_refresh():
            log.debug(f"Refreshing data for video: {self.full_path}")
            self.size = self._get_size()
            metadata = MediaInfo.parse(self.full_path)
            self.audio_tracks = metadata.audio_tracks  # type: ignore
            self.text_tracks = metadata.text_tracks  # type: ignore
            try:
                self.video_track = metadata.video_tracks[0]  # type: ignore
            except IndexError:
                raise RuntimeError

            self.quality = Validator().quality_similar_to(self.video_track)
            self.codec = Codec(format_name=self.video_track.format)
            if self.quality == "Unknown":
                error_message = f"Failed to parse track metadata from {self.full_path}"
                log.error(error_message)
                raise RuntimeError(error_message)
