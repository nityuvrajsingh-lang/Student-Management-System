"""
file_handler.py - Low-level, safe file input/output.

This module knows HOW to read and write files (JSON), but it knows nothing
about students. The data_storage module builds on top of it.
"""

import json
import os
from datetime import datetime
from pathlib import Path


class DataFileError(Exception):
    """Raised when a data file cannot be read or written."""


class CorruptDataError(DataFileError):
    """Raised when a file exists but its content is not valid or not usable."""


def ensure_directory(path):
    """Create a folder (and any missing parents) if it does not exist yet."""
    Path(path).mkdir(parents=True, exist_ok=True)


def read_json(path, default=None):
    """
    Read a JSON file and return its content.

    Returns `default` when the file does not exist or is empty.
    Raises CorruptDataError for invalid JSON, DataFileError for OS problems.
    """
    path = Path(path)
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as file:
            text = file.read()
    except OSError as error:
        raise DataFileError(f"Could not read '{path}': {error}") from error

    if not text.strip():
        return default
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise CorruptDataError(f"'{path.name}' is not valid JSON ({error}).") from error


def write_json(path, data):
    """
    Write `data` to a JSON file safely.

    The data is first written to a temporary file and then swapped in with
    os.replace(). If the program crashes half-way, the original file is still
    intact instead of being left half-written.
    """
    path = Path(path)
    temp_path = path.with_name(path.name + ".tmp")
    try:
        ensure_directory(path.parent)
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        os.replace(temp_path, path)
    except (OSError, TypeError) as error:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
        raise DataFileError(f"Could not save '{path}': {error}") from error


def backup_corrupt_file(path):
    """Rename a damaged file to '<name>.corrupt-<timestamp>' and return the new path."""
    path = Path(path)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_name(f"{path.name}.corrupt-{stamp}")
    try:
        os.replace(path, backup_path)
    except OSError as error:
        raise DataFileError(f"Could not back up damaged file '{path}': {error}") from error
    return backup_path
