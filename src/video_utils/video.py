import logging
import os
from enum import Enum
from os import path
from typing import List, Optional

from iso639 import to_iso639_2
from pymediainfo import MediaInfo

from .codec import Codec
from .validators import Validator

log = logging.getLogger(__name__)


class Resolution(Enum):
    P576 = "576p"
    P720 = "720p"
    P1080 = "1080p"
    P2160 = "2160p"
    OTHER = "other"


class Video:
    # Increment this when adding new fields or changing the structure
    SCHEMA_VERSION = 2

    def __init__(
        self,
        name: str,
        dir_path: str,
        codec: Optional[Codec] = None,
        quality: Optional[str] = None,
        size_b: Optional[int] = None,
        duration: Optional[float] = None,
        video_track: Optional[object] = None,
        audio_tracks: Optional[List[object]] = None,
        text_tracks: Optional[List[object]] = None,
        resolution: Optional[Resolution] = None,
        schema_version: Optional[int] = None,
    ):
        self.name = name
        self.dir_path = dir_path
        self.codec = codec
        self.quality = quality
        self.size_b = size_b
        self.duration = duration
        self.video_track = video_track
        self.audio_tracks = audio_tracks
        self.text_tracks = text_tracks
        self.resolution = resolution
        self.schema_version = schema_version or self.SCHEMA_VERSION

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Video):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.full_path == other.full_path

    def __repr__(self) -> str:
        return f"<Video name={self.name} codec={self.codec} quality={self.quality} resolution={self.resolution}>"

    def __str__(self) -> str:
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
    def dir_path(self, value: str) -> None:
        self._dir_path = path.realpath(value)

    @property
    def full_path(self) -> str:
        return path.join(self.dir_path, self.name)

    @property
    def codec(self) -> Optional[Codec]:
        return self._codec

    @codec.setter
    def codec(self, value: Optional[Codec]) -> None:
        if value is not None and not isinstance(value, Codec):
            raise TypeError("An object of type Codec must be specified")
        self._codec = value

    @property
    def quality(self) -> Optional[str]:
        return self._quality

    @quality.setter
    def quality(self, value: Optional[str]) -> None:
        if value is None:
            value = "Unknown"
        Validator().quality(value)
        self._quality = value

    def _determine_resolution(self, width: int) -> Resolution:
        """Determine resolution based on video width with 10% tolerance"""
        resolutions = {
            1024: Resolution.P576,  # 576p (1024x576)
            1280: Resolution.P720,  # 720p (1280x720)
            1920: Resolution.P1080,  # 1080p (1920x1080)
            3840: Resolution.P2160,  # 2160p (3840x2160)
        }

        for target_width, resolution in resolutions.items():
            if abs(width - target_width) / target_width <= 0.1:
                return resolution

        return Resolution.OTHER

    def _needs_refresh(self) -> bool:
        if self.size_b != self.get_current_size():
            return True
        log.debug(f"Skipping refresh on '{self.full_path}'")
        return False

    def get_current_size(self) -> int:
        return os.stat(self.full_path).st_size

    def refresh(self) -> None:
        """
        Reads the metadata for the given filename and path from the filesystem and saves it to this instance
        """
        if self._needs_refresh():
            log.debug(f"Refreshing data for video: {self.full_path}")
            self.size_b = self.get_current_size()
            metadata = MediaInfo.parse(self.full_path)
            self.audio_tracks = metadata.audio_tracks  # type: ignore
            self.text_tracks = metadata.text_tracks  # type: ignore
            try:
                self.video_track = metadata.video_tracks[0]  # type: ignore
            except IndexError:
                raise RuntimeError

            self.quality = Validator().quality_similar_to(self.video_track)
            self.codec = Codec(format_name=self.video_track.format)
            self.duration = (
                float(self.video_track.duration) if self.video_track.duration else None
            )
            self.resolution = (
                self._determine_resolution(int(self.video_track.width))
                if self.video_track.width
                else Resolution.OTHER
            )
            self.schema_version = self.SCHEMA_VERSION
            if self.quality == "Unknown":
                error_message = f"Failed to parse track metadata from {self.full_path}"
                log.error(error_message)
                raise RuntimeError(error_message)
