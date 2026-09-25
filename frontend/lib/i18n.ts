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
};

export const strings: Record<Lang, Strings> = {
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
  },
};
