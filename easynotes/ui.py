import streamlit as st

from notes import NotesRepository, Note, Article


class NotesUI:
    def __init__(self, repo: NotesRepository) -> None:
        self._repo = repo
        self.init_session()

    def init_session(self) -> None:
        st.title("Easy Notes")

        if "note_id" not in st.session_state:
            st.session_state["note_id"] = self._repo.root

        self._note_id = st.session_state.note_id
        self._note = self._repo[self._note_id]

        st.header(self._note.title)

    def rerun(self, note_id: str) -> None:
        st.session_state.note_id = note_id
        self._repo.save()
        st.rerun()

    def display_articles(self) -> None:
        line_h = 23
        max_h = 460

        for i, article in enumerate(self._note.articles):
            st.subheader(article.name)
            st.markdown(article.text)

            with st.expander(f'Edit "{article.name}"'):
                h = min(len(article.text.splitlines()) * line_h, max_h)
                text = st.text_area(article.name, value=article.text, height=h)

                if st.button(f'Update "{article.name}"'):
                    self._note.articles[i] = Article(name=article.name, text=text)
                    self.rerun(self._note_id)

    def change_note(self) -> None:
        st.divider()
        st.header("Go to")

        if self._note.parent_id is not None:
            parent = self._repo[self._note.parent_id]

            if st.button(parent.title):
                self.rerun(self._note.parent_id)

        for child_id, child in self._repo.children(self._note_id).items():
            if st.button(child.title):
                self.rerun(child_id)

    def add_new(self) -> None:
        st.divider()
        st.header("New")

        with st.expander("**New article**"):
            name = st.text_input("New article name", value="")
            text = st.text_area("New article text", value="")

            if st.button("Add article"):
                new_article = Article(name=name, text=text)
                self._note.articles.append(new_article)
                st.success("Article added successfully!")
                self.rerun(self._note_id)

        with st.expander("**New note**"):
            title = st.text_input("Title")
            new_note_id = "".join(title.split())

            if st.button("Add note"):
                new_note = Note(title=title, parent_id=self._note_id)
                self._repo[new_note_id] = new_note
                st.success("Note added successfully!")
                self.rerun(new_note_id)
