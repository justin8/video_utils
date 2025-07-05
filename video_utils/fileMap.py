import hashlib
import logging
import os
import pickle
from copy import deepcopy
from os import path
from typing import Dict, List

from rich.progress import track

from .colour import colour
from .validators import Filter
from .video import Video

log = logging.getLogger(__name__)


class FileMap:
    def __init__(
        self,
        directory: str,
        update: bool = True,
        use_cache: bool = True,
        progress_bar: bool = True,
    ):
        """
        update and use_cache values are only honoured on object initialization
        """
        self.directory: str = directory
        self._update: bool = update
        self._use_cache: bool = use_cache
        self._progress_bar: bool = progress_bar
        self.contents: Dict[str, List[Video]] = {}
        self._validate_settings(update=self._update, use_cache=self._use_cache)

    @property
    def directory(self) -> str:
        return self._directory

    @directory.setter
    def directory(self, value: str) -> None:
        self._directory = path.realpath(value)

    @property
    def update(self) -> bool:
        return self._update

    @update.setter
    def update(self, value: bool) -> None:
        self._validate_settings(update=value, use_cache=self.use_cache)
        self._update = value

    @property
    def use_cache(self) -> bool:
        return self._use_cache

    @use_cache.setter
    def use_cache(self, value: bool) -> None:
        self._validate_settings(update=self.update, use_cache=value)
        self._use_cache = value

    def _validate_settings(self, update: bool, use_cache: bool) -> None:
        if not update and not use_cache:
            raise AttributeError("At least one of update or use_cache must be True")

    def load(self) -> None:
        storage = _FileMapStorage(self.directory)
        self.contents = storage.load(self.use_cache)
        if self.update:
            self._update_content()
        storage.save(self.contents)

    def _update_content(self) -> None:
        """
        Update the contents of this filemap
        """
        log.debug("Updating contents...")
        filter = Filter()
        if self.use_cache:
            self._prune_missing_files()
        for dir_path, dir_names, file_names in self._file_tree():
            log.info(colour("green", "Working in directory: %s" % dir_path))

            video_files = filter.only_videos(file_names)
            log.debug("Total videos in %s: %s" % (dir_path, len(video_files)))

            if self._progress_bar:
                video_files = track(video_files)

            for video_file in video_files:
                self._update_video(dir_path, video_file)

    def _update_video(self, dir_path: str, video_name: str) -> None:
        if dir_path not in self.contents:
            self.contents[dir_path] = []

        video = Video(name=video_name, dir_path=dir_path)
        if video in self.contents[dir_path]:
            log.debug(
                f"Video ({video.full_path} already in cache. Checking for updates and replacing...)"
            )
            video = next(i for i in self.contents[dir_path] if i == video)
            self.contents[dir_path].remove(video)
        video.refresh()
        self.contents[dir_path].append(video)

    def _video_needs_refreshing(self, video: Video) -> None:
        pass

    def _file_tree(self):
        if path.isfile(self.directory):
            log.debug("Provided directory is a file, not a directory")
            file_tree = [
                (path.dirname(self.directory), [], [path.basename(self.directory)])
            ]
        else:
            file_tree = os.walk(self.directory, followlinks=True)
        return file_tree

    def _prune_missing_files(self) -> None:
        log.info(colour("blue", "Checking for missing/deleted files..."))
        # Can't mutate the original while we iterate through it
        contents_copy = deepcopy(self.contents)
        for dir_path in contents_copy:
            log.info(colour("blue", f"Processing directory {dir_path}"))

            if not path.exists(dir_path):
                log.debug("Removing %s from cache" % dir_path)
                del self.contents[dir_path]
                continue

            sub_directory = contents_copy[dir_path]
            if self._progress_bar:
                sub_directory = track(sub_directory)

            for video in sub_directory:
                if not path.exists(video.full_path):
                    log.debug("Removing %s from cache" % video.full_path)
                    self.contents[dir_path].remove(video)


class _FileMapStorage:
    def __init__(self, directory: str) -> None:
        self.directory = directory

    def load(self, use_cache: bool = True) -> Dict[str, List[Video]]:
        data = {}
        if use_cache:
            if path.exists(self.storage_path):
                log.debug("Loading from cache...")
                try:
                    with open(self.storage_path, "rb") as f:
                        data = pickle.load(f)
                except EOFError:
                    log.error(
                        f"Failed to load cache! Likely a corrupt cache file ({self.storage_path}). Ignoring cache..."
                    )
        return data

    def save(self, data: Dict[str, List[Video]]) -> None:
        log.debug("Saving out filemap...")
        with open(self.storage_path, "wb") as f:
            pickle.dump(data, f)

    @property
    def storage_path(self) -> str:
        storage_path = path.join(path.expanduser("~"), ".cache", "video_utils")
        os.makedirs(storage_path, exist_ok=True)
        name = hashlib.md5(bytes(self.directory, "ascii")).hexdigest()
        return path.join(storage_path, name)
