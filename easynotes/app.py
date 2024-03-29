from notes import NotesRepository
from ui import NotesUI


def main():
    file_path = "./resources/notes.json"
    repo = NotesRepository(file_path)
    ui = NotesUI(repo)

    ui.display_articles()
    ui.add_new()
    ui.change_note()


if __name__ == "__main__":
    main()
