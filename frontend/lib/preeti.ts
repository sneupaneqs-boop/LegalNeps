// Preeti -> Unicode Devanagari converter (client-side, no dependencies).
//
// Preeti is a legacy *font*: the text is ordinary Latin characters that the
// font draws as Devanagari glyphs ("g]kfn" looks like नेपाल). Converting is
// therefore a table lookup plus fix-ups for the places where the font's visual
// order differs from Unicode logical order:
//   * the short-i matra (ि) is typed BEFORE its consonant ("l" + "g" = नि),
//   * reph (र्) is typed AFTER the syllable it sits on ("ug]{" = गर्ने),
//   * some letters are typed as consonant + matra pairs ("0f" = ण, "if" = ष),
//   * ो / ौ are typed as ा + े / ा + ै.
//
// The character table is the community-standard Preeti keyboard map. Every
// entry below was cross-checked against three independent published tables
// (the nep-tt2utf test vectors, the `preeti-unicode` and `unicode-to-preeti`
// packages); glyphs on which those tables disagree (Ì ° © ¤) are left out
// rather than guessed, and pass through unchanged.

// Devanagari code points used by the fix-up rules (written as escapes so the
// combining marks stay visible in review).
const HALANT = "्"; // ्
const AA = "ा"; // ा
const E = "े"; // े
const AI = "ै"; // ै
const O = "ो"; // ो
const AU = "ौ"; // ौ
const CANDRA = "ॅ"; // ॅ
const CANDRA_O = "ॉ"; // ॉ
const ANUSVARA = "ं"; // ं
const CANDRABINDU = "ँ"; // ँ
const SHORT_I = "ि"; // ि
const RA = "र"; // र

// Multi-character sequences (matched before single characters).
const SEQUENCES: Record<string, string> = {
  "cf‘": "ऑ",
  "c‘f": "ऑ",
  "cf}": "औ",
  "cf]": "ओ",
  cf: "आ",
  "P]": "ऐ",
  "O{": "ई",
  "k|m": "फ्र",
  km: "फ",
  em: "झ",
  pm: "ऊ",
  Qm: "क्त",
  qm: "क्र",
};

// Single characters.
const CHARS: Record<string, string> = {
  // lowercase: full consonants and letters ("l" is deliberately absent: it is the i-matra marker)
  a: "ब", b: "द", c: "अ", d: "म", e: "भ", f: AA, g: "न", h: "ज", i: "ष्", j: "व",
  k: "प", n: "ल", o: "य", p: "उ", q: "त्र", r: "च", s: "क", t: "त", u: "ग",
  v: "ख", w: "ध", x: "ह", y: "थ", z: "श",
  // uppercase: half consonants and matras
  A: "ब्", B: "द्य", C: "ऋ", D: "म्", E: "भ्", F: CANDRABINDU, G: "न्", H: "ज्",
  I: "क्ष्", J: "व्", K: "प्", L: "ी", M: "ः", N: "ल्", O: "इ", P: "ए", Q: "त्त",
  R: "च्", S: "क्", T: "त्", U: "ग्", V: "ख्", W: "ध्", X: "ह्", Y: "थ्", Z: "श्",
  // digit row = consonants; the shifted row = Devanagari digits
  "0": "ण्", "1": "ज्ञ", "2": "द्द", "3": "घ", "4": "द्ध", "5": "छ", "6": "ट",
  "7": "ठ", "8": "ड", "9": "ढ",
  "!": "१", "@": "२", "#": "३", $: "४", "%": "५", "^": "६", "&": "७", "*": "८",
  "(": "९", ")": "०",
  // punctuation row ("{" stays as the reph marker and is resolved after the lookup)
  "-": "(", _: ")", "=": ".", "+": ANUSVARA, "~": "ञ्", "`": "ञ",
  "[": "ृ", "]": E, "}": AI, "\\": HALANT, "|": "्र",
  ";": "स", ":": "स्", "'": "ु", '"': "ू", ",": ",", "<": "?", ".": "।",
  ">": "श्र", "/": "र", "?": "रु",
  // Latin-1 / cp1252 glyph positions the font uses for conjuncts and marks
  "ç": "ॐ", "˜": "ऽ", "¡": "ज्ञ्", "¢": "द्घ", "£": "घ्", "ª": "ङ", "«": "्र",
  "´": "झ", "‰": "झ्", "ˆ": "फ्", "Å": "हृ", "Ë": "ङ्ग", "Í": "ङ्क", "Î": "ङ्ख",
  "Ý": "ट्ठ", "å": "द्व", "Ø": "्य", "ß": "द्म", "„": "ध्र", "‹": "ङ्घ", "›": "द्र",
  "•": "ड्ड", "§": "ट्ट", "¶": "ठ्ठ", "¿": "रू", "‘": CANDRA,
  "¥": `${RA}${HALANT}‍`, // reph + ZWJ, as in पर्‍यो ("k¥of]")
  // glyphs standing in for punctuation whose plain keys the font took over
  "Ö": "=", "Ù": ";", "…": "‘", "Ú": "’", "Û": "!", "Ü": "%", "æ": "“",
  "Æ": "”", "±": "+",
};

