"""V3.3: a DATA-DRIVEN topical-fit gate.

The V3.2 checks prove a quote is real and says what the sentence says; they cannot prove the provision is ON TOPIC
for the person's question. The V3.2 live review (fresh 30 answers) had 24 of 70 kept sentences that were a real,
verbatim, verified quote from a provision that does not govern the person's situation (the hire-purchase chapter for
a tenant eviction, an Army Act pay deduction for a salary-tax question, a judges' service Act for private maternity
leave). Those arise when off-topic passages are in the prompt and the model feels obliged to use them.

This module scores every (question, passage) pair BEFORE generation (which sources the model sees; whether to answer
at all) and AFTER it (which cited sentences may stay). No LLM is involved (LLM entailment removed 44% of good
sentences and stays off). The score is a small logistic model over cheap features; the weights and threshold live in
`data/topical_fit.json`, are fitted by `eval/topical_fit_calibration.py` and are tested on data they were not fitted on
(see docs/PROGRESS.md, V3.3).

Features per (question, passage)                         family
  rank          1-based position among the retrieved sources           retrieval
  d_head        max over the question's queries of cos(query, "law | heading")     dense
  d_head_rel    d_head minus the best d_head among the candidate sources           dense
  d_pass_rel    the passage's cosine minus the best among the candidates           dense
  q_cov_head    idf-weighted share of the question's terms found in heading + law title   lexical
  q_cov_body    same over the passage text                                                lexical
  h_unexpl      idf-weighted share of the HEADING's distinctive terms the question (with its glossary/transliteration
                expansion) never mentions                                                lexical
  l_unexpl      the same for the LAW TITLE's subject terms ("सैनिक ऐन", "हुलाक ऐन", "उपभोक्ता संरक्षण ऐन")  lexical
  specialist    1 when the passage belongs to a specialist population/regime (army, judges, post, insolvency,
                hire-purchase, customs, instalment tax ...) that neither the question nor the matched plan mentions;
                the table is DATA (SPECIALIST below), each family says where its marker came from    marker

With no dense model the dense features drop out and a lexical-only model (fitted the same way) is used.
Precedents (a case title says nothing) use the body features only.
"""
from __future__ import annotations

import json
import logging
import math
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import config, glossary, translit
from .text_norm import DEVANAGARI_RE, fold, tokenize

log = logging.getLogger("kanooni.topical_fit")

MODEL_PATH = Path(__file__).parent / "data" / "topical_fit.json"

_PAREN_TAIL = re.compile(r"\([^)]*\)\s*$")
_GENERIC_TITLE = frozenset(tokenize(
    "मुलुकी देवानी फौजदारी अपराध संहिता ऐन नियमावली नियम नियमहरु निर्देशिका विनियम अध्यादेश संशोधन सम्बन्धी सम्बन्धि सहित "
    "व्यवस्था कार्यविधि निर्णय नं सर्वोच्च अदालत संयुक्त इजलास नेपाल नेपालको नेपाली सरकार "
    "ऐन कानुन कानून व्यक्ति बमोजिम अनुसार अन्य कुनै दफा उपदफा "
    "act law legal section rule provision code article court person may must shall"))
_SPECIFIC_MIN_LEN = 2


# ------------------------------------------------------------------ specialist regimes (DATA)
@dataclass(frozen=True)
class Family:
    id: str
    marker: re.Pattern      # in the passage's law title / heading / opening: it belongs to this regime
    cue: re.Pattern         # in the question (or its expansion, or the matched plan): the person is in this regime
    source: str             # where the marker came from: "corpus" (law/chapter titles), "review1", "review2"
    where: str = "title"    # "title": law title + section heading only (broad regime words); "any": also the opening text


def _f(p: str) -> re.Pattern:
    return re.compile(fold(p))


