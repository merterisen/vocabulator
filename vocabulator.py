import streamlit as st
import fitz  # PyMuPDF
import spacy
import re
from collections import Counter
import pandas as pd
from spellchecker import SpellChecker
import io

st.set_page_config(page_title="Vocabulator", layout="wide")

# Languages supported by pyspellchecker
PYSPELLCHECKER_SUPPORTED_LANGS = ['en', 'es', 'fr', 'pt', 'de', 'it', 'ru', 'nl']

# Supported languages for spaCy and their mapping to pyspellchecker codes
# If a language is not in PYSPELLCHECKER_SUPPORTED_LANGS, its spellchecker code is None.
SUPPORTED_LANGUAGES = {
    "Catalan (Català)": {"spacy": "ca_core_news_sm", "spellchecker": None},
    "Chinese (简体中文)": {"spacy": "zh_core_web_sm", "spellchecker": None},
    "Croatian (Hrvatski)": {"spacy": "hr_core_news_sm", "spellchecker": None},
    "Danish (Dansk)": {"spacy": "da_core_news_sm", "spellchecker": None},
    "Dutch (Nederlands)": {"spacy": "nl_core_news_sm", "spellchecker": "nl" if "nl" in PYSPELLCHECKER_SUPPORTED_LANGS else None},
    "English": {"spacy": "en_core_web_sm", "spellchecker": "en" if "en" in PYSPELLCHECKER_SUPPORTED_LANGS else None},
    "Finnish (Suomi)": {"spacy": "fi_core_news_sm", "spellchecker": None},
    "French (Français)": {"spacy": "fr_core_news_sm", "spellchecker": "fr" if "fr" in PYSPELLCHECKER_SUPPORTED_LANGS else None},
    "German (Deutsch)": {"spacy": "de_core_news_sm", "spellchecker": "de" if "de" in PYSPELLCHECKER_SUPPORTED_LANGS else None},
    "Greek (Ελληνικά)": {"spacy": "el_core_news_sm", "spellchecker": None},
    "Italian (Italiano)": {"spacy": "it_core_news_sm", "spellchecker": "it" if "it" in PYSPELLCHECKER_SUPPORTED_LANGS else None},
    "Japanese (日本語)": {"spacy": "ja_core_news_sm", "spellchecker": None},
    "Korean (한국어)": {"spacy": "ko_core_news_sm", "spellchecker": None},
    "Lithuanian (Lietuvių)": {"spacy": "lt_core_news_sm", "spellchecker": None},
    "Macedonian (Македонски)": {"spacy": "mk_core_news_sm", "spellchecker": None},
    "Norwegian Bokmål (Norsk Bokmål)": {"spacy": "nb_core_news_sm", "spellchecker": None},
    "Polish (Polski)": {"spacy": "pl_core_news_sm", "spellchecker": None},
    "Portuguese (Português)": {"spacy": "pt_core_news_sm", "spellchecker": "pt" if "pt" in PYSPELLCHECKER_SUPPORTED_LANGS else None},
    "Romanian (Română)": {"spacy": "ro_core_news_sm", "spellchecker": None},
    "Russian (Русский)": {"spacy": "ru_core_news_sm", "spellchecker": "ru" if "ru" in PYSPELLCHECKER_SUPPORTED_LANGS else None},
    "Slovenian (Slovenščina)": {"spacy": "sl_core_news_sm", "spellchecker": None},
    "Spanish (Español)": {"spacy": "es_core_news_sm", "spellchecker": "es" if "es" in PYSPELLCHECKER_SUPPORTED_LANGS else None},
    "Swedish (Svenska)": {"spacy": "sv_core_news_sm", "spellchecker": None},
    "Ukrainian (Українська)": {"spacy": "uk_core_news_sm", "spellchecker": None}
}


@st.cache_resource
def load_spacy_model(model_name):
    try:
        return spacy.load(model_name)
    except OSError:
        st.error(
            f"SpaCy model '{model_name}' not found. "
            f"Please download it by running: python -m spacy download {model_name}"
        )
        st.stop()

