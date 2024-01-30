import streamlit as st

from notes import NotesRepository, Note, Article


class NotesUI:
    def __init__(self, repo: NotesRepository) -> None:
        self._repo = repo
        self.init_session(repo.root)
        self._note = repo[st.session_state.label]

    def init_session(self, note: Note) -> None:
        st.title("Easy Notes")

        if "label" not in st.session_state:
            st.session_state["label"] = note.label

    def rerun(self) -> None:
        self._repo.save()
        st.rerun()

    def articles(self) -> None:
        st.header(self._note.title)

        updated_articles = []
        line_h = 23
        max_h = 460

        for article in self._note.articles:
            h = min(len(article.text.splitlines()) * line_h, max_h)
            text = st.text_area(article.name, value=article.text, height=h)
            new_article = Article(name=article.name, text=text)
            updated_articles.append(new_article)

        self._note.articles = updated_articles

        if st.button("Update articles"):
            self.rerun()

        st.divider()

        name = st.text_input("New article name", value="")
        text = st.text_area("New article text", value="")

        if st.button("Add article"):
            new_article = Article(name=name, text=text)
            self._note.articles.append(new_article)
            st.success("Article added successfully!")
            self.rerun()

    def goto(self) -> None:
        st.divider()
        st.header("Go to")

        if self._note.parent_label is not None:
            parent = self._repo[self._note.parent_label]

            if st.button(f"[{parent.label}] {parent.title} (Parent of this note)"):
                st.session_state.label = self._note.parent_label
                self.rerun()

        for child in self._note.children:
            if st.button(f"[{child.label}] {child.title}"):
                st.session_state.label = child.label
                self.rerun()

    def new(self) -> None:
        st.divider()
        st.header("New note")

        label = st.text_input("Label (unique value)")
        title = st.text_input("Title")

        if st.button("Add note"):
            new_note = Note(label=label, title=title, parent_label=self._note.label)
            self._note.children.append(new_note)
            st.success("Note added successfully!")
            self.rerun()