SPECIALIST: tuple[Family, ...] = (
    # ---- from the corpus's law and chapter titles (an Act or chapter that regulates one population / regime)
    Family("armed_forces", _f(r"सैनिक|सेना|सशस्त्र प्रहरी|सैन्य"),
           _f(r"सेना|सैनिक|सैन्य|army|soldier|military|armed police|फौज"), "corpus"),
    Family("judiciary", _f(r"न्यायाधीश|न्याय सेवा|न्यायिक परिषद"),
           _f(r"judge|न्यायाधीश|न्याय सेवा|judicial council"), "corpus"),
    Family("postal", _f(r"हुलाक|धनादेश"),
           _f(r"post ?office|postal|money order|हुलाक|धनादेश|postman|courier"), "corpus"),
    Family("insolvency", _f(r"दामासाही|दामासाहि"),
           _f(r"bankrupt|insolven|दामासाही|liquidat|दामासाहि"), "corpus", "any"),
    Family("hire_purchase", _f(r"हायर पर्चेज|हायर परचेज"),
           _f(r"hire ?purchase|हायर|purchase agreement|पर्चेज|on instal"), "corpus", "any"),
    Family("customs_excise", _f(r"भन्सार|अन्तःशुल्क|अन्त:शुल्क|अन्तः शुल्क|निकासी पैठारी|निकासी|पैठारी"),
           _f(r"customs|excise|import|export|भन्सार|अन्तःशुल्क|निकासी|पैठारी|smuggl"), "corpus"),
    Family("election_parliament", _f(r"निर्वाचन|मतदाता|संसद|राष्ट्रिय सभा|प्रतिनिधि सभा|प्रदेश सभा"),
           _f(r"election|vote|voter|candidate|parliament|निर्वाचन|मतदान|मतदाता|उम्मेदवार|संसद|सांसद"), "corpus"),
    Family("civil_service", _f(r"निजामती|लोक सेवा आयोग|सरकारी कर्मचारी"),
           _f(r"civil servant|civil service|government (?:job|employee|servant)|निजामती|लोक सेवा|सरकारी कर्मचारी|सरकारी जागिर"), "corpus"),
    Family("prison", _f(r"कारागार"),
           _f(r"prison|jail|inmate|convict|कारागार|कैदी|जेल"), "corpus"),
    Family("tax_instalment", _f(r"किस्तामा कर|किस्ता(?:मा)? कर|अग्रिम कर"),
           _f(r"instal?ment|advance tax|किस्ता|अग्रिम कर|business|व्यवसाय|self.?employed|तीन किस्ता"), "corpus", "any"),
    Family("education_institution", _f(r"शिक्षक सेवा|शिक्षा नियमावली|विश्वविद्यालय"),
           _f(r"teacher|school|university|college|student|शिक्षक|विद्यालय|विश्वविद्यालय|विद्यार्थी"), "corpus"),
    # ---- markers first seen in the labelled wrong-law passages of review 2 (used in production, NOT in the
    #      held-out test of V3.3)
    Family("widow", _f(r"विधवा"),
           _f(r"widow|विधवा|bidhwa|bidhawa|remarr|पुनर्विवाह|अर्को विवाह"), "review2", "any"),
    Family("producer_liability", _f(r"उत्पादक|पैठारीकर्ता|सञ्चयकर्ता|ढुवानीकर्ता|वितरक"),
           _f(r"consumer|उपभोक्ता|defect|product|उत्पादन|ग्राहक|seller|shop|dealer|बिक्रेता|manufactur"), "review2", "any"),
    Family("professional_brokerage", _f(r"घर\s?जग्गा सम्बन्धी कारोबार|घरजग्गा दलाल"),
           _f(r"broker|dalal|agent|दलाल|consultan|real estate|घरजग्गा कारोबार"), "review2", "any"),
    Family("sentence_procedure", _f(r"घटी सजाय गर्न|सजाय निर्धारण"),
           _f(r"sentenc|सजाय निर्धारण|reduc(?:e|tion) (?:of )?(?:the )?punish|घटी सजाय"), "review2", "any"),
)


