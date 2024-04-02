from notes import NotesRepository
from ui import NotesUI


def main():
    file_path = "./resources/notes.json"
    repo = NotesRepository(file_path)
    ui = NotesUI(repo)

    ui.display_note_content()
    ui.display_sidebar_mamager()


if __name__ == "__main__":
    main()
