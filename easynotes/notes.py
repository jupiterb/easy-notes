from __future__ import annotations

import json
from pydantic import BaseModel, Field
from typing import Iterable, Iterator, Mapping


class Article(BaseModel):
    name: str
    text: str


class Note(BaseModel):
    label: str
    title: str
    articles: list[Article] = Field(default_factory=list)
    parent_label: str | None = None
    children: list[Note] = Field(default_factory=list)


class NotesRepository(Mapping[str, Note]):
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
        self.load()

    def load(self) -> None:
        try:
            with open(self._file_path, "r") as file:
                notes_data_json = json.load(file)
                self._root = Note(**notes_data_json)
        except FileNotFoundError:
            self._build_empty_root()

        self._build_map()

    def save(self) -> None:
        with open(self._file_path, "w") as file:
            json.dump(self._root, file, default=lambda obj: obj.__dict__)

    def _build_empty_root(self) -> None:
        self._root = Note(label="ROOT", title="Root of all notes")

    def _build_map(self) -> None:
        self._notes_map: dict[str, Note] = {}
        queue: list[Iterable[Note]] = [self.root.children]

        while any(queue):
            notes = queue.pop()

            for note in notes:
                if any(note.children):
                    queue.append(note.children)

                self._notes_map[note.label] = note

        self._notes_map[self.root.label] = self.root

    @property
    def root(self) -> Note:
        return self._root

    def __len__(self) -> int:
        return len(self._notes_map)

    def __iter__(self) -> Iterator[str]:
        return self._notes_map.__iter__()

    def __getitem__(self, label) -> Note:
        return self._notes_map[label]
