import logging
import os
import pickle
import sqlite3
import time
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
        progress_bar: bool = True,
    ):
        """
        update value is only honoured on object initialization
        """
        self.directory: str = directory
        self._update: bool = update
        self._progress_bar: bool = progress_bar
        self.contents: Dict[str, List[Video]] = {}

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
        self._update = value

    def load(self) -> None:
        storage = _FileMapStorage(self.directory)
        self.contents = storage.load()
        self._prune_missing_files()
        if self.update:
            self._update_content()

    def _update_content(self) -> None:
        """
        Update the contents of this filemap
        """
        log.debug("Updating contents...")
        filter = Filter()
        for dir_path, dir_names, file_names in self._file_tree():
            log.info(colour("green", "Working in directory: %s" % dir_path))

            video_files = filter.only_videos(file_names)
            log.debug("Total videos in %s: %s" % (dir_path, len(video_files)))

            if self._progress_bar:
                video_files = track(video_files, f"Processing {dir_path}...")

            for video_file in video_files:
                self._update_video(dir_path, video_file)

            # Save videos for this directory after processing
            if dir_path in self.contents:
                storage = _FileMapStorage(self.directory)
                storage.save_videos(self.contents[dir_path])

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
        missing_files = set()

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
                    missing_files.add(video.full_path)

        # Update database to remove missing files
        if missing_files:
            storage = _FileMapStorage(self.directory)
            storage.remove_existing_files(missing_files)


class _FileMapStorage:
    def __init__(self, directory: str) -> None:
        self.directory = directory
        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database with required schema"""
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS video_cache (
                    file_path TEXT PRIMARY KEY,
                    directory TEXT NOT NULL,
                    last_modified REAL NOT NULL,
                    video_data BLOB NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_directory ON video_cache(directory)"
            )
            conn.commit()

    def load(self) -> Dict[str, List[Video]]:
        data = {}
        log.debug("Loading from cache...")
        try:
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute(
                    "SELECT directory, video_data FROM video_cache WHERE file_path LIKE ?",
                    (f"{self.directory}%",),
                )

                for directory, video_data_blob in cursor:
                    if directory not in data:
                        data[directory] = []
                    video = pickle.loads(video_data_blob)
                    data[directory].append(video)

        except (sqlite3.Error, pickle.PickleError) as e:
            log.error(f"Failed to load cache from database: {e}. Ignoring cache...")

        return data

    def save_videos(self, videos: List[Video]) -> None:
        log.debug("Saving videos to cache...")
        current_time = time.time()

        try:
            with sqlite3.connect(self.storage_path) as conn:
                for video in videos:
                    file_path = video.full_path
                    directory = video.dir_path
                    last_modified = (
                        video.get_current_size() if path.exists(file_path) else 0
                    )
                    video_data = pickle.dumps(video)

                    conn.execute(
                        """
                        INSERT OR REPLACE INTO video_cache 
                        (file_path, directory, last_modified, video_data, created_at, updated_at)
                        VALUES (?, ?, ?, ?, 
                            COALESCE((SELECT created_at FROM video_cache WHERE file_path = ?), ?),
                            ?)
                    """,
                        (
                            file_path,
                            directory,
                            last_modified,
                            video_data,
                            file_path,
                            current_time,
                            current_time,
                        ),
                    )

                conn.commit()

        except (sqlite3.Error, pickle.PickleError) as e:
            log.error(f"Failed to save videos to database: {e}")

    def remove_existing_files(self, files_to_remove: set) -> None:
        """Remove specified files from cache"""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                if files_to_remove:
                    placeholders = ",".join("?" * len(files_to_remove))
                    conn.execute(
                        f"DELETE FROM video_cache WHERE file_path IN ({placeholders})",
                        list(files_to_remove),
                    )
                conn.commit()

        except sqlite3.Error as e:
            log.error(f"Failed to remove files from cache: {e}")

    @property
    def storage_path(self) -> str:
        storage_path = path.join(path.expanduser("~"), ".cache", "video_utils")
        os.makedirs(storage_path, exist_ok=True)
        return path.join(storage_path, "cache.db")
