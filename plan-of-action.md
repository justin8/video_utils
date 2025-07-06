# Plan of Action: Individual File Path Caching

## Current State Analysis

- FileMap currently uses pickle to cache entire directory trees as single objects
- Cache key is MD5 hash of the base directory path
- All subdirectories are cached together, preventing partial loading/caching
- Storage location: `~/.cache/video_utils/{md5_hash}`

## Recommended Solution: SQLite Database

**Choice Rationale:**

- SQLite provides structured storage with indexing for fast lookups
- Supports atomic transactions and concurrent access
- Built into Python standard library (no new dependencies)
- Allows querying subsets of data efficiently
- Better data integrity than multiple pickle files
- Easier to debug and inspect cache contents

## Implementation Plan

### 1. Create New SQLite Storage Backend

- Replace `_FileMapStorage` class with `_FileMapStorageV2`
- Database schema:

  ```sql
  CREATE TABLE video_cache (
      file_path TEXT PRIMARY KEY,
      directory TEXT,
      last_modified REAL,
      video_data BLOB,  -- pickled Video object
      created_at REAL,
      updated_at REAL
  );
  CREATE INDEX idx_directory ON video_cache(directory);
  ```

### 2. Update FileMap Class

- Modify `load()` method to query SQLite by directory patterns
- Update `_update_video()` to use individual file caching
- Enhance `_prune_missing_files()` to work with SQLite queries
- Add support for loading subdirectories independently

### 3. Migration Strategy

- Not needed, assume use on a new system only

### 4. Key Benefits

- **Granular caching**: Cache individual files, not entire directory trees
- **Partial loading**: Load only specific subdirectories when needed
- **Better performance**: Index-based lookups instead of loading entire cache
- **Concurrent access**: SQLite handles multiple processes safely
- **Data integrity**: ACID transactions prevent corruption
- **Debugging**: SQL queries to inspect cache state

### 5. Implementation Steps

1. Create `_FileMapStorageV2` class with database schema
2. Update FileMap to use new storage backend
3. Add comprehensive tests for new functionality
4. Update documentation and version bump

### 6. Backward Compatibility

- No changes to public FileMap API

## Files to Modify

- `video_utils/fileMap.py` - Main implementation
- `tests/test_filemap.py` - Update existing tests
- `tests/test_filemap_storage.py` - New SQLite storage tests

## Testing Strategy

- Unit tests for SQLite storage operations
- Edge case testing (corrupted cache, concurrent access)

This approach provides the most robust and scalable solution while improving performance.
