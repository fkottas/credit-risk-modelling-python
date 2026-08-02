# Manuscript

The complete first-edition review manuscript is in `book/manuscript/`: front matter, eighteen large applied chapters, appendices and references. The earlier numbered foundation drafts remain in `book/chapters/` as development history.

`tools/build_book_docx.py` produces the review Word document using the `compact_reference_guide` design preset and `editorial_cover` pattern.

```bash
$CODEX_PRIMARY_RUNTIME_PYTHON tools/build_book_docx.py
```

Generated review files live under the ignored `artifacts/` directory. The editable source, builder, tests and notebook validator remain in Git.