def extract_book_words(pdf_bytes, language_details, remove_stopwords: bool, enable_spellcheck: bool):
    """
    Reads a PDF, cleans text, extracts words, and returns a DataFrame of word frequencies.
    """
    st.info("Reading PDF file...")
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None

    raw_text = "".join(page.get_text("text") for page in doc)
    doc.close()

    if not raw_text.strip():
        st.warning("No text could be extracted from the PDF, or the file is empty.")
        return None

    st.info("Cleaning and processing text...")

    # Keep word characters (letters, numbers, underscore), whitespace, and hyphens.
    # Most language characters should be covered by \w in Python 3's re with Unicode.
    cleaned_text = re.sub(r"[^\w\s-]", "", raw_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    spacy_model_name = language_details["spacy"]
    nlp = load_spacy_model(spacy_model_name)

    spacy_doc = nlp(cleaned_text)

    # Tokenize, lemmatize, and ensure lemmas are alphabetic and longer than one character.
    lemmas = [
        word.lemma_.lower()
        for word in spacy_doc
        if word.is_alpha and len(word.lemma_) > 1
    ]

    # Optional
    if remove_stopwords: 
        st.info("Removing stopwords...")
        stop_words = nlp.Defaults.stop_words
        lemmas = [lemma for lemma in lemmas if lemma not in stop_words]

    if not lemmas:
        st.warning("No processable words found after initial filtering (and optional stopword removal).")
        return None

    meaningful_lemmas = list(lemmas) # Start with current lemmas

    # Optional
    if enable_spellcheck:
        spellchecker_code = language_details.get("spellchecker")
        if spellchecker_code: # Check if a spellchecker code is defined for the language
            st.info(f"Attempting spell checking for language code: '{spellchecker_code}'...")
            try:
                spell = SpellChecker(language=spellchecker_code)
                dictionary_words = spell.known(meaningful_lemmas)
                
                # Filter out unknown words
                current_lemmas_after_spellcheck = [lemma for lemma in meaningful_lemmas if lemma in dictionary_words]

                if meaningful_lemmas and not current_lemmas_after_spellcheck:
                    st.warning(
                        f"Spell checking for '{spellchecker_code}' filtered out all words. "
                        "This might be due to limited dictionary coverage for this text. "
                        "Proceeding with words before spell check."
                    )
                    # meaningful_lemmas remains as it was before this spell check attempt
                elif not dictionary_words and meaningful_lemmas:
                     st.warning(
                        f"No words from the text were found in the '{spellchecker_code}' dictionary. "
                        "Spell checking may not be effective. Proceeding with words before spell check."
                    )
                else:
                    meaningful_lemmas = current_lemmas_after_spellcheck

            except Exception as e: # Catches errors from SpellChecker
                st.warning(
                    f"Could not apply spell checking for '{spellchecker_code}': {e}. "
                    "This language might not be supported by the spellchecker library, or an error occurred. "
                    "Skipping spell check."
                )
        else:
            st.info("Spell checking is enabled, but the selected language does not have a configured or supported spellchecker. Skipping.")


    if not meaningful_lemmas:
        st.warning("No words remained after all processing steps.")
        return None

    df = pd.DataFrame(
        Counter(meaningful_lemmas).items(),
        columns=['Word', 'Count']
    ).sort_values(by="Count", ascending=False)

    return df

# --- Streamlit UI ---
st.title(" Vocabulator: Word Extractor")
st.markdown("Extract word frequencies from your PDF documents.")

sorted_language_names = sorted(list(SUPPORTED_LANGUAGES.keys()))
default_english_index = sorted_language_names.index("English") if "English" in sorted_language_names else 0

selected_language_name = st.selectbox(
    "Select language for analysis:",
    options=sorted_language_names,
    index=default_english_index
)
language_details = SUPPORTED_LANGUAGES[selected_language_name]

uploaded_file = st.file_uploader("Choose a PDF file to extract", type=["pdf"])

# Stopwords checkbox + info button
remove_stopwords_col, remove_stopwords_info_col = st.columns([20, 1])
with remove_stopwords_col:
    remove_stopwords_option = st.checkbox("Remove stopwords", value=True)
with remove_stopwords_info_col:
    remove_stopwords_info_btn = st.button("❓", key="stopwords_info_btn", help="Click for explanation")

if 'show_stopwords_info' not in st.session_state:
    st.session_state['show_stopwords_info'] = False

if remove_stopwords_info_btn:
    st.session_state['show_stopwords_info'] = not st.session_state['show_stopwords_info']

if st.session_state['show_stopwords_info']:
    st.info(
        "Stopwords are very common words like 'and', 'the', 'is' or their equivalents in other languages. "
        "Removing them helps focus on the more meaningful words in the text."
    )

# Spellcheck checkbox + info button
spellcheck_col, spellcheck_info_col = st.columns([20, 1])
with spellcheck_col:
    enable_spellcheck_option = st.checkbox("Spell checking (filters non-dictionary/meaningless words)", value=True)
with spellcheck_info_col:
    spellcheck_info_btn = st.button("❓", key="spellcheck_info_btn", help="Click for explanation")

if 'show_spellcheck_info' not in st.session_state:
    st.session_state['show_spellcheck_info'] = False

if spellcheck_info_btn:
    st.session_state['show_spellcheck_info'] = not st.session_state['show_spellcheck_info']

if st.session_state['show_spellcheck_info']:
    supported_langs = ", ".join([
        lang for lang, details in SUPPORTED_LANGUAGES.items()
        if details.get("spellchecker") is not None
    ])
    st.info(
        "Spell checking removes words not found in the selected language's dictionary, "
        "helping to correct OCR or typographical errors.\n\n"
        "Supported languages for spell checking:\n" + "\n".join(f"- {lang}" for lang in [
        lang for lang, details in SUPPORTED_LANGUAGES.items()
        if details.get("spellchecker") is not None
])
        
    )


if st.button("Analyze PDF", type="primary"):
    if uploaded_file is not None:
        pdf_bytes = uploaded_file.getvalue()
        with st.spinner("Analyzing words... This may take a moment depending on file size and language."):
            df_results = extract_book_words(
                pdf_bytes,
                language_details,
                remove_stopwords_option,
                enable_spellcheck_option
            )

        if df_results is not None and not df_results.empty:
            st.success("Word analysis complete!")
            st.dataframe(df_results.head(200), height=500, use_container_width=True)

            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
                df_results.to_excel(writer, index=False, sheet_name='WordAnalysis')
            excel_data = output_excel.getvalue()

            output_csv = io.StringIO()
            df_results.to_csv(output_csv, index=False)
            csv_data = output_csv.getvalue()

            # Excel and CSV buttons
            st.download_button(
                label="Download Results as Excel",
                data=excel_data,
                file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_words.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            st.download_button(
                label="Download Results as CSV",
                data=csv_data,
                file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_words.csv",
                mime="text/csv"
                )
            
        elif df_results is not None and df_results.empty:
            st.info("Analysis complete, but no words were found to display after filtering.")
    else:
        st.warning("Please upload a PDF file to extract.")