def specialist_hits(head_text: str, law_title: str, opening: str, question_side: str, guidance: str = "",
                    sources: tuple[str, ...] = ("corpus", "review1", "review2")) -> list[str]:
    """Family ids the passage belongs to although neither the question nor the matched plan mentions the regime."""
    titles = fold(" ".join((law_title or "", head_text or "")))
    anywhere = titles + " " + fold((opening or "")[:400])
    asked = fold(" ".join((question_side or "", guidance or "")))
    out = []
    for fam in SPECIALIST:
        if fam.source not in sources:
            continue
        if fam.marker.search(anywhere if fam.where == "any" else titles) and not fam.cue.search(asked):
            out.append(fam.id)
    return out


# ------------------------------------------------------------------ profile of the question
def _cterms(text: str) -> list[str]:
    return [t for t in dict.fromkeys(tokenize(text or ""))
            if not t.isdigit() and len(t) >= _SPECIFIC_MIN_LEN and t not in _GENERIC_TITLE]


def _same(a: str, b: str) -> bool:
    return a == b or (len(a) >= 5 and len(b) >= 5 and a[:5] == b[:5])


def _in(term: str, pool) -> bool:
    return term in pool or (len(term) >= 5 and any(_same(term, p) for p in pool))


@dataclass
class Profile:
    """Everything the gate needs to know about one question."""
    message: str
    queries: list[str] = field(default_factory=list)
    terms: frozenset = frozenset()          # content stems of the message, its rewrites and glossary/translit expansions
    question_side: str = ""                 # raw text the specialist cues are matched on
    guidance: str = ""                      # the matched playbook's text


def make_profile(message: str, analysis: dict | None = None, guidance: str = "", queries=None) -> Profile:
    """`queries`: weighted (text, weight) list as generation.build_queries makes it (None = derived here)."""
    analysis = analysis or {}
    question = analysis.get("question") or ""
    ne_rewrites = [str(x) for x in (analysis.get("queries_ne") or [])]
    exp = list(glossary.expand(message)) + list(translit.expand(message))
    if question and question != message:
        exp += list(glossary.expand(question)) + list(translit.expand(question))
    side = " ".join([message, question, *ne_rewrites, *exp])
    terms = frozenset(_cterms(side))
    qs: list[str] = []
    for item in queries or []:
        text, w = (item, 1.0) if isinstance(item, str) else item
        if w >= 0.5 and text.strip() and text not in qs:
            qs.append(text)
    if not qs:
        qs = [message]
    return Profile(message=message, queries=qs[:config.FIT_MAX_QUERIES], terms=terms, question_side=side, guidance=guidance or "")


# ------------------------------------------------------------------ corpus statistics
class _Stats:
    """idf of a stem over the BM25 index's passages (document frequency from the CSC matrix - no scan)."""

    def __init__(self, idx):
        self.idx = idx
        self.n = max(1, len(idx))
        self.df = np.diff(idx.W.indptr)
        self.vocab = idx.vocab
        self._memo: dict[str, float] = {}

    def idf(self, term: str) -> float:
        v = self._memo.get(term)
        if v is None:
            j = self.vocab.get(term)
            d = 0.5 if j is None else float(self.df[j])
            v = self._memo[term] = math.log(1 + (self.n - d + 0.5) / (d + 0.5))
        return v


_stats_cache: dict[int, _Stats] = {}


def _stats(idx) -> _Stats:
    s = _stats_cache.get(id(idx))
    if s is None:
        s = _stats_cache[id(idx)] = _Stats(idx)
    return s


# ------------------------------------------------------------------ features
FEATURES = ("rank", "d_head", "d_head_rel", "d_pass_rel", "q_cov_head", "q_cov_body", "h_unexpl", "l_unexpl")
DENSE_FEATURES = ("d_head", "d_head_rel", "d_pass_rel")
HEAD_ONLY = ("d_head", "d_head_rel", "q_cov_head", "h_unexpl", "l_unexpl")  # meaningless for a precedent (its "heading" is a case number)


