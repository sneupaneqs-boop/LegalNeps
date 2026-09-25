"""
Recovers correct Unicode text from Devanagari PDFs whose ToUnicode maps are
broken - the dominant defect in lawcommission.gov.np PDFs typeset in
Kalimati (e.g. "मममि" for "मिति", "्" for spaces).

Word-generated PDFs keep the font's original glyph ids (GIDs) in visual
order, but build each document's ToUnicode map from the first context a
glyph appears in, so the same glyph decodes differently per document. We
ignore ToUnicode and instead:

1. derive a GID -> Unicode table from a complete copy of the font (its cmap
   plus GSUB substitutions resolved to a fixpoint, respecting what each
   OpenType feature means: 'blwf' र+् is the below-base "्र", 'rphf' is the
   reph "र्" drawn above the cluster);
2. map each span's glyph ids through that table;
3. convert visual order back to logical order (pre-base ि moves after its
   consonant cluster, the reph moves in front of the cluster it sits on).
"""
from __future__ import annotations

import io
import re

HALANT = "्"
I_MATRA = "ि"
NUKTA = "़"
REPH = "र" + HALANT
CONSONANT_RE = re.compile(r"[क-हक़-य़]")
DEPENDENT_RE = re.compile(r"[ऺ-ौॎॏॕ-ॗँ-ःॢॣ॒॑]")

BELOW_FEATURES = {"blwf", "pstf"}  # input [C, halant] -> below/post form == halant + C
REPH_FEATURES = {"rphf"}


def build_glyph_table(font_bytes: bytes) -> dict:
    """Returns {"text": {gid: str}, "reph": [gid,...], "prebase_i": [gid,...]}."""
    from fontTools.ttLib import TTFont

    font = TTFont(io.BytesIO(font_bytes))
    order = font.getGlyphOrder()
    gid_of = {name: i for i, name in enumerate(order)}
    text: dict[str, str] = {}
    for cp, name in sorted((font.getBestCmap() or {}).items()):
        if cp in (0x200C, 0x200D):
            text.setdefault(name, "")
        else:
            text.setdefault(name, chr(cp))
    reph: set[str] = set()

    rules: list[tuple[str, list[str], list[str]]] = []  # (feature, inputs, outputs)
    if "GSUB" in font:
        g = font["GSUB"].table
        feats: dict[int, set[str]] = {}
        for fr in g.FeatureList.FeatureRecord:
            for li in fr.Feature.LookupListIndex:
                feats.setdefault(li, set()).add(fr.FeatureTag)
        for li, lookup in enumerate(g.LookupList.Lookup):
            tag = next(iter(sorted(feats.get(li, {"?"}))))
            for st in lookup.SubTable:
                if st.LookupType == 7:
                    st = st.ExtSubTable
                t = st.LookupType
                if t == 1:
                    rules += [(tag, [a], [b]) for a, b in st.mapping.items()]
                elif t == 2:
                    rules += [(tag, [a], list(seq)) for a, seq in st.mapping.items()]
                elif t == 3:
                    rules += [(tag, [a], [b]) for a, alts in st.alternates.items() for b in alts]
                elif t == 4:
                    for first, ligs in st.ligatures.items():
                        rules += [(tag, [first] + list(l.Component), [l.LigGlyph]) for l in ligs]

    # Feature-specific rules first so e.g. the blwf rakar gets "्र" before
    # some generic rule could label it.
    rules.sort(key=lambda r: 0 if r[0] in BELOW_FEATURES | REPH_FEATURES else 1)
    changed = True
    while changed:
        changed = False
        for tag, ins, outs in rules:
            if not all(x in text for x in ins):
                continue
            if tag in BELOW_FEATURES and len(ins) == 2 and text[ins[1]] == HALANT:
                joined = HALANT + text[ins[0]]
            else:
                joined = "".join(text[x] for x in ins)
            is_reph = tag in REPH_FEATURES or any(x in reph for x in ins)
            for k, o in enumerate(outs):
                if o not in text:
                    text[o] = joined if k == 0 else ""
                    if is_reph and k == 0:
                        reph.add(o)
                    changed = True

    return {
        "text": {gid_of[n]: s for n, s in text.items() if n in gid_of},
        "reph": sorted(gid_of[n] for n in reph if n in gid_of),
    }


def visual_to_logical(glyphs: list[tuple[str, bool]]) -> str:
    """glyphs: (unicode string, is_reph) per glyph, in visual order."""
    out: list[tuple[str, bool]] = []
    i, n = 0, len(glyphs)
    while i < n:
        s, rf = glyphs[i]
        if s == I_MATRA:
            # pre-base i-matra: move it after the next consonant cluster
            j, cluster = i + 1, []
            while j < n and glyphs[j][0].endswith(HALANT) and CONSONANT_RE.match(glyphs[j][0]) and not glyphs[j][1]:
                cluster.append(glyphs[j])  # half forms
                j += 1
            if j < n and CONSONANT_RE.match(glyphs[j][0]) and not glyphs[j][1]:
                cluster.append(glyphs[j])
                j += 1
                # below-base forms / nukta belong to the cluster too
                while j < n and (glyphs[j][0] == NUKTA or (glyphs[j][0].startswith(HALANT) and len(glyphs[j][0]) == 2)):
                    cluster.append(glyphs[j])
                    j += 1
                out.extend(cluster)
                out.append((s, False))
                i = j
                continue
        out.append((s, rf))
        i += 1

    res: list[str] = []
    for s, rf in out:
        if rf and REPH in s and res:
            rest = s.replace(REPH, "", 1)
            k = len(res) - 1
            while k >= 0 and res[k] and all(DEPENDENT_RE.match(c) or c == HALANT for c in res[k]):
                k -= 1  # skip matras / below-base forms attached to the cluster
            if k >= 0 and CONSONANT_RE.match(res[k] or ""):
                while k - 1 >= 0 and res[k - 1].endswith(HALANT) and CONSONANT_RE.match(res[k - 1]):
                    k -= 1  # include preceding half forms
                res.insert(k, REPH)
                if rest:
                    res.append(rest)
                continue
        res.append(s)
    return "".join(res)


