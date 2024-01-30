from notes import NotesRepository
from ui import NotesUI


def main():
    file_path = "./notes.json"
    repo = NotesRepository(file_path)
    ui = NotesUI(repo)

    ui.articles()
    ui.goto()
    ui.new()


if __name__ == "__main__":
    main()
