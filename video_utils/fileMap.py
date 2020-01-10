#!/usr/bin/env python3

from copy import deepcopy
import logging
import os
from os import path
import hashlib
import pickle
from tqdm import tqdm

from .cprint import cprint
from .validators import Filter
from .video import Video

log = logging.getLogger(__name__)


class FileMap:
    def __init__(self, directory, update=True, use_cache=True):
        """
        update and use_cache values are only honoured on object initialization
        """
        self.directory = directory
        self._update = update
        self._use_cache = use_cache
        self.contents = {}
        self._validate_settings(update=self.update, use_cache=self.use_cache)

    @property
    def directory(self):
        return self._directory

    @directory.setter
    def directory(self, value):
        self._directory = path.realpath(value)

    @property
    def update(self):
        return self._update

    @update.setter
    def update(self, value):
        self._validate_settings(update=value, use_cache=self.use_cache)
        self._update = value

    @property
    def use_cache(self):
        return self._use_cache

    @use_cache.setter
    def use_cache(self, value):
        self._validate_settings(update=self.update, use_cache=value)
        self._use_cache = value

    def _validate_settings(self, update, use_cache):
        if not update and not use_cache:
            raise AttributeError(
                "At least one of update or use_cache must be True")

    def load(self):
        storage = _FileMapStorage(self.directory)
        self.contents = storage.load(self.use_cache)
        if self.update:
            self._update_content()
        storage.save(self.contents)

    def _update_content(self):
        """
        Update the contents of this filemap
        """
        log.info("Updating contents...")
        filter = Filter()
        if self.use_cache:
            self._prune_missing_files()
        for dir_path, dir_names, file_names in self._file_tree():
            cprint("green", "Working in directory: %s" % dir_path)

            video_files = filter.only_videos(file_names)
            log.info("Total videos in %s: %s" % (dir_path, len(video_files)))

            if log.level > logging.INFO:
                video_files = tqdm(video_files)

            for video_file in video_files:
                self._update_video(dir_path, video_file)

    def _update_video(self, dir_path, video_name):
        if dir_path not in self.contents:
            self.contents[dir_path] = []

        video = Video(name=video_name, dir_path=dir_path)
        if video in self.contents[dir_path]:
            log.info(
                f"Video ({video.full_path} already in cache. Checking for updates and replacing...)")
            video = next(i for i in self.contents[dir_path] if i == video)
            self.contents[dir_path].remove(video)
        video.refresh()
        self.contents[dir_path].append(video)

    def _video_needs_refreshing(self, video):
        pass

    def _file_tree(self):
        if path.isfile(self.directory):
            log.info("Provided directory is a file, not a directory")
            file_tree = [(path.dirname(self.directory), [],
                          [path.basename(self.directory)])]
        else:
            file_tree = os.walk(self.directory, followlinks=True)
        return file_tree

    def _prune_missing_files(self):
        cprint("blue", "Checking for missing/deleted files...")
        # Can't mutate the original while we iterate through it
        contents_copy = deepcopy(self.contents)
        if log.level > logging.INFO:
            contents_copy = tqdm(contents_copy)
        for dir_path in contents_copy:
            if not path.exists(dir_path):
                log.info("Removing %s from cache" % dir_path)
                del self.contents[dir_path]
                continue

            for video in contents_copy[dir_path]:
                if not path.exists(video.full_path):
                    log.info("Removing %s from cache" % video.full_path)
                    self.contents[dir_path].remove(video)


class _FileMapStorage:
    def __init__(self, directory):
        self.directory = directory

    def load(self, use_cache=True):
        data = {}
        if use_cache:
            if path.exists(self.storage_path):
                log.info("Loading from cache...")
                try:
                    with open(self.storage_path, 'rb') as f:
                        data = pickle.load(f)
                except EOFError:
                    log.error(
                        f"Failed to load cache! Likely a corrupt cache file ({self.storage_path}). Ignoring cache...")
        return data

    def save(self, data):
        log.info("Saving out filemap...")
        with open(self.storage_path, 'wb') as f:
            pickle.dump(data, f)

    @property
    def storage_path(self):
        storage_path = path.join(path.expanduser("~"), ".video_utils")
        os.makedirs(storage_path, exist_ok=True)
        name = hashlib.md5(bytes(self.directory, 'ascii')).hexdigest()
        return path.join(storage_path, name)