const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

const TOKEN_RE = new RegExp(
  [...Object.keys(SEQUENCES), ...Object.keys(CHARS)]
    .sort((a, b) => b.length - a.length)
    .map(escapeRe)
    .join("|"),
  "g"
);

const CONSONANT = "[\\u0915-\\u0939\\u0958-\\u095F]";
const MATRAS = "\\u093E-\\u094C\\u0900-\\u0903\\u0945\\u0949"; // ा..ौ, ँ ं ः, ॅ ॉ
const CLUSTER = `(?:${CONSONANT}${HALANT})*${CONSONANT}`; // क्ष, स्त्र, न ...

const I_MATRA_RE = new RegExp(`l(${CLUSTER})`, "g");
const REPH_RE = new RegExp(`(${CLUSTER})([${MATRAS}]*)\\{`, "g");
// Matras typed on the wrong side of a conjunct: "6]«" is ट + े + ्र (want ट्रे);
// in "k|:'tt" the ु is typed before the त it belongs to.
const MATRA_BEFORE_HALANT_RE = new RegExp(`([${MATRAS}]+)(${HALANT}(?:${CONSONANT}${HALANT})*${CONSONANT})`, "g");
const MATRA_AFTER_HALANT_RE = new RegExp(`${HALANT}([${MATRAS}]+)(${CLUSTER})`, "g");
const NASAL_BEFORE_MATRA_RE = new RegExp(`([${ANUSVARA}${CANDRABINDU}])([\\u093E-\\u094C]+)`, "g");

const rx = (src: string) => new RegExp(src, "g");

// [pattern, replacement], applied in order right after the table lookup.
const JOIN_RULES: [RegExp, string][] = [
  // A half consonant followed by ा is a full consonant: ण = "0f", ष = "if", क्ष = "If".
  // Must run before ो/ौ are joined: "u0f]z" is गणेश, its "]" is a separate े.
  [rx(`${HALANT}${AA}`), ""],
  // ो / ौ are typed as ा + े / ा + ै (occasionally in the other order)
  [rx(`${AA}${E}|${E}${AA}`), O],
  [rx(`${AA}${AI}|${AI}${AA}`), AU],
  [rx(`${AA}${CANDRA}`), CANDRA_O],
  [rx("अ" + AA), "आ"], // अ + ा = आ
  [rx("आ" + E), "ओ"], // आ + े = ओ
  [rx("आ" + AI), "औ"], // आ + ै = औ
  [rx("ए" + E), "ऐ"], // ए + े = ऐ
  [rx(`आ([${ANUSVARA}${CANDRABINDU}])${AI}`), "औ$1"], // "cf+}" = औं
  [rx(`आ([${ANUSVARA}${CANDRABINDU}])${E}`), "ओ$1"],
  // repeated matras from double keystrokes
  [rx(`${E}${E}`), E],
  [rx(`${AI}${AI}`), AI],
  [rx("ुु"), "ु"],
  [rx("ूू"), "ू"],
];

export function preetiToUnicode(input: string): string {
  if (!input) return "";
  let s = input.normalize("NFC");

  // "'" / "]" / "\" typed between a base letter and its modifier "m" (k'm = फु): put m next to the base
  s = s.replace(/([kepQq]\|?)([\]'"[}+F\\]+)m/g, "$1m$2");
  // "f{]" and "f]{" spell the same syllable: keep the reph after the matras
  s = s.replace(/\{([\]}]+)/g, "$1{");

  s = s.replace(TOKEN_RE, (m) => (m in SEQUENCES ? SEQUENCES[m] : CHARS[m]));

  for (const [re, rep] of JOIN_RULES) s = s.replace(re, rep);
  s = s.replace(MATRA_BEFORE_HALANT_RE, "$2$1");
  s = s.replace(MATRA_AFTER_HALANT_RE, `${HALANT}$2$1`);

  // the short-i matra is typed before its consonant cluster
  s = s.replace(I_MATRA_RE, `$1${SHORT_I}`);

  // reph is typed after the syllable; Unicode wants it before the consonant cluster
  s = s.replace(REPH_RE, `${RA}${HALANT}$1$2`);
  s = s.replace(/\{/g, `${RA}${HALANT}`); // a stray reph with nothing to attach to

  // anusvara / chandrabindu come after the matra
  s = s.replace(NASAL_BEFORE_MATRA_RE, "$2$1");

  return s;
}
