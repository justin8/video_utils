VALID_EXTENSIONS = ("avi", "divx", "mkv", "mp4", "mpg",
                    "mpeg", "mov", "m4v", "flv", "ts", "wmv")

# This can't be an enum because you can't have numbers at the start of the enums
VALID_QUALITIES = ("1080p", "720p", "SD", "Unknown")


class Validator:

    def is_video(self, file_path):
        return file_path.lower().endswith(VALID_EXTENSIONS)

    def quality_similar_to(self, track):
        # TODO: Refactor this; it's not a validator
        if self._similar_to(track.width, 1920):
            return "1080p"
        if self._similar_to(track.height, 1080):
            return "1080p"
        if self._similar_to(track.width, 1280):
            return "720p"
        if self._similar_to(track.height, 720):
            return "720p"
        if track.width < 1000:
            return "SD"
        return "Unknown"

    def quality(self, quality):
        if quality not in VALID_QUALITIES:
            raise AttributeError(f"Invalid quality: {quality}")

    def _similar_to(self, value, target):
        value = float(value)
        target = float(target)
        return target * 0.9 <= value <= target * 1.1


class Filter:
    def only_videos(self, file_list):
        validator = Validator()
        videos = []
        for filename in file_list:
            if validator.is_video(filename):
                videos.append(filename)
        videos.sort()
        return videos