def decode_span(chars, table: dict) -> str | None:
    """chars: PyMuPDF texttrace char tuples (ucs, gid, origin, bbox).
    Returns None if the span has a Devanagari glyph the table doesn't know
    (caller should then fall back to the PDF's own ToUnicode text)."""
    text_of = table["text"]
    reph = table.get("reph_set") or set(table["reph"])
    glyphs: list[tuple[str, bool]] = []
    for c in chars:
        gid = c[1]
        if gid < 0:
            continue  # continuation of the previous glyph's multi-char map
        s = text_of.get(gid)
        if s is None:
            s = chr(c[0]) if c[0] > 0 else ""
            if s and "ऀ" <= s <= "ॿ":
                return None
        glyphs.append((s, gid in reph))

    # Nepali text often puts a ZWJ after a halant (प्राप्‍त); fonts without a
    # ZWJ glyph draw it with the space glyph, which would split the word.
    cleaned: list[tuple[str, bool]] = []
    for k, g in enumerate(glyphs):
        if g[0] == " " and cleaned and cleaned[-1][0].endswith(HALANT) and k + 1 < len(glyphs) \
                and CONSONANT_RE.match(glyphs[k + 1][0] or ""):
            continue
        cleaned.append(g)
    return visual_to_logical(cleaned)


def prepare(table: dict) -> dict:
    """Normalise a table loaded from JSON (string keys) for fast lookups."""
    return {
        "text": {int(k): v for k, v in table["text"].items()},
        "reph": table["reph"],
        "reph_set": set(table["reph"]),
    }


# --- version-independent decoding via glyph outlines -----------------------
# Different Kalimati builds number their glyphs differently, but a glyph's
# outline (its contour coordinates) is the same in every build. Keying the
# reference table by outline hash lets us decode any build/subset.

def _outline_hash(glyf, name: str) -> str | None:
    import hashlib

    try:
        coords, ends, flags = glyf[name].getCoordinates(glyf)
    except Exception:  # noqa: BLE001
        return None
    if len(coords) == 0:
        return None  # empty outline (space, ZWJ, .notdef without contours)
    h = hashlib.sha1()
    h.update(bytes(str(list(coords)), "ascii"))
    h.update(bytes(str(list(ends)), "ascii"))
    return h.hexdigest()[:16]


def build_reference(font_bytes: bytes) -> dict:
    """{"hash_text": {outline_hash: text}, "reph_hashes": [...]} from a
    complete font (needs cmap + GSUB)."""
    from fontTools.ttLib import TTFont

    table = build_glyph_table(font_bytes)
    font = TTFont(io.BytesIO(font_bytes))
    glyf = font["glyf"]
    order = font.getGlyphOrder()
    reph = set(table["reph"])
    hash_text, reph_hashes, clashes = {}, set(), set()
    for gid, text in table["text"].items():
        h = _outline_hash(glyf, order[gid])
        if h is None:
            continue
        if h in hash_text and hash_text[h] != text:
            clashes.add(h)  # identical outlines, different meaning: can't decide
        hash_text[h] = text
        if gid in reph:
            reph_hashes.add(h)
    for h in clashes:
        hash_text.pop(h, None)
    return {"hash_text": hash_text, "reph_hashes": sorted(reph_hashes)}


def table_for_embedded(font_bytes: bytes, reference: dict) -> dict | None:
    """GID->text table for an embedded (possibly subset, any-build) font,
    matched to the reference by outline. None if it isn't the same design."""
    from fontTools.ttLib import TTFont

    try:
        font = TTFont(io.BytesIO(font_bytes))
        glyf = font["glyf"]
    except Exception:  # noqa: BLE001
        return None
    order = font.getGlyphOrder()
    try:
        cmap = {name: chr(cp) for cp, name in (font.getBestCmap() or {}).items()}
    except Exception:  # noqa: BLE001 - subset without a cmap table
        cmap = {}
    hash_text = reference["hash_text"]
    reph_h = set(reference["reph_hashes"])
    text, reph, matched, outlined = {}, set(), 0, 0
    for gid, name in enumerate(order):
        h = _outline_hash(glyf, name)
        if h is None:
            if name in cmap:
                text[gid] = cmap[name]
            elif name in ("space", "uni0020", "nbspace", "uni00A0"):
                text[gid] = " "
            continue
        outlined += 1
        if h in hash_text:
            text[gid] = hash_text[h]
            matched += 1
            if h in reph_h:
                reph.add(gid)
        elif name in cmap:
            text[gid] = cmap[name]
    if outlined == 0 or matched / outlined < 0.6:
        return None  # a different typeface
    return {"text": text, "reph": sorted(reph), "reph_set": reph}
