"""Romanised-Nepali / English -> formal statute-Nepali legal lexicon.

The corpus is Devanagari only, so a message typed as "boss le din ko 12 ghanta
kaam garauchha, overtime ko paisa pani dinna" shares no token with the Labour
Act. This module is the deterministic (no LLM, no network) bridge: a curated
lexicon of roman spellings -> the formal Devanagari terms the statutes use,
matched tolerantly (aa/a, sh/s, w/v/b, chh/ch, doubled letters, dropped
aspirates, postpositions like -le/-ko/-lai/-ma glued to the word).

Every Devanagari target must exist in the search index vocabulary
(tests/test_translit.py checks this against get_index().vocab), every law
title must be an exact corpus title, and generic words (paisa, kaam, ghar) are
never keys on their own: "weak" entries only contribute when a strong entry
also matched.

Lexicon line format (one entry per line, fields separated by " ; "):
    S|W ; roman variants (|-separated) ; Devanagari targets (|-separated) [; law titles (|-separated)]
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

# exact corpus titles (validated by tests/test_translit.py)
_LAW = {
    "LAB": "श्रम ऐन, २०७४",
    "FE": "वैदेशिक रोजगार ऐन, २०६४",
    "CIV": "मुलुकी देवानी संहिता, २०७४",
    "CIVP": "मुलुकी देवानी कार्यविधि संहिता, २०७४",
    "CRIM": "मुलुकी अपराध संहिता, २०७४",
    "CRIMP": "मुलुकी फौजदारी कार्यविधि संहिता, २०७४",
    "DV": "घरेलु हिंसा (कसूर र सजाय) ऐन, २०६६",
    "RTI": "सूचनाको हक सम्बन्धी ऐन, २०६४",
    "SEC": "धितोपत्र सम्बन्धी ऐन, २०६३",
    "COMP": "कम्पनी ऐन, २०६३",
    "VAT": "मूल्य अभिवृद्धि कर ऐन, २०५२",
    "ITX": "आयकर ऐन, २०५८",
    "NEG": "विनिमेय अधिकारपत्र ऐन, २०३४",
    "BANKOFF": "बैङ्किङ्ग कसूर तथा सजाय ऐन, २०६४",
    "CONS": "उपभोक्ता संरक्षण ऐन, २०७५",
    "ETA": "विद्युतीय (इलेक्ट्रोनिक) कारोबार ऐन, २०६३",
    "MAL": "मालपोत ऐन, २०३४",
    "MV": "सवारी तथा यातायात व्यवस्था ऐन, २०४९",
    "CIT": "नेपाल नागरिकता ऐन, २०६३",
    "COOP": "सहकारी ऐन, २०७४",
    "CORR": "भ्रष्टाचार निवारण ऐन, २०५९",
    "BONUS": "बोनस ऐन, २०३०",
    "SHH": "कार्यस्थलमा हुने यौनजन्य दुर्व्यवहार ( निवारण) ऐन, २०७१",
}

# S = strong (specific, safe alone), W = weak (generic: only alongside a strong hit)
_LEXICON = """
S ; talab|talabh|tallab|salary|salaries|wage|wages|jyala|jyaala|paritramik|paaritramik|pariswamik ; पारिश्रमिक|तलब|ज्याला ; LAB
S ; ghanta kaam|ghanta ko kaam|ghanta duty|working hours|work hours|duty hours|hours of work|kaam ko samay|kam ko samay ; कार्य घण्टा|दैनिक कार्य समय|अतिरिक्त समय ; LAB
S ; overtime|over time|ovartime|obhartime|extra kaam|thap kaam|thap samay ; अतिरिक्त समय|अतिरिक्त समयको पारिश्रमिक ; LAB
S ; barkhasta|barkhast|terminated|termination|kaam bata nikalyo|kaam bata nikaalyo|job bata nikalyo|nikaaldiyo kaam bata|kaam bata hataayo|kaam bata hatayo ; बर्खास्त|सेवाबाट हटाउने|सेवा समाप्त ; LAB
S ; rajinama|rajinaama|rajinamaa|resign|resigned|resignation ; राजिनामा|सेवाबाट राजिनामा ; LAB
S ; gratuity|upadan|upadaan|upadhan ; उपदान ; LAB
S ; provident fund|sanchaya kosh|sanchay kosh|pf ; सञ्चय कोष|कर्मचारी सञ्चय कोष ; LAB
S ; bonus ; बोनस ; BONUS
S ; prasuti bida|prasuti bidaa|maternity leave|prasooti bida ; प्रसूति बिदा|बिदा ; LAB
S ; sick leave|birami bida|birami ko bida|beramee bida|ghar bida ; बिदा|बिरामी बिदा ; LAB
S ; majdur|majdoor|mazdur|mazdoor|kamdar|kaamdar|worker|workers|shramik|sramik|employee|employees ; कामदार|श्रमिक|रोजगारदाता ; LAB
S ; boss|employer|rojgardata|rojgaardata|sheth|seth|thekedar|malik le kaam ; रोजगारदाता|कामदार ; LAB
S ; labour office|labor office|shram karyalaya|sram karyalaya ; श्रम कार्यालय|श्रम अदालत ; LAB
S ; labour court|labor court|shram adalat|sram adalat ; श्रम अदालत ; LAB
S ; trade union|majdur sangh|majdoor sangh|shramik sangathan ; ट्रेड युनियन|ट्रेड युनियन अधिकार ; LAB
S ; manpower|man power|manpauar|manpawar|manpower company|manpower agency|recruiting agency ; वैदेशिक रोजगार|म्यानपावर|वैदेशिक रोजगार व्यवसायी ; FE
S ; videsh|bidesh|abroad|foreign employment|baidesik rojgar|baideshik rojgar|kuwait|malaysia|qatar|saudi|dubai|uae|oman|bahrain|lebanon|israel|korea|gulf|khadi ; वैदेशिक रोजगार|वैदेशिक रोजगार विभाग ; FE
S ; visa|bhisa|visaa|bisa ; भिसा|वैदेशिक रोजगार ; FE
S ; thagyo|thagi|thagne|thagera|thagiyo|thagiyo|thagna|dhoka|dhokha|dhoka diyo|fraud|cheat|cheated|cheating|scam|scammed|fraudulent ; ठगी|ठगी गर्ने ; CRIM
S ; sasu sasura|sasu|sasura|in laws|in-laws|inlaws|sasurali ; सासू ससुरा|सासू|ससुरा ; CIV
S ; ansha|ansh|anshabanda|ansabanda|ansh banda|angsha|angsa|anshiyar|angshabanda|hissa|hisssa|share of property ; अंश|अंशबण्डा|अंशियार ; CIV
S ; bidhwa|bidhuwa|bidhwaa|widow|vidhwa ; विधवा|पति|सम्पत्ति ; CIV
S ; shreeman|shriman|shreemaan|shrimaan|shrimaan|pati|patiko|husband ; पति ; CIV
S ; shreemati|shrimati|srimati|shreematee|patni|swasni|swasnee|wife ; पत्नी ; CIV
W ; sampatti|sampati|sampatti ko|property|properties ; सम्पत्ति
W ; haq|hak|adhikar|adhikaar|right|rights ; हक|अधिकार
W ; mrityu|mritu|mrtyu|nidhan|death|died|dekhant|marechha|marecha ; मृत्यु
W ; chora|chhora|chhoro|choro|son|sons|chhori|chhoree|daughter|daughters|santan|santaan|bachha|bachcha|bachchha|bachhaa|children|kids ; छोरा|छोरी|सन्तान|बालबालिका
S ; bibaha|biwaha|biha|bihe|bibah|vivah|marriage|married ; विवाह ; CIV
S ; sautini|sauta|sautani|sautin|dosro bibaha|dosro biha|dosro biwaha|second marriage|bahubibaha|bahu bibaha|bahubiwaha ; बहुविवाह|दोस्रो विवाह ; CRIM
S ; sambandha bichhed|sambandh bichhed|sambandha bichchhed|sambandh bicched|sambandha bicched|sambandha bicchhed|bichhed|divorce|divorced|chhodpatra|chodpatra|talak|talaq|chhutta bhutta ; सम्बन्ध विच्छेद|सम्बन्ध विच्छेद मञ्जुरी ; CIV
S ; kutpit|kutpeet|kutai|kuteko|kutyo|kutera|marpit|marpeet|beat|beaten|beating|beats ; कुटपिट|कुटपिट वा अंग भङ्ग|शारीरिक हिंसा ; CRIM
S ; daijo|daijo maagyo|dahej|dowry|daaijo ; दाइजो|दाइजो माग्ने ; CRIM
S ; ghar kharcha|kharcha dinna|kharcha nadine|kharch dinna|bharanposhan|bharan poshan|bharnposhan|maintenance|alimony|bhattha ; भरणपोषण|खर्च ; CIV
S ; ghareloo hinsa|gharelu hinsa|ghareluhinsa|domestic violence|hinsa ; घरेलु हिंसा|हिंसा ; DV
S ; custody|sarankshan|sanrakshan|abhibhawak|abhibhabak|guardian ; संरक्षकत्व|संरक्षण|बालबालिका ; CIV
S ; dattak|dattak putra|adoption|adopt|adopting ; धर्मपुत्र|धर्मपुत्री|धर्मपुत्रको ; CIV
S ; jagga|jaggaa|jamin|jaminn|zamin|jaggajamin|jagga jamin|land|plot|ropani|bigha|kattha|kaththa ; जग्गा|घर जग्गा ; MAL
S ; lalpurja|lal purja|lalpurza|lalpurja haru|jagga dhani|jaggadhani|jaggadhani purja|land ownership certificate ; जग्गाधनी प्रमाणपुर्जा|प्रमाणपुर्जा ; MAL
S ; malpot|malpoth|malpot karyalaya|land revenue office ; मालपोत|मालपोत कार्यालय ; MAL
S ; naamsari|namsari|namasari|naamsaari|nam sari|ownership transfer ; नामसारी|जग्गा नामसारी ; MAL
S ; rajinama pass|rajinama garne|rajinamaa pass|rajinama lekhne|sale deed ; राजीनामा|राजीनामा पास|रजिष्ट्रेशन ; CIV
S ; sarkari jagga|sarkari jaggaa|ailani|parti jagga|guthi jagga|guthi ; सरकारी जग्गा|ऐलानी|पर्ती|गुठी ; MAL
S ; mohi|mohiyani|mohiyani haq|tenant farmer|kisan mohi ; मोही|मोहीयानी हक ; MAL
S ; sima|simana|sim ana|boundary|hadbandi|sandhiyar|sandhiyarko jagga|chhimeki ; सिमाना|हदबन्दी|साँध|सिमाना ; CIV
S ; ghar bahal|ghar bhada|ghar bhaada|kotha bhada|room rent|house rent|bahal|bahalma|bahalwala|bahaalwala|derawal|dera wal|tenant|tenants ; घर बहाल|बहाल|बहालवाला|भाडा ; CIV
S ; gharbeti|gharbetti|gharbeti le|ghardhani|ghar dhani|landlord|makan malik|makanmalik|house owner ; घरधनी ; CIV
S ; deposit|dharauti|dharauta|dharautee|dharaut|security deposit|advance rent ; धरौटी|अग्रिम ; CIV
S ; jamanat|jamanata|zamanat|bail|bail lidaina|jamanat rakhera|dharauti rakhera|dharauti jamanat ; जमानत|धरौटी|थुनामा ; CRIMP
S ; suchanako hak|suchana ko hak|suchana hak|suchna ko hak|sucahnako hak|sucahna ko hak|soochanako hak|rti|right to information|suchana adhikari|suchana mangeko ; सूचनाको हक|सूचना अधिकारी|राष्ट्रिय सूचना आयोग ; RTI
S ; punarabedan|punarawedan|punaravedan|punarbedan|appeal|appeals|appeal garne ; पुनरावेदन|उजुरी ; CIVP
S ; ujuri|ujurii|ujoori|complaint|complain|complaints|shikayat|shikayet ; उजुरी|उजुरी दिने ; CIVP
S ; gunaso|gunaaso|gunasoo ; गुनासो|उजुरी
W ; darta|dartaa|registration|register|registered|registrar ; दर्ता
W ; jawaf|jawab|jabab|jabaf|reply|response ; जवाफ
W ; mudda|muddha|muddaa|mukadama|mukaddama|muddamamila|case|cases ; मुद्दा|अदालत
W ; adalat|adaalat|court|kachahari|kachari ; अदालत
S ; jilla adalat|zilla adalat|district court ; जिल्ला अदालत ; CIVP
S ; jaheri|jaheri darkhast|jahiri|jahery|jaheri dinu|fir|f i r|first information report|police complaint|police report|jaherikarta ; जाहेरी दरखास्त|जाहेरी|प्रहरी ; CRIMP
W ; police|prahari|praharee|pulis ; प्रहरी
S ; pakrau|pakraau|pakriyo|pakrayo|pakreko|pakrauchha|arrest|arrested|arrests|thuna|thunama|thunaama|hiraasat|hirasat|remand|rimand ; पक्राउ|थुना|थुनुवा ; CRIMP
W ; sajaya|sajay|sazaya|saja|jail|karagar|kaid|sentence ; सजाय|कैद
S ; jariwana|jarimana|jaribana|dandajarimana ; जरिवाना|सजाय ; CRIM
S ; hadmyad|hadmyaad|hadmiyad|limitation|time limit|time bar ; हदम्याद ; CIVP
W ; sabut|saboot|proof|evidence|praman ; प्रमाण|सबुद
W ; company|kampani|kampanee|pvt ltd|private limited|private company|public company|limited company ; कम्पनी|कम्पनी दर्ता
S ; company darta|kampani darta|company register|kampani register|company registration|kampani registration|register garna|company registrar ; कम्पनी दर्ता|कम्पनी रजिस्ट्रार|प्रवर्तक ; COMP
S ; shareholder|shareholders|share holder|sheyardhani|sheyar dhani|sherdhani|shareholder le ; शेयरधनी|सेयरधनी ; COMP
S ; agm|annual general meeting|sadharan sabha|saadharan sabha|shadharan sabha|saadharan sava ; साधारणसभा|वार्षिक साधारणसभा ; COMP
S ; share|shares|sheyar|sher|stock|stocks ; शेयर|सेयर|धितोपत्र ; SEC
S ; dhitopatra|dhitoptra|dhito patra|securities|sebon|nepse|ipo|broker|brokers|mutual fund ; धितोपत्र|धितोपत्र बोर्ड|धितोपत्र दलाल ; SEC
S ; dhito|dhito rakhera|collateral|mortgage|bandhaki|bandhak|bandhaki rakhera|dhitopatra bandhak ; धितो|बन्धक|धितो बन्धक ; CIV
S ; insider|insider trading|bhitri suchana|bhitri karobar|bhitri karobar|bhitree suchana|bhitri jankari ; भित्री कारोबार|भित्री सूचना|धितोपत्र ; SEC
S ; cheque|cheques|chek|cheek|cheque bounce|check bounce|cheque bouncing|dishonour|dishonor|bounced|bounce|chek bounce|cheque fail|cheque return ; चेक अनादर|चेक|विनिमेय अधिकारपत्र ; BANKOFF|NEG
S ; byaj|byaaj|bayaj|byaz|interest|byaj dar|byajdar|byaj ko dar|sud|byajko ; ब्याज|ब्याजदर ; CIV
S ; penal interest|late payment|delay payment|late fee|penalty interest|pheri byaj ; ब्याज|जरिवाना|थप ब्याज
S ; rin|rinn|karja|karjaa|kaarja|loan|loans|rin liyeko|karja liyeko ; कर्जा|ऋण ; CIV
S ; sahu|sahuji|moneylender|money lender|lender|byajwala|sudkhor ; साहु|साहुको ब्याज ; CIV
S ; udhar|udhaar|udharo|sapati|sapaati|paisa liyeko|paisa lieko|paisa maagyo ; सापटी|ऋण|लेनदेन ; CIV
S ; lekhat|likhat|likhit|dastakhat|dastkhat|sahichhap|sahi chhap|signature ; लिखत|सहीछाप|दस्तखत ; CIV
S ; sambidhan|samvidhan|samvidhaan|constitution ; संविधान
S ; nagarikta|nagrikta|nagarikata|nagarita|citizenship|nagarikta pramanpatra ; नागरिकता|नागरिकताको प्रमाणपत्र ; CIT
S ; naam thar|nam thar|naam ra thar|name correction|naam sachyaune|umer sachyaune|janma miti ; नाम थर|जन्म मिति|उमेर ; CIT
S ; bima|bimaa|beema|insurance|premium|bima company ; बीमा|बीमक|बीमालेख
S ; durghatana|dhurghatana|durghatna|accident|accidents|hit and run|hit garera|thokyo|thokkar|thokar ; दुर्घटना|सवारी दुर्घटना|ठक्कर ; MV
S ; ghaite|ghaate|injured|chot lagyo|chot|injury ; घाइते|चोटपटक|क्षतिपूर्ति ; CRIM
S ; driver|chalak|dhrayver|drayvar|driver bhagyo ; सवारी चालक|चालक ; MV
S ; muabja|muaabja|muabjaa|compensation|kshatipurti|khatipurti|harjana|harjaana ; क्षतिपूर्ति|मुआब्जा|हर्जाना
S ; bike|motorbike|motorcycle|scooter|scooty|bus|truck|tempo|microbus|gadi|gaadi|sawari|sabari|vehicle ; सवारी साधन|सवारी|मोटरसाइकल ; MV
S ; driving license|driving licence|driving lisence|driving lisans|driver license|driver licence ; सवारी चालक अनुमतिपत्र|इजाजतपत्र ; MV
S ; doctor|daktar|dactar|doktor|dr|physician|nurse|hospital|aspatal|aspataal|clinic ; चिकित्सक|स्वास्थ्यकर्मी|उपचार
S ; galat operation|galat ilaj|galat upachar|galat treatment|operation|opreshan|surgery|medical negligence|laparwahi|laparbahi|lapar ; लापरबाही गरी मृत्यु गराएमा|उपचारमा लापरबाही|मृत्यु ; CRIM
S ; facebook|fb|instagram|tiktok|whatsapp|messenger|twitter|youtube|social media ; विद्युतीय माध्यम|सामाजिक सञ्जाल|विद्युतीय कारोबार ; ETA
S ; hack|hacked|hacking|hacker|cyber|cyber crime|cybercrime|online fraud|online thagi ; साइबर|कम्प्युटर|विद्युतीय कारोबार ; ETA
S ; fake id|fake account|fake profile|nakali id|nakkali id|nakali account|fake facebook id|fake facebook ; नक्कली|विद्युतीय माध्यम|विद्युतीय कारोबार ; ETA|CRIM
S ; abusive|abusive message|abusive messages|gali|gaali|gali gareko|dhamki|dhamkee|threat|threats|blackmail ; गाली बेइज्जती|धम्की|अपमान ; ETA|CRIM
S ; badnam|badnami|badnaam|jhutho|jhuto|jhutto|defame|defamation|bejjat|bejjati|izzat|ijjat|maanhani|manhani|apaman|apamaan|insult ; बदनाम|इज्जत|अपमान|झुटो ; CRIM
S ; grahak|grahakko|consumer|customer ; उपभोक्ता|उपभोक्ता संरक्षण ; CONS
S ; nakali|nakkali|nakli|fake|duplicate|expiry|expired|kharab|kharaab|defective|damaged|faulty ; नक्कली|गुणस्तर|उपभोक्ता ; CONS
S ; online order|online shopping|order gareko|daraz|e commerce|ecommerce|e-commerce|sellhub ; इ-कमर्स|उपभोक्ता|विद्युतीय कारोबार ; CONS
S ; minimum balance|min balance|balance nabhayeko|balance nabhaeko ; न्यूनतम मौज्दात|खाता|एकीकृत निर्देशन|बैंक
S ; bank|banks|bfi|nrb|rastra bank|atm|debit card|credit card ; बैंक|वित्तीय संस्था|एकीकृत निर्देशन
W ; khata|khataa|account|accounts ; खाता
S ; sahakari|sahakaari|cooperative|cooperatives|co-operative|bachat sahakari|saving cooperative|savings cooperative ; सहकारी|सहकारी संस्था|निक्षेप ; COOP
S ; laghubitta|laghu bitta|laghubita|microfinance|finance company ; लघुवित्त|वित्तीय संस्था
S ; vat|bhat|bhyat|value added tax ; मूल्य अभिवृद्धि कर|भ्याट ; VAT
S ; income tax|aayakar|aaykar|ayakar|tds|tax|taxes ; आयकर|कर ; ITX
S ; pan number|pan no|permanent account number ; स्थायी लेखा नम्बर|आयकर ; ITX
S ; ghus|ghush|ghoos|bribe|bribery|rishwat|ghus khayo|ghus maagyo ; घूस|रिसवत|भ्रष्टाचार ; CORR
S ; rape|balatkar|jabarjasti|jabardasti|jbrjsti ; जबरजस्ती करणी|बलात्कार ; CRIM
S ; chhedchhad|chedchhad|chhedchhad garyo|sexual harassment|yaun durbyabahar|yaun hinsa|harassment at work|workplace harassment ; यौनजन्य दुर्व्यवहार|कार्यस्थल ; SHH
S ; satauna|satauchhan|sataunchhan|satayo|sataucha|sataucchan|torture|yatana|yatna|harass|harassing ; यातना|सताउने|दुर्व्यवहार ; DV
S ; chori|chorii|chori bhayo|chori garyo|steal|stole|stolen|theft|lutpat|loot|dakaiti|dakaity|robbery|lutera|chorayo|choryo ; चोरी|डकैती|लुटपाट ; CRIM
S ; hatya|murder|jyan marne|jyan mareko|jyanmara|killed ; ज्यान मार्ने|हत्या ; CRIM
S ; ward office|ward karyalaya|ward|nagarpalika|gaunpalika|municipality|palika|rural municipality|sifaris|sifarish|sipharis ; वडा कार्यालय|स्थानीय तह|सिफारिस
S ; nyayik samiti|judicial committee|melmilap|mel milap|mediation|mediator|sulah ; न्यायिक समिति|मेलमिलाप|मध्यस्थता
"""


@dataclass(frozen=True)
class Entry:
    strong: bool
    keys: tuple[str, ...]
    terms: tuple[str, ...]
    laws: tuple[str, ...]


def _parse() -> tuple[Entry, ...]:
    out = []
    for line in _LEXICON.strip().splitlines():
        parts = [p.strip() for p in line.split(" ; ")]
        if len(parts) < 3:
            continue
        laws = tuple(_LAW[k] for k in parts[3].split("|")) if len(parts) > 3 and parts[3] else ()
        out.append(Entry(parts[0] == "S", tuple(k.strip() for k in parts[1].split("|") if k.strip()),
                         tuple(t.strip() for t in parts[2].split("|") if t.strip()), laws))
    return tuple(out)


ENTRIES: tuple[Entry, ...] = _parse()

# ordinary English words that must never be fuzzy-matched onto a roman key
_COMMON_EN = {"what", "when", "where", "which", "while", "with", "that", "this", "these", "those", "there",
              "then", "than", "them", "they", "their", "have", "will", "would", "could", "should", "about",
              "after", "before", "under", "over", "does", "done", "make", "made", "take", "took", "give",
              "gave", "know", "need", "want", "long", "much", "many", "very", "also", "only", "same",
              "such", "some", "from", "into", "onto", "upon", "each", "every", "other", "another",
              "person", "people", "nepal", "nepali", "legal", "state", "public", "national", "general",
              "official", "language", "house", "procedure", "process", "system", "order", "rules", "rule"}

_SUFFIXES = ("haruko", "harule", "haruma", "harulai", "haru", "bata", "sanga", "sita", "dekhi", "samma",
             "le", "lai", "ko", "ka", "ki", "ma")


def canon(word: str) -> str:
    """Spelling-tolerant form of a roman word: sh->s, w/v->b, z->j, ph/f->p,
    aa/ee/ii/oo/uu -> single vowel, doubled consonants collapsed. Keeps chh vs
    ch (chori theft vs chhori daughter) - see loose()."""
    w = re.sub(r"[^a-z]", "", word.lower())
    w = w.replace("chh", "C").replace("sh", "s").replace("ph", "p")
    w = w.translate(str.maketrans({"w": "b", "v": "b", "z": "j", "f": "p", "q": "k"}))
    w = re.sub(r"aa+", "a", w)
    w = re.sub(r"ee+|ii+", "i", w)
    w = re.sub(r"oo+|uu+", "u", w)
    w = re.sub(r"([a-zC])\1+", r"\1", w)
    return re.sub(r"ey$", "e", w)


def loose(word: str) -> str:
    """Even looser: chh==ch and trailing vowels dropped (dharauti/dharauta). Used only when the strict form matched nothing, and only for words
    long enough that a collision is unlikely."""
    w = canon(word).replace("C", "c")
    w = re.sub(r"([a-z])\1+", r"\1", w)
    return re.sub(r"[aeiou]+$", "", w)


@lru_cache(maxsize=1)
def _tables():
    literal: dict[tuple[str, ...], list[int]] = {}
    strict: dict[tuple[str, ...], list[int]] = {}
    lenient: dict[tuple[str, ...], list[int]] = {}
    longest = 1
    for i, e in enumerate(ENTRIES):
        for key in e.keys:
            words = re.findall(r"[a-z]+", key.lower())
            if not words:
                continue
            longest = max(longest, len(words))
            literal.setdefault(tuple(words), []).append(i)
            strict.setdefault(tuple(canon(w) for w in words), []).append(i)
            lenient.setdefault(tuple(loose(w) for w in words), []).append(i)
    return literal, strict, lenient, longest


def _stem_variants(raw: str) -> list[str]:
    """The word itself, then with a glued Nepali postposition (-le/-ko/-lai/-ma
    ...) or English plural removed."""
    out = [raw]
    for suf in _SUFFIXES:
        if raw.endswith(suf) and len(raw) - len(suf) >= 3:
            out.append(raw[: -len(suf)])
    if raw.endswith("s") and len(raw) > 3:
        out.append(raw[:-1])
    return out


def _lookup(ws: list[str]) -> list[int] | None:
    """Entries for a word sequence. A literal spelling always matches. Fuzzy
    matching (canonical spelling, then the loosest form) is only trusted for
    longer words: short ones collide with common English words ("what" ~
    "bhat", "the" ~ "tha") and there is no spelling variety worth recovering
    in 3-4 letters."""
    literal, strict, lenient, _ = _tables()
    got = literal.get(tuple(ws))
    if got:
        return got
    letters = sum(len(w) for w in ws)
    if letters < 5 or any(w in _COMMON_EN for w in ws):
        return None
    got = strict.get(tuple(canon(w) for w in ws))
    if got:
        return got
    if letters >= 6:
        return lenient.get(tuple(loose(w) for w in ws))
    return None


def match(text: str) -> list[Entry]:
    """Lexicon entries hit by the Latin-script words of `text`, in order of
    appearance (longest phrase first at each position). Weak entries are only
    returned when at least one strong entry matched."""
    longest = _tables()[3]
    words = re.findall(r"[a-z]+", (text or "").lower())
    hits: list[int] = []
    i = 0
    while i < len(words):
        found = None
        for n in range(min(longest, len(words) - i), 0, -1):
            chunk = words[i:i + n]
            for last in _stem_variants(chunk[-1]):
                got = _lookup(chunk[:-1] + [last])
                if got:
                    found = (got, n)
                    break
            if found:
                break
        if found:
            hits.extend(found[0])
            i += found[1]
        else:
            i += 1
    seen: list[int] = []
    for h in hits:
        if h not in seen:
            seen.append(h)
    entries = [ENTRIES[h] for h in seen]
    if not any(e.strong for e in entries):
        return []
    return entries


def expand(text: str, max_terms: int = 14) -> list[str]:
    """Devanagari statute terms for the roman/English words in `text`
    (deduplicated, in order of appearance)."""
    out: list[str] = []
    for e in match(text):
        for t in e.terms:
            if t not in out:
                out.append(t)
    return out[:max_terms]


def laws(text: str, limit: int = 4) -> list[str]:
    """Exact corpus titles of the statutes the matched strong entries point to."""
    out: list[str] = []
    for e in match(text):
        if e.strong:
            for law in e.laws:
                if law not in out:
                    out.append(law)
    return out[:limit]


def strong_count(text: str) -> int:
    return sum(1 for e in match(text) if e.strong)