def heading_of(src: dict) -> tuple[str, str]:
    """(law title, section heading) of a passage without the parenthetical law name repeated after the heading."""
    law = _PAREN_TAIL.sub("", str(src.get("doc_title_ne") or src.get("source_ne") or "")).strip()
    head = _PAREN_TAIL.sub("", str(src.get("title_ne") or "")).strip()
    if head == law:
        head = ""
    return law, head


def _is_precedent(src: dict) -> bool:
    return src.get("category") == "precedent"


def _head_string(src: dict) -> str:
    law, head = heading_of(src)
    return (law[:110] + (" | " + head[:110] if head else "")).strip()


class Scorer:
    """Features (and the score) of the candidate passages for ONE question. `candidates` are the retrieved sources
    (dict as search returns them); they define the relative dense features and the rank."""

    def __init__(self, profile: Profile, idx=None, dense=None, model: dict | None = None, use_dense: bool | None = None):
        from .retrieval import get_index
        self.profile = profile
        self.idx = idx or get_index()
        self.model = model if model is not None else load_model()
        # the e5 cosines are compressed (0.85 +- 0.02 for on- and off-topic alike) and did not survive the held-out
        # test: the dense features are computed only with FIT_USE_DENSE=1 (or use_dense=True, for calibration)
        want = config.FIT_USE_DENSE if use_dense is None else use_dense
        self.dense = (dense if dense is not None else getattr(self.idx, "dense", None)) if want else None
        self.stats = _stats(self.idx)
        self._qvecs = None
        self._rows: dict[str, int] | None = None

    # -- dense helpers -------------------------------------------------------
    def _query_vectors(self):
        if self._qvecs is None:
            self._qvecs = self.dense.encode_queries(self.profile.queries)
        return self._qvecs

    def _row(self, src: dict) -> int | None:
        if self._rows is None:
            self._rows = {pid: i for i, pid in enumerate(self.idx.ids)}
        return self._rows.get(src.get("id"))

    def _dense_features(self, cands: list[dict]) -> list[dict]:
        """d_head, d_head_rel, d_pass_rel per candidate (NaN when the passage has no vector)."""
        qv = self._query_vectors()
        heads = [_head_string(s) for s in cands]
        hv = self.dense.encoder.encode(heads, "passage: ", max_tokens=64) if heads else np.zeros((0, qv.shape[1]))
        d_head = (hv @ qv.T).max(axis=1) if len(heads) else np.zeros(0)
        store = self.dense.store
        rows = [self._row(s) for s in cands]
        d_pass = np.full(len(cands), np.nan, dtype=np.float32)
        ok = [i for i, r in enumerate(rows) if r is not None and store.have[r]]
        if ok:
            rr = np.array([rows[i] for i in ok])
            cos = (store.q[rr].astype(np.float32) @ qv.T.astype(np.float32)) * store.scale[rr, None]
            d_pass[ok] = cos.max(axis=1)
        out = []
        for k, s in enumerate(cands):
            out.append({"d_head": float(d_head[k]) if not _is_precedent(s) and heads[k] else float("nan"),
                        "_pass": float(d_pass[k])})
        for cat in (False, True):
            grp = [k for k, s in enumerate(cands) if _is_precedent(s) == cat]
            best_h = max((out[k]["d_head"] for k in grp if not math.isnan(out[k]["d_head"])), default=float("nan"))
            best_p = max((out[k]["_pass"] for k in grp if not math.isnan(out[k]["_pass"])), default=float("nan"))
            for k in grp:
                out[k]["d_head_rel"] = out[k]["d_head"] - best_h if not math.isnan(out[k]["d_head"]) else float("nan")
                out[k]["d_pass_rel"] = out[k]["_pass"] - best_p if not math.isnan(out[k]["_pass"]) else float("nan")
        return out

    # -- lexical features ------------------------------------------------------
    def _lexical(self, src: dict) -> dict:
        st, T = self.stats, self.profile.terms
        law, head = heading_of(src)
        H = _cterms(head) if not _is_precedent(src) else []
        L = _cterms(law) if not _is_precedent(src) else []
        body = set(tokenize(" ".join(str(src.get("text_ne") or src.get("text_en") or "").split())[:1500]))
        Tdev = [t for t in T if DEVANAGARI_RE.match(t)] or list(T)
        qi = {t: st.idf(t) for t in Tdev}
        tot = sum(qi.values()) or 1.0
        HL = set(H) | set(L)

        def unexpl(terms):
            if not terms:
                return 0.0
            w = {t: st.idf(t) for t in terms}
            return sum(v for t, v in w.items() if not _in(t, T)) / (sum(w.values()) or 1.0)

        return {"q_cov_head": sum(v for t, v in qi.items() if _in(t, HL)) / tot if HL else 0.0,
                "q_cov_body": sum(v for t, v in qi.items() if _in(t, body)) / tot,
                "h_unexpl": unexpl(H), "l_unexpl": unexpl(L)}

    # -- public --------------------------------------------------------------------
    def features(self, cands: list[dict], ranks: list[float] | None = None) -> list[dict]:
        dense_f = self._dense_features(cands) if self.dense is not None else None
        out = []
        for k, s in enumerate(cands):
            f = {"rank": float(ranks[k] if ranks else k + 1), **self._lexical(s)}
            if dense_f is not None:
                f.update({x: dense_f[k][x] for x in DENSE_FEATURES})
            law, head = heading_of(s)
            f["specialist"] = specialist_hits(head, law, str(s.get("text_ne") or ""), self.profile.question_side,
                                              self.profile.guidance, self.model.get("specialist_sources", ("corpus", "review1", "review2")))
            out.append(f)
        return out


