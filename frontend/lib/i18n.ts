export type Lang = "en" | "ne";

export const strings: Record<Lang, Record<string, string>> = {
  en: {
    appName: "Kanooni Sathi",
    tagline: "Your bilingual legal friend for Nepali law",
    placeholder: "Describe what's going on, in your own words...",
    send: "Send",
    thinking: "Thinking...",
    disclaimerBanner:
      "Kanooni Sathi gives general legal information for educational purposes. It is not a substitute for a licensed advocate.",
    sourcesLabel: "Based on",
    emptyState:
      "Tell me what's happening — a landlord dispute, a marriage problem, an unpaid debt, anything. I'll explain your options in plain language.",
    langToggle: "नेपाली",
    fallbackNotice:
      "AI model not configured on this server — showing matched legal passages directly.",
  },
  ne: {
    appName: "कानूनी साथी",
    tagline: "नेपाली कानूनका लागि तपाईंको दुईभाषी कानूनी साथी",
    placeholder: "आफ्नै भाषामा आफ्नो समस्या लेख्नुहोस्...",
    send: "पठाउनुहोस्",
    thinking: "सोच्दैछु...",
    disclaimerBanner:
      "कानूनी साथीले शैक्षिक उद्देश्यले सामान्य कानूनी जानकारी प्रदान गर्छ। यो इजाजतपत्रप्राप्त अधिवक्ताको सल्लाहको विकल्प होइन।",
    sourcesLabel: "आधार",
    emptyState:
      "घरभेटासँगको विवाद, वैवाहिक समस्या, नतिरेको ऋण, जे भए पनि मलाई भन्नुहोस्। म सजिलो भाषामा तपाईंका विकल्पहरू बुझाउँला।",
    langToggle: "English",
    fallbackNotice:
      "यस सर्भरमा AI मोडेल कन्फिगर छैन — मिल्दो कानूनी अंशहरू सिधै देखाइन्छ।",
  },
};
