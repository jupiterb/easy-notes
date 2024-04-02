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


class Tree(BaseModel):
    root: str
    notes: dict[str, NoteData] = Field(default_factory=dict)
    edges: dict[str, list[str]] = Field(default_factory=dict)


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
        return [self[id] for id in self._tree.edges[source_id]]

    def source(self, id: str) -> Note | None:
        search = [note for note in self if id in self._tree.edges[note.id]]
        return search[0] if any(search) else None

    def get(self, id: str) -> Note:
        return Note(id, self._tree.notes[id])

    def add(self, data: NoteData, source_id: str) -> Note:
        id = _new_id()

        self._tree.notes[id] = data
        self._tree.edges[id] = []
        self._tree.edges[source_id].append(id)

        return self[id]

    def remove(self, id: str) -> None:
        for note in self.destinations(id):
            self.remove(note.id)

        source = self.source(id=id)

        if source is not None:
            self._tree.edges[source.id].remove(id)

        del self._tree.notes[id]
        del self._tree.edges[id]

    def load(self) -> None:
        try:
            with open(self._file_path, "r") as file:
                notes_data_json = json.load(file)
                self._tree = Tree(**notes_data_json)
        except FileNotFoundError:
            self._init_tree()
            self.save()

    def save(self) -> None:
        with open(self._file_path, "w") as file:
            json.dump(self._tree, file, default=lambda obj: obj.__dict__)

    def _init_tree(self) -> None:
        root_id = _new_id()
        root_data = NoteData(title="Start")
        self._tree = Tree(root=root_id, notes={root_id: root_data}, edges={root_id: []})

    def __len__(self) -> int:
        return len(self._tree.notes)

    def __iter__(self) -> Iterator[Note]:
        return [self[id] for id in self._tree.notes].__iter__()

    def __getitem__(self, id: str) -> Note:
        return self.get(id)
