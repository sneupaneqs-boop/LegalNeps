import { expect, test } from "@playwright/test";
import { preetiToUnicode } from "../../lib/preeti";

// [Preeti as typed, expected Unicode]. Inputs are what a Preeti keyboard
// produces for each word; expected values are the correct Nepali spellings.
const PAIRS: [string, string][] = [
  // plain letters and matras
  ["g]kfn", "नेपाल"],
  ["cbfnt", "अदालत"],
  ["tna", "तलब"],
  ["/fli6«o", "राष्ट्रिय"],
  ["ph'/L", "उजुरी"],
  ["d'2f", "मुद्दा"],
  ["k'g/fj]bg", "पुनरावेदन"],
  ["sfg\"g", "कानून"],
  ["sfg\"gL ;fyL", "कानूनी साथी"],
  // ो / ौ typed as ा + े / ा + ै
  ["/f]huf/L", "रोजगारी"],
  ["w/f}6L", "धरौटी"],
  ["cfof]u", "आयोग"],
  ["cf}iflw", "औषधि"],
  // short-i matra is typed before the consonant (and before whole conjuncts)
  ["lxdfn", "हिमाल"],
  ["ljw]os", "विधेयक"],
  ["k|ltlqmof", "प्रतिक्रिया"],
  ["lhn\\nf", "जिल्ला"],
  ["cg'dlt", "अनुमति"],
  // reph is typed after the syllable
  ["ug{]", "गर्ने"],
  ["ug]{", "गर्ने"],
  ["wd{", "धर्म"],
  ["cy{", "अर्थ"],
  ["sfo{fno", "कार्यालय"],
  ["lg0f{o", "निर्णय"],
  ["d\"lt{", "मूर्ति"],
  ["sLlt{", "कीर्ति"],
  ["k\"j{", "पूर्व"],
  [";j{f]Rr", "सर्वोच्च"],
  [";j{f]Rr cbfnt, g]kfn.", "सर्वोच्च अदालत, नेपाल।"],
  ["lgb{]lzsf", "निर्देशिका"],
  ["Ifltk\"lt{", "क्षतिपूर्ति"],
  // letters typed as consonant + aa (ण, ष, क्ष)
  ["u0f]z", "गणेश"],
  ["C0f", "ऋण"],
  ["aofg", "बयान"],
  ["Ifdf", "क्षमा"],
  // conjunct glyphs from the high half of the font
  ["1fg", "ज्ञान"],
  [">d", "श्रम"],
  ["cfkm\\gf]", "आफ्नो"],
  ["km};nf", "फैसला"],
  ["eQm", "भक्त"],
  ["6«]S;", "ट्रेक्स"],
  ["åf/f", "द्वारा"],
  // digits are typed on the shifted number row; "." is the danda
  ["@)*@", "२०८२"],
  ["!@#", "१२३"],
  ["cy{.", "अर्थ।"],
];

test.describe("Preeti -> Unicode", () => {
  for (const [preeti, unicode] of PAIRS) {
    test(`${preeti} -> ${unicode}`, () => {
      expect(preetiToUnicode(preeti)).toBe(unicode);
    });
  }

  test("has at least 20 pairs", () => {
    expect(PAIRS.length).toBeGreaterThanOrEqual(20);
  });

  test("empty and non-Preeti input is left alone", () => {
    expect(preetiToUnicode("")).toBe("");
    expect(preetiToUnicode(" \n\t")).toBe(" \n\t");
    expect(preetiToUnicode("नेपाल")).toBe("नेपाल"); // already Unicode
  });

  test("a stray reph marker does not crash", () => {
    expect(preetiToUnicode("{")).toBe("र्");
  });
});