# ------------------------------------------------------------------ the model
@lru_cache(maxsize=1)
def load_model() -> dict:
    """The fitted gate (data/topical_fit.json); a missing/broken file disables the gate (fail open)."""
    try:
        return json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        log.warning("topical fit model unavailable (%s): gate disabled", e)
        return {}


def _variant(model: dict, has_dense: bool) -> dict | None:
    if not model:
        return None
    return model.get("dense" if has_dense else "lexical") or model.get("lexical") or model.get("dense")


def score(f: dict, variant: dict, precedent: bool = False) -> float:
    """Off-topic logit (higher = more likely off topic)."""
    names, w, mu, sd, b = variant["features"], variant["w"], variant["mean"], variant["std"], variant["b"]
    z = b
    for name, wk, m, s in zip(names, w, mu, sd):
        v = f.get(name)
        if v is None or (isinstance(v, float) and math.isnan(v)) or (precedent and name in HEAD_ONLY):
            continue  # a missing feature contributes its mean (0 after standardising)
        z += wk * (v - m) / (s or 1.0)
    return z


@dataclass
class Verdict:
    id: str
    ok: bool
    score: float
    reasons: list = field(default_factory=list)
    features: dict = field(default_factory=dict)
    pinned: bool = False


def judge(cands: list[dict], scorer: Scorer, model: dict | None = None, ranks: list[float] | None = None) -> list[Verdict]:
    """A verdict per candidate. A passage fails when a specialist regime the question never mentions is in it, or
    its off-topic score passes the fitted threshold. Pinned playbook provisions are never failed (curated)."""
    model = model if model is not None else scorer.model
    variant = _variant(model, scorer.dense is not None)
    feats = scorer.features(cands, ranks)
    out = []
    for s, f in zip(cands, feats):
        prec = _is_precedent(s)
        reasons = []
        z = score(f, variant, prec) if variant else 0.0
        if variant and z > variant["threshold_prec" if prec else "threshold"]:
            reasons.append("low_topical_fit")
        if f["specialist"] and not prec:
            reasons.append("specialist:" + "+".join(f["specialist"]))
        pinned = bool(s.get("pinned"))
        out.append(Verdict(id=s.get("id", ""), ok=pinned or not reasons, score=z, reasons=reasons, features=f, pinned=pinned))
    return out
