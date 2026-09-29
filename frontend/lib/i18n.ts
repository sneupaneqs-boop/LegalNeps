import { extraEn, extraNe } from "./i18n-extra";

export type Lang = "en" | "ne";

type Strings = {
  appName: string;
  tagline: string;
  placeholder: string;
  send: string;
  thinking: string;
  disclaimerBanner: string;
  sourcesLabel: string;
  emptyState: string;
  langToggle: string;
  fallbackNotice: string;
  badgeLaw: string;
  badgePrecedent: string;
  officialSource: string;
  tryAsking: string;
  suggestions: string[];
  error: string;
  timeout: string;
  navSearch: string;
  navChat: string;
  searchPlaceholder: string;
  searchButton: string;
  searchEmpty: string;
  searchNoResults: string;
  filterCategory: string;
  filterAllCategories: string;
  filterDocType: string;
  filterAllDocTypes: string;
  filterInForceOnly: string;
  filterIncludeBills: string;
  statusInForce: string;
  statusBill: string;
  statusUnknown: string;
  billWarning: string;
  unknownStatusNote: string;
  enactedLabel: string;
  amendedLabel: string;
  officialPdf: string;
  prevSection: string;
  nextSection: string;
  backToDoc: string;
  docTypeAct: string;
  docTypeRule: string;
  docTypeConstitution: string;
  docTypeOrder: string;
  docTypeDirective: string;
  docTypeTreaty: string;
  docTypeOther: string;
  signIn: string;
  signOut: string;
  emailPlaceholder: string;
  sendCode: string;
  codeSentTo: string;
  codePlaceholder: string;
  verifyCode: string;
  saveResearch: string;
  savedResearch: string;
  savedToResearch: string;
  navSaved: string;
  savedEmpty: string;
  signInToSave: string;
  deleteSaved: string;
  navPlaybooks: string;
  playbooksTitle: string;
  playbooksEmpty: string;
  factQuestionsLabel: string;
  provisionsLabel: string;
  evidenceLabel: string;
  forumLabel: string;
  limitationLabel: string;
  nextStepsLabel: string;
  backToPlaybooks: string;
  areaEmployment: string;
  areaTenancy: string;
  areaFamily: string;
  areaFinance: string;
  areaConsumer: string;
  areaCyber: string;
};

