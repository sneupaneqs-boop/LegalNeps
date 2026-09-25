from devanagari_glyphs import visual_to_logical


def g(*parts):
    return [(p, False) for p in parts]


def test_prebase_i_matra_moves_after_consonant():
    # "मिति" is drawn ि म ि त
    assert visual_to_logical(g("ि", "म", "ि", "त")) == "मिति"
    assert visual_to_logical(g("ि", "न", "य", "म")) == "नियम"


def test_prebase_i_matra_moves_after_whole_conjunct():
    # visual: ि स् त  -> logical: स्ति
    assert visual_to_logical(g("ि", "स्", "त")) == "स्ति"
    # below-base rakar stays inside the cluster: ि प्र -> प्रि
    assert visual_to_logical(g("ि", "प्र", "य")) == "प्रिय"


def test_reph_moves_before_its_cluster():
    # गर्ने is drawn ग न (reph+े); logically ग र् न े
    glyphs = [("ग", False), ("न", False), ("ेर्", True)]
    assert visual_to_logical(glyphs) == "गर्ने"
    # सार्वभौम: स ा व (reph) भ ौ म
    glyphs = [("स", False), ("ा", False), ("व", False), ("र्", True), ("भ", False), ("ौ", False), ("म", False)]
    assert visual_to_logical(glyphs) == "सार्वभौम"


def test_half_form_ra_is_not_treated_as_reph():
    glyphs = [("र्", False), ("य", False)]
    assert visual_to_logical(glyphs) == "र्य"
