from app.text_norm import detect_language, fold, tokenize


def test_digits_and_vowel_length_fold_together():
    assert fold("दफा ९९") == fold("दफा 99")
    assert tokenize("नीति") == tokenize("निति")
    assert tokenize("पूर्व") == tokenize("पुर्व")
    assert tokenize("सँग") == tokenize("संग")


def test_postpositions_are_stripped_to_the_same_stem():
    stems = {tokenize(w)[0] for w in ["जग्गाको", "जग्गालाई", "जग्गामा", "जग्गा"]}
    assert stems == {"जग्गा"}
    assert tokenize("बालबालिकाहरूको") == tokenize("बालबालिका")


def test_zero_width_joiners_are_ignored():
    assert tokenize("प्राप्‍त") == tokenize("प्राप्त")


def test_stopwords_dropped_and_english_stemmed():
    assert tokenize("र वा तथा") == []
    assert tokenize("The tenants were evicted") == tokenize("tenant evict")


def test_danda_is_not_part_of_a_word():
    assert tokenize("हुनेछ।") == tokenize("हुनेछ")


def test_detect_language():
    assert detect_language("मेरो घरबेटीले धरौटी फिर्ता दिएन") == "ne"
    assert detect_language("my landlord kept my deposit") == "en"
    assert detect_language("दफा 5 of the Act?") == "ne"


def test_guess_language_handles_romanised_nepali():
    from app.text_norm import guess_language
    assert guess_language("k garne malai police le pakreko cha") == "ne"
    assert guess_language("gharbeti le deposit firta diyena") == "ne"
    assert guess_language("what about daughters?") == "en"
    assert guess_language("what's the weather in Kathmandu today?") == "en"
    assert guess_language("सम्बन्ध विच्छेद") == "ne"
