import json
from pydantic import BaseModel, Field
from typing import Iterator


class Article(BaseModel):
    name: str
    text: str


class Note(BaseModel):
    title: str
    articles: list[Article] = Field(default_factory=list)
    parent_id: str | None = None


class Notes(BaseModel):
    mapping: dict[str, Note]


class NotesRepository:
    def __init__(self, file_path: str) -> None:
        self._file_path = file_path
        self.load()

    @property
    def root(self) -> str:
        return [id for id in self if self[id].parent_id is None][0]

    def children(self, parent_id: str) -> dict[str, Note]:
        return {id: self[id] for id in self if self[id].parent_id == parent_id}

    def load(self) -> None:
        try:
            with open(self._file_path, "r") as file:
                notes_data_json = json.load(file)
                self._notes = Notes(**notes_data_json)
        except FileNotFoundError:
            self._build_empty_map()

    def save(self) -> None:
        with open(self._file_path, "w") as file:
            json.dump(self._notes, file, default=lambda obj: obj.__dict__)

    def _build_empty_map(self) -> None:
        mapping = {"ROOT": Note(title="Root of all notes")}
        self._notes = Notes(mapping=mapping)

    def __len__(self) -> int:
        return len(self._notes.mapping)

    def __iter__(self) -> Iterator[str]:
        return self._notes.mapping.__iter__()

    def __getitem__(self, id: str) -> Note:
        return self._notes.mapping[id]

    def __setitem__(self, id: str, note: Note) -> None:
        self._notes.mapping[id] = note
