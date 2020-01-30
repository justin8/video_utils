import logging
import os
from os import path

from pymediainfo import MediaInfo

from .validators import Validator
from .codec import Codec

log = logging.getLogger(__name__)


class Video:
    def __init__(self, name, dir_path, codec=None, quality=None, size=None):
        self.name = name
        self.dir_path = dir_path
        self.codec = codec
        self.quality = quality
        self.size = size

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
    def dir_path(self):
        return self._dir_path

    @dir_path.setter
    def dir_path(self, value):
        self._dir_path = path.realpath(value)

    @property
    def full_path(self):
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
        log.info(f"Skipping refresh on '{self.full_path}'")
        return False

    def _get_size(self):
        return os.stat(self.full_path).st_size

    def refresh(self):
        """
        Reads the metadata for the given filename and path from the filesystem and saves it to this instance
        """
        if self._needs_refresh():
            log.info(f"Refreshing data for video: {self.full_path}")
            self.size = self._get_size()
            metadata = MediaInfo.parse(self.full_path)
            for track in metadata.tracks:
                if track.track_type == "Video":
                    self.quality = Validator().quality_similar_to(track)
                    self.codec = Codec(format_name=track.format, )
                    break
            if self.quality == "Unknown":
                error_message = f"Failed to parse track metadata from {self.full_path}"
                log.error(error_message)
                raise RuntimeError(error_message)
