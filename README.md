# 📚 Vocabulator

**Vocabulator** is an application that allows users to upload PDF documents and extract words and frequency data. It supports multiple languages and includes options to remove stopwords and perform spell checking for cleaner, more relevant results.

---

## 🌍 Supported Languages

Vocabulator supports over 20 languages through **spaCy** for natural language processing. Spell checking is available for a subset of these languages using the **PySpellChecker** library.

> ℹ️ Not all languages support spell checking. If unavailable, the app will skip that step.


| Language                     | Support | Spell Checker |
| :--------------------------- | :------ | :------------ |
| Catalan (Català)             | ✅      | ❌            |
| Chinese (简体中文)           | ✅      | ❌            |
| Croatian (Hrvatski)          | ✅      | ❌            |
| Danish (Dansk)               | ✅      | ❌            |
| Dutch (Nederlands)           | ✅      | ✅            |
| English                      | ✅      | ✅            |
| Finnish (Suomi)              | ✅      | ❌            |
| French (Français)            | ✅      | ✅            |
| German (Deutsch)             | ✅      | ✅            |
| Greek (Ελληνικά)             | ✅      | ❌            |
| Italian (Italiano)           | ✅      | ✅            |
| Japanese (日本語)            | ✅      | ❌            |
| Korean (한국어)              | ✅      | ❌            |
| Lithuanian (Lietuvių)        | ✅      | ❌            |
| Macedonian (Македонски)      | ✅      | ❌            |
| Norwegian Bokmål (Norsk Bokmål) | ✅   | ❌            |
| Polish (Polski)              | ✅      | ❌            |
| Portuguese (Português)       | ✅      | ✅            |
| Romanian (Română)            | ✅      | ❌            |
| Russian (Русский)            | ✅      | ✅            |
| Slovenian (Slovenščina)      | ✅      | ❌            |
| Spanish (Español)            | ✅      | ✅            |
| Swedish (Svenska)            | ✅      | ❌            |
| Ukrainian (Українська)       | ✅      | ❌            |

---

## 🛠 Technologies Used

- [Streamlit](https://streamlit.io) – Web app framework
- [spaCy](https://spacy.io) – NLP for tokenization and lemmatization
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) – PDF text extraction
- [pyspellchecker](https://github.com/barrust/pyspellchecker) – Spell checking
- [Pandas](https://pandas.pydata.org/) – Data processing
- [XlsxWriter](https://xlsxwriter.readthedocs.io/) – Excel export

---