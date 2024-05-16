from __future__ import annotations

import json
import uuid

from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Iterator


_new_id = lambda: uuid.uuid4().__str__()


class Article(BaseModel):
    name: str
    text: str


class NoteData(BaseModel):
    title: str
    articles: list[Article] = Field(default_factory=list)


class NoteNode(BaseModel):
    data: NoteData
    edges: list[str] = Field(default_factory=list)


class Tree(BaseModel):
    root: str
    notes: dict[str, NoteNode] = Field(default_factory=dict)

    @staticmethod
    def init() -> Tree:
        root_id = _new_id()
        root_data = NoteData(title="Start")
        root_node = NoteNode(data=root_data)
        return Tree(root=root_id, notes={root_id: root_node})


@dataclass
class Note:
    id: str
    data: NoteData


class NotesRepository:
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
        self.load()

    @property
    def root(self) -> Note:
        return self[self._tree.root]

    def destinations(self, source_id: str) -> list[Note]:
        return [self[id] for id in self._tree.notes[source_id].edges]

    def source(self, id: str) -> Note | None:
        search = [note for note in self if id in self._tree.notes[note.id].edges]
        return search[0] if any(search) else None

    def get(self, id: str) -> Note:
        return Note(id, self._tree.notes[id].data)

    def add(self, data: NoteData, source_id: str) -> Note:
        id = _new_id()
        self._tree.notes[id] = NoteNode(data=data)
        self._tree.notes[source_id].edges.append(id)
        return self[id]

    def remove(self, id: str) -> None:
        for note in self.destinations(id):
            self.remove(note.id)

        source = self.source(id)

        if source is not None:
            self._tree.notes[source.id].edges.remove(id)

        del self._tree.notes[id]

    def load(self) -> None:
        try:
            with open(self._file_path, "r") as file:
                notes_data_json = json.load(file)
                self._tree = Tree(**notes_data_json)
        except FileNotFoundError:
            self._tree = Tree.init()
            self.save()

    def save(self) -> None:
        with open(self._file_path, "w") as file:
            json.dump(self._tree, file, default=lambda obj: obj.__dict__)

    def __len__(self) -> int:
        return len(self._tree.notes)

    def __iter__(self) -> Iterator[Note]:
        return [self[id] for id in self._tree.notes].__iter__()

    def __getitem__(self, id: str) -> Note:
        return self.get(id)
