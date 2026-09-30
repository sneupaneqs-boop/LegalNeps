"""V2: the romanised-Nepali -> statute-Nepali lexicon (app/translit.py).

The corpus is Devanagari-only, so every Devanagari target must be a word the
index really contains, and every law title must be a real corpus title."""
import pytest

from app import translit
from app.retrieval import get_index
from app.text_norm import tokenize


@pytest.fixture(scope="module")
def index():
    return get_index()


def test_every_target_term_is_in_the_index_vocabulary(index):
    """The validation that keeps the lexicon honest: after the same
    tokenisation the index uses, each token of each target must be a
    vocabulary word that occurs in at least 2 passages."""
    vocab = index.vocab
    df = None
    bad = []
    for e in translit.ENTRIES:
        for term in e.terms:
            toks = tokenize(term)
            if not toks:
                bad.append((e.keys[0], term, "no tokens"))
                continue
            for t in toks:
                if t not in vocab:
                    bad.append((e.keys[0], term, t))
                    continue
                if df is None:
                    df = index.W.tocsc()
                col = vocab[t]
                if df.indptr[col + 1] - df.indptr[col] < 2:
                    bad.append((e.keys[0], term, f"{t}: rare"))
    assert not bad, bad


def test_law_titles_are_exact_corpus_titles(index):
    titles = {e.get("doc_title_ne") for e in index.entries}
    for e in translit.ENTRIES:
        for law in e.laws:
            assert law in titles, law


def test_lexicon_is_substantial():
    assert len(translit.ENTRIES) >= 100
    assert sum(len(e.keys) for e in translit.ENTRIES) >= 800


@pytest.mark.parametrize("text,expected", [
    ("boss le din ko 12 ghanta kaam garauchha, overtime ko paisa pani dinna", "अतिरिक्त समय"),
    ("boss le din ko 12 ghanta kaam garauchha, overtime ko paisa pani dinna", "कार्य घण्टा"),
    ("mero shreemanko mrityu bhayo. sasu-sasura le sampatti ma haq chhaina", "सासू ससुरा"),
    ("manpower le thagyo", "वैदेशिक रोजगार"),
    ("gharbeti le deposit firta dinna", "धरौटी"),
    ("cheque bounce bhayo", "चेक अनादर"),
    ("kampani ko bhitri suchana bata share kinbech", "भित्री कारोबार"),
    ("police le jaheri darkhast lina maandaina", "जाहेरी दरखास्त"),
    ("mero dai lai jamanat rakhera chhutaune", "जमानत"),
    ("sano pasal ko VAT darta", "मूल्य अभिवृद्धि कर"),
])
def test_romanised_phrases_map_to_statutory_terms(text, expected):
    assert expected in translit.expand(text)


@pytest.mark.parametrize("a,b", [
    ("dharauti", "dharauta"),        # trailing vowel
    ("bibaha", "biwaha"),            # b/w/v
    ("shreemati", "srimati"),        # sh/s, ee/i
    ("sambandha bichhed", "sambandh bichhed"),
    ("talab", "tallab"),             # double letters
    ("jaheri", "jahiri"),
    ("ghareloo hinsa", "gharelu hinsa"),
])
def test_spelling_variants_hit_the_same_entry(a, b):
    ea = [e.keys for e in translit.match(a)]
    eb = [e.keys for e in translit.match(b)]
    assert ea and ea == eb


def test_chh_ch_variants_tolerated_but_theft_is_not_daughter():
    # aspirated/unaspirated spellings of a long word are the same word...
    assert translit.match("sambandha bicched") == translit.match("sambandha bichhed")
    # ...but chori (theft) and chhori (daughter) are different words
    theft = {e.terms[0] for e in translit.match("chori bhayo")}
    daughter = {e.terms[0] for e in translit.match("meri chhori le talab")}
    assert "चोरी" in theft and "छोरा" not in theft
    assert "चोरी" not in daughter


def test_postpositions_glued_to_the_word_are_stripped():
    assert translit.expand("gharbetile deposit") == translit.expand("gharbeti deposit")
    assert "वैदेशिक रोजगार" in translit.expand("manpowerle thagyo")
    assert "जग्गा" in translit.expand("jaggama kabja")


@pytest.mark.parametrize("text", [
    "What is the official language of Nepal?",
    "Which international treaties on human rights has Nepal ratified?",
    "What is the tenure of the House of Representatives?",
    "Is it legal to carry a gun in Nepal without a license?",
    "mero haq ke ho",                      # only a generic (weak) word
    "malai sampatti ko bare ma bhannus",   # only generic words
])
def test_ordinary_english_and_generic_words_do_not_fire(text):
    assert translit.match(text) == []
    assert translit.expand(text) == []


def test_laws_are_reported_for_strong_matches_only():
    assert translit.laws("overtime ko paisa") == ["श्रम ऐन, २०७४"]
    assert translit.laws("haq") == []


def test_devanagari_only_message_is_untouched():
    assert translit.match("घरबेटीले धरौटी फिर्ता दिएन") == []
