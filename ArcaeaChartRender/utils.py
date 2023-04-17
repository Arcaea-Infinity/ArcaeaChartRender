__all__ = ['read_file', 'fetch_song_info', 'len_iter', 'ms_to_sexagesimal']

import json
from collections import deque
from itertools import count
from typing import Iterable

from .model import Song


def read_file(file_path: str) -> list[str]:
    """Return the lines of a file as list[str]."""
    with open(file_path, 'r') as f:
        return f.readlines()


def fetch_song_info(songlist_path: str, song_id: str) -> Song:
    """Return specific song info from songlist file."""
    with open(songlist_path, 'r', encoding='utf-8') as f:
        song_list = json.load(f)
    for song in song_list['songs']:
        if song['id'] == song_id:
            return Song(**song)


def len_iter(iterable: Iterable) -> int:
    """Consume an iterable not reading it into memory, and return the length."""
    counter = count()
    deque(zip(iterable, counter), maxlen=0)
    return next(counter)


def ms_to_sexagesimal(t: int) -> str:
    """Convert milliseconds to sexagesimal notation."""
    return f'{t // 60000}:{(t % 60000) // 1000:02d}.{(t % 1000) // 100:0d}'  # 0:00.0
