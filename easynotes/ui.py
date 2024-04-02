import streamlit as st

from notes import NotesRepository, Note, NoteData, Article


class NotesUI:
    def __init__(self, repo: NotesRepository) -> None:
        self._repo = repo
        self.init_session()

    def init_session(self) -> None:
        if "id" not in st.session_state:
            st.session_state["id"] = self._repo.root.id

        id = st.session_state.id
        self._note: Note = self._repo[id]
        self._source: Note | None = self._repo.source(id)

    def reload(self, id: str) -> None:
        self._repo.save()
        st.session_state.id = id
        st.rerun()

    def display_note_content(self) -> None:
        st.title("Easy Notes")
        st.divider()
        st.header(self._note.data.title)

        for article in self._note.data.articles:
            st.subheader(article.name)
            st.markdown(article.text)

    def display_sidebar_mamager(self) -> None:
        with st.sidebar:
            self._edit_articles()
            self._add_new()
            self._link_related_notes()
            self._manage_note()

    def _edit_articles(self) -> None:
        if not any(self._note.data.articles):
            return

        st.header("Articles")

        line_h = 23
        max_h = 460

        for i, article in enumerate(self._note.data.articles):
            with st.expander(f'Edit "{article.name}"'):
                name = st.text_input(f'Rename "{article.name}', value=article.name)

                h = min(len(article.text.splitlines()) * line_h, max_h)
                text = st.text_area(
                    f'Edit "{article.name}"', value=article.text, height=h
                )

                if st.button(f'Update "{article.name}"'):
                    self._note.data.articles[i] = Article(name=name, text=text)
                    self.reload(self._note.id)

                if st.button(f'Delete "{article.name}"'):
                    self._note.data.articles.pop(i)
                    self.reload(self._note.id)

    def _link_related_notes(self) -> None:
        links = self._repo.destinations(self._note.id)

        if self._source is not None:
            links.append(self._repo[self._source.id])

        if any(links):
            st.header("Go to")

        for note in links:
            if st.button(note.data.title):
                self.reload(note.id)

    def _add_new(self) -> None:
        st.header("New")

        with st.expander("New article"):
            name = st.text_input("New article name", value="")
            text = st.text_area("New article text", value="")

            if st.button("Add article"):
                new_article = Article(name=name, text=text)
                self._note.data.articles.append(new_article)
                st.success("Article added successfully!")
                self.reload(self._note.id)

        with st.expander("New note"):
            title = st.text_input("Title")

            if st.button("Add note"):
                data = NoteData(title=title)
                id = self._repo.add(data, self._note.id).id
                st.success("Note added successfully!")
                self.reload(id)

    def _manage_note(self) -> None:
        st.header("Manage")

        with st.expander("Rename"):
            title = st.text_input("Title", value=self._note.data.title)
            self._note.data.title = title

            if st.button("Update"):
                self.reload(self._note.id)

        if self._source is None:
            return

        with st.expander("Delete"):
            st.text(
                f'Removing note "{self._note.data.title}" will cause removing all notes falling under this note'
            )

            if st.button(f'Delete "{self._note.data.title}"'):
                self._repo.remove(self._note.id)
                self.reload(self._source.id)