const baseStrings: Record<Lang, Strings> = {
  en: {
    appName: "Kanooni Sathi",
    tagline: "Your bilingual legal friend for Nepali law",
    placeholder: "Describe what's going on, in your own words...",
    send: "Send",
    thinking: "Reading the relevant laws and precedents...",
    disclaimerBanner:
      "Answers are grounded only in official sources (Nepal Law Commission and Supreme Court's Nepal Kanoon Patrika). General information, not a substitute for a licensed advocate.",
    sourcesLabel: "Official sources",
    emptyState:
      "Tell me what's happening — a landlord dispute, a marriage problem, an unpaid debt, a workplace issue, anything. I'll explain your options in plain language, citing the exact law.",
    langToggle: "नेपाली",
    fallbackNotice:
      "AI summary unavailable right now — showing the matching official provisions directly.",
    badgeLaw: "Law",
    badgePrecedent: "Precedent",
    officialSource: "Open official source",
    tryAsking: "Try asking:",
    suggestions: [
      "My landlord won't return my deposit. What can I do?",
      "How can a woman get citizenship for her child in Nepal?",
      "What is the punishment for child marriage?",
      "My employer hasn't paid my salary for 3 months.",
    ],
    error: "Something went wrong reaching the server. Please try again.",
    timeout: "The server is taking too long to respond (it may have been waking up). Please send your question again.",
    navSearch: "Search laws",
    navChat: "Ask a question",
    searchPlaceholder: "Search laws and precedents (e.g. deposit, divorce, cheque bounce)...",
    searchButton: "Search",
    searchEmpty: "Search Nepal's laws and Supreme Court precedents directly, browse by section, and open the official source.",
    searchNoResults: "No matches. Try different words, or ask the question in the chat instead.",
    filterCategory: "Type",
    filterAllCategories: "Law + precedent",
    filterDocType: "Document type",
    filterAllDocTypes: "All",
    filterInForceOnly: "In force only",
    filterIncludeBills: "Include draft bills",
    statusInForce: "In force",
    statusBill: "Draft bill — not yet law",
    statusUnknown: "Status not confirmed",
    billWarning: "This is a draft bill. It has not been passed and has no legal force yet.",
    unknownStatusNote: "We couldn't confirm this document's enactment date from its text — verify against the official source before relying on it.",
    enactedLabel: "Enacted",
    amendedLabel: "Amended by",
    officialPdf: "Open official PDF",
    prevSection: "Previous section",
    nextSection: "Next section",
    backToDoc: "Back to document",
    docTypeAct: "Act",
    docTypeRule: "Regulation",
    docTypeConstitution: "Constitution",
    docTypeOrder: "Order",
    docTypeDirective: "Directive",
    docTypeTreaty: "Treaty",
    docTypeOther: "Other",
    signIn: "Sign in",
    signOut: "Sign out",
    emailPlaceholder: "you@example.com",
    sendCode: "Send code",
    codeSentTo: "Code sent to",
    codePlaceholder: "6-digit code",
    verifyCode: "Verify",
    saveResearch: "Save",
    savedResearch: "Saved",
    savedToResearch: "Saved to your research",
    navSaved: "Saved",
    savedEmpty: "Nothing saved yet. Save an answer from the chat to find it here later.",
    signInToSave: "Sign in to save this answer for later.",
    deleteSaved: "Delete",
    navPlaybooks: "Action Plans",
    playbooksTitle: "Action Plans",
    playbooksEmpty: "No action plans available right now.",
    factQuestionsLabel: "Questions to think through",
    provisionsLabel: "Relevant law",
    evidenceLabel: "Evidence to gather",
    forumLabel: "Where to go",
    limitationLabel: "Time limit",
    nextStepsLabel: "Next steps",
    backToPlaybooks: "← All action plans",
    areaEmployment: "Employment",
    areaTenancy: "Tenancy",
    areaFamily: "Family",
    areaFinance: "Finance",
    areaConsumer: "Consumer",
    areaCyber: "Cyber",
  },
  ne: {
    appName: "कानूनी साथी",
    tagline: "नेपाली कानूनका लागि तपाईंको दुईभाषी कानूनी साथी",
    placeholder: "आफ्नै भाषामा आफ्नो समस्या लेख्नुहोस्...",
    send: "पठाउनुहोस्",
    thinking: "सम्बन्धित कानून र नजिर पढ्दैछु...",
    disclaimerBanner:
      "जवाफ नेपाल कानून आयोग र सर्वोच्च अदालतको नेपाल कानून पत्रिकाका आधिकारिक स्रोतमा मात्र आधारित छन्। यो सामान्य जानकारी हो, इजाजतपत्रप्राप्त अधिवक्ताको सल्लाहको विकल्प होइन।",
    sourcesLabel: "आधिकारिक स्रोत",
    emptyState:
      "घरबहाल विवाद, वैवाहिक समस्या, नतिरेको ऋण, कामदारको पारिश्रमिक, जे भए पनि मलाई भन्नुहोस्। म सजिलो भाषामा, सम्बन्धित कानूनको दफासहित तपाईंका विकल्पहरू बुझाउँला।",
    langToggle: "English",
    fallbackNotice: "AI सारांश अहिले उपलब्ध छैन — मिल्दो आधिकारिक कानुनी प्रावधान सिधै देखाइन्छ।",
    badgeLaw: "कानून",
    badgePrecedent: "नजिर",
    officialSource: "आधिकारिक स्रोत हेर्नुहोस्",
    tryAsking: "यस्तो सोध्न सक्नुहुन्छ:",
    suggestions: [
      "घरबेटीले धरौटी फिर्ता दिएन, म के गर्न सक्छु?",
      "सम्बन्ध विच्छेद गर्दा अंश कसरी पाइन्छ?",
      "बाल विवाह गरेमा के सजाय हुन्छ?",
      "कम्पनीले तीन महिनादेखि तलब दिएको छैन।",
    ],
    error: "सर्भरसँग जडान गर्दा समस्या भयो। कृपया फेरि प्रयास गर्नुहोस्।",
    timeout: "सर्भरले जवाफ दिन धेरै समय लगायो (सर्भर भर्खरै सुरु हुँदै थियो होला)। कृपया प्रश्न फेरि पठाउनुहोस्।",
    navSearch: "कानून खोज्नुहोस्",
    navChat: "प्रश्न सोध्नुहोस्",
    searchPlaceholder: "कानून र नजिर खोज्नुहोस् (जस्तै: धरौटी, सम्बन्ध विच्छेद, चेक बाउन्स)...",
    searchButton: "खोज्नुहोस्",
    searchEmpty: "नेपालको कानून र सर्वोच्च अदालतका नजिरहरू सिधै खोज्नुहोस्, दफा अनुसार हेर्नुहोस्, र आधिकारिक स्रोत खोल्नुहोस्।",
    searchNoResults: "कुनै मिल्दो नतिज्जा फेला परेन। अर्को शब्द प्रयोग गर्नुहोस्, वा च्याटमा प्रश्न सोध्नुहोस्।",
    filterCategory: "प्रकार",
    filterAllCategories: "कानून + नजिर",
    filterDocType: "कागजातको किसिम",
    filterAllDocTypes: "सबै",
    filterInForceOnly: "हाल लागू कानून मात्र",
    filterIncludeBills: "विधेयक पनि देखाउनुहोस्",
    statusInForce: "हाल लागू",
    statusBill: "विधेयक — अझै कानून बनेको छैन",
    statusUnknown: "स्थिति पुष्टि भएको छैन",
    billWarning: "यो एउटा विधेयक हो। यो अझै पारित भएको छैन र हाल कानूनी मान्यता छैन।",
    unknownStatusNote: "यस कागजातको प्रमाणीकरण मिति यसको पाठबाट पुष्टि गर्न सकिएन — भर पर्नुअघि आधिकारिक स्रोतमा जाँच गर्नुहोस्।",
    enactedLabel: "प्रमाणीकरण मिति",
    amendedLabel: "संशोधन गर्ने ऐन",
    officialPdf: "आधिकारिक PDF खोल्नुहोस्",
    prevSection: "अघिल्लो दफा",
    nextSection: "अर्को दफा",
    backToDoc: "कागजातमा फर्कनुहोस्",
    docTypeAct: "ऐन",
    docTypeRule: "नियमावली",
    docTypeConstitution: "संविधान",
    docTypeOrder: "आदेश",
    docTypeDirective: "निर्देशिका",
    docTypeTreaty: "सन्धि",
    docTypeOther: "अन्य",
    signIn: "साइन इन",
    signOut: "साइन आउट",
    emailPlaceholder: "you@example.com",
    sendCode: "कोड पठाउनुहोस्",
    codeSentTo: "कोड यहाँ पठाइयो:",
    codePlaceholder: "६ अंकको कोड",
    verifyCode: "प्रमाणित गर्नुहोस्",
    saveResearch: "सेभ गर्नुहोस्",
    savedResearch: "सेभ गरिएको",
    savedToResearch: "तपाईंको अनुसन्धानमा सेभ भयो",
    navSaved: "सेभ गरिएका",
    savedEmpty: "अहिलेसम्म केही सेभ गरिएको छैन। पछि यहाँ भेट्टाउन च्याटबाट कुनै जवाफ सेभ गर्नुहोस्।",
    signInToSave: "यो जवाफ पछिका लागि सेभ गर्न साइन इन गर्नुहोस्।",
    deleteSaved: "मेटाउनुहोस्",
    navPlaybooks: "कार्य योजना",
    playbooksTitle: "कार्य योजनाहरू",
    playbooksEmpty: "अहिले कुनै कार्य योजना उपलब्ध छैन।",
    factQuestionsLabel: "विचार गर्नुपर्ने प्रश्नहरू",
    provisionsLabel: "सम्बन्धित कानून",
    evidenceLabel: "जुटाउनुपर्ने प्रमाण",
    forumLabel: "कहाँ जाने",
    limitationLabel: "समय सीमा",
    nextStepsLabel: "अर्को कदम",
    backToPlaybooks: "← सबै कार्य योजना",
    areaEmployment: "रोजगारी",
    areaTenancy: "घरबहाल",
    areaFamily: "पारिवारिक",
    areaFinance: "वित्तीय",
    areaConsumer: "उपभोक्ता",
    areaCyber: "साइबर",
  },
};

export const strings: Record<Lang, Strings & typeof extraEn> = {
  en: { ...baseStrings.en, ...extraEn },
  ne: { ...baseStrings.ne, ...extraNe },
};
