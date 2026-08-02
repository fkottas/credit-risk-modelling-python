# Manuscript

The expanded review manuscript is in `book/full_manuscript/`: front matter, 72 analytical chapters, appendices, 72-case practice book, technical workshops, numerical examples, policy playbook, viva questions, glossary and references. The earlier 18-chapter manuscript and numbered foundation drafts remain as development history.

`tools/build_book_docx.py` produces the review Word document using the `compact_reference_guide` design preset and `editorial_cover` pattern.

```bash
$CODEX_PRIMARY_RUNTIME_PYTHON tools/build_book_docx.py
```

Generated review files live under the ignored `artifacts/` directory. The validated analytical review build is 400+ pages, including 72 mathematics-to-code laboratories and native Word equations. The editable source, builder, tests, manuscript validator and notebook validator remain in Git.
