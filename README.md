# Video Utils

[![Supported Python Versions](https://img.shields.io/pypi/pyversions/video_utils)](https://pypi.org/project/video_utils/) [![PyPI version](https://badge.fury.io/py/video_utils.svg)](https://badge.fury.io/py/video_utils)

[![Workflow](https://github.com/justin8/video_utils/actions/workflows/workflow.yml/badge.svg)](https://github.com/justin8/video_utils/actions/workflows/workflow.yml)
[![codecov](https://codecov.io/gh/justin8/video_utils/branch/master/graph/badge.svg)](https://codecov.io/gh/justin8/video_utils)
[![Downloads](https://pepy.tech/badge/video_utils/month)](https://pepy.tech/project/video_utils)

This library provides utilities for dealing with TV show and Movie files and the metadata around them.

## Example Usage

```python
from video_utils import FileMap

f = FileMap("/path/to/videos")
f.load() # By default, this will load the cached metadata, and then update files that have changed in size

for directory in f.contents:
    for video in f.contents[directory]:
        codec = video.codec
        print(codec.pretty_name) # x265
        print(video.quality) # 1080p
        print(video.full_path)
        print(video.size) # in bytes
        print(video)
        video.refresh() # force a refresh of the video metadata, will only occur if filesize has changed.
```
