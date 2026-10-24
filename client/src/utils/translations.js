/**
 * Stellar AI — UI String Translations
 * All static UI strings in English (en) and Hindi (hi).
 * Access via useT() hook from LanguageContext.
 */

export const translations = {
  en: {
    // ── Query Bar ──
    queryBarPrompts: [
      'Ask anything…',
      'Track a satellite orbit…',
      'Query ISS position…',
      'Find debris in LEO…',
      'Predict orbital decay…',
      'Analyse telemetry data…',
      'Search by NORAD ID…',
      'Check solar activity…',
    ],

    // ── Chat Header ──
    activeQuery: 'Active Query',
    about: 'About',

    // ── Chat Tabs ──
    tabAIAnalysis: 'AI Analysis',
    tabUploadedImage: 'Uploaded Image',
    tabOrbitalRadar: 'Orbital Radar',
    tabNORADTLE: 'NORAD TLE',

    // ── Chat Header Buttons ──
    saveNote: 'Save Note',
    share: 'Share',
    export: 'Export',
    regenerate: 'Regenerate',

    // ── Chat Messages ──
    you: 'You',
    stellarAI: 'Stellar AI',
    processingQuery: 'Processing satellite intelligence query…',
    attachedImagery: 'Attached Imagery',
    apiError: 'API Error:',

    // ── Follow-up bar ──
    followupPlaceholder: 'Ask a follow-up query or attach imagery…',
    followupLoadingPlaceholder: 'Processing query…',

    // ── Right Summary Panel ──
    querySummary: 'Query Summary',
    visual: 'Visual',
    rawData: 'Raw Data',
    confidenceScore: 'Confidence Score',
    classifiedTask: 'Classified Task',
    spatialDetections: 'Spatial Detections',
    regions: 'region(s)',
    pipelineStatus: 'Pipeline Status',
    processing: 'Processing…',
    error: 'Error',
    clarificationNeeded: 'Clarification Needed ⚠️',
    completed: 'Completed ✓',
    idle: 'Idle',
    relatedTopics: 'Related Topics & Tags',

    // ── Orbital Radar Tab ──
    agentSensorMetadata: 'Agent Sensor & Orbital Metadata',
    orbitalSensorSweep: 'Orbital Sensor Sweep',
    runQueryFirst: 'Run an AI Analysis query first to populate sensor metadata.',
    waitingAgent: 'Waiting for agent result…',
    taskType: 'Task Type',
    sensorMode: 'Sensor Mode',
    spectralPolarization: 'Spectral / Polarization',
    passMode: 'Pass Mode',
    offNadir: 'Off-Nadir Angle',
    confidence: 'Confidence',
    toolPipeline: 'Tool Pipeline',
    boundingBoxes: 'Bounding Boxes',
    noResultYet: 'No result yet',

    // ── TLE Tab ──
    liveNORADTLE: 'Live NORAD TLE Data',
    fetchingTLE: '// Fetching live TLE from Celestrak…',
    tleUnavailable: '// Click the NORAD TLE tab to fetch live data',

    // ── About Modal & Team ──
    aboutStellar: 'About Stellar AI',
    aboutDescription: 'Stellar AI is a state-of-the-art earth observation intelligence platform powered by a compiled LangGraph multi-agent orchestrator. It routes queries through specialist VQA, spatial grounding, change detection, and cross-modal SAR-optical fusion models.',
    teamName: 'Debugg Dynasty',
    teamTitle: 'Meet Team Debugg Dynasty',
    memberUditRole: 'Team Leader and AI & UI Lead',
    memberAadhyaRole: 'Researcher',
    memberAmanRole: 'Backend Lead',
    memberSwastikaRole: 'Visual Content Designer',
    memberAkashRole: 'Backend Dev',
    memberNishantRole: 'Frontend Dev',

    // ── Sidebar — Nav Labels ──
    navSearch: 'Search',
    navHistory: 'History',
    navKnowledge: 'Knowledge Base',
    navNotesDocs: 'Notes & Docs',
    navAbout: 'About & Team',
    navSettings: 'Settings',
    navProfile: 'Profile',

    // ── Sidebar — Settings ──
    systemPreferences: 'System Preferences',
    dopplerSync: 'Real-time Doppler Sync',
    highPrecisionTLE: 'High Precision TLE Calculation',

    // ── Sidebar — Profile ──
    missionOperator: 'Mission Operator',
    orbitalFlightDynamics: 'Orbital Flight Dynamics',
    signOut: 'Sign Out',

    // ── Sidebar — History Modal ──
    recentQueryHistory: 'Recent Query History',
    historySubheading: 'Select any past query to re-launch satellite intelligence',
    clearHistory: 'Clear History',
    searchHistoryPlaceholder: 'Search history by query keyword, NORAD ID, or mission tag...',
    launchQuery: 'Launch Query',
    noHistoryFound: 'No history entries found',
    clearSearchFilter: 'Try clearing your search filter or launch a new query!',

    // ── Sidebar — Notes Modal ──
    orbitNotesDocs: 'Orbit Notes & Documents',
    notesSubheading: 'Create custom research notes & save satellite imagery from AI queries',
    exportNotes: 'Export',
    newNote: 'New Note',
    cancel: 'Cancel',
    updateNote: 'Update Note',
    saveNote2: 'Save Note',
    noteTitlePlaceholder: 'Note Title (e.g. Cartosat-3 Solar Array Inspection)...',
    noteContentPlaceholder: 'Type your notes, orbital calculations, or satellite analysis observations...',
    attachDocument: 'Attach Document File (.pdf, .txt, .json, .csv, .docx)',
    attachImage: 'Add Image / Satellite Photo',
    searchNotesPlaceholder: 'Search saved notes by title, tag, document, or content...',
    allNotes: 'All Notes',
    noNotesYet: 'No notes created yet',
    noNotesHint: 'Click "+ New Note" to save satellite intelligence, telemetry, & documents!',

    // ── Notes Tags ──
    tagTelemetry: 'Telemetry',
    tagEarthScan: 'Earth Scan',
    tagDebrisRisk: 'Debris Risk',
    tagMissionLog: 'Mission Log',
    tagResearch: 'Research',
    tagGeneral: 'General',

    // ── Related Topics & Tech Chips ──
    topicSatelliteVQA: 'Satellite-VQA',
    topicISROAgent: 'ISRO-Agent',
    topicLangGraph: 'LangGraph',
    topicCartosat3: 'Cartosat-3',
    topicSentinel2: 'Sentinel-2',
    langGraphOrchestrated: 'LangGraph Orchestrated',
    isroCompliant: 'ISRO Compliant',
    liquidGlassUI: 'Liquid Glass UI',

    // ── Note Actions ──
    copyNoteText: 'Copy Note Text',
    editNoteTitle: 'Edit Note',
    deleteNoteTitle: 'Delete Note',
    closeModal: 'Close',

    // ── Translating indicator ──
    translating: 'Translating…',

    // ── Auth & Hero Screen ──
    brandBadge: 'Stellar AI Engine • Active',
    heroHeading: 'Autonomous Satellite Visual QA',
    heroSubtitle: 'Instantly query any Earth observation scene, STAC Sentinel-2 & Landsat-9 imagery, coordinates, or automated change detection through natural AI conversations.',
    telemetryStac: 'STAC Sentinel-2 & Landsat-9',
    telemetryIsro: 'ISRO Earth Observation',
    signInTab: 'Sign In',
    createAccountTab: 'Create Account',
    orbitalEmail: 'Orbital Email / Call sign',
    securityKey: 'Security Key',
    keepSessionActive: 'Keep session active',
    resetSecurityKey: 'Reset Security Key?',
    launchSession: 'Launch Session',
    authenticating: 'Authenticating...',
    accessGranted: '✓ Access Granted',
    orAuthenticateVia: 'or authenticate via',
    commanderName: 'Commander Name',
    createSecurityKey: 'Create Security Key',
    atLeast8Chars: 'At least 8 characters',
    agreeTerms: 'I agree to the',
    orbitalCharter: 'Orbital Charter',
    privacyProtocol: '& Privacy Protocol',
    createExplorerAccount: 'Create Explorer Account',
    provisioning: 'Provisioning...',
    accountCreated: '✓ Account Created',
    strengthWeak: 'Weak',
    strengthFair: 'Fair',
    strengthStrong: 'Strong',
    strengthCelestial: 'Celestial',

    // ── Badges & Home UI ──
    isroBadge: 'ISRO',
    indiaBadge: 'INDIA',
    stellarHeroTitle: 'STELLAR AI.',
    queryBarAria: 'Satellite Intelligence Query Bar',
    queryInputAria: 'Type your satellite query',
    attachTooltip: 'Attach telemetry document, dataset, or satellite picture',
    removeAttachment: 'Remove attachment',
  },

  hi: {
    // ── Query Bar ──
    queryBarPrompts: [
      'कुछ भी पूछें…',
      'उपग्रह कक्षा ट्रैक करें…',
      'ISS की स्थिति खोजें…',
      'LEO में मलबा खोजें…',
      'कक्षीय क्षय का अनुमान लगाएं…',
      'टेलीमेट्री डेटा विश्लेषण करें…',
      'NORAD ID से खोजें…',
      'सौर गतिविधि जांचें…',
    ],

    // ── Chat Header ──
    activeQuery: 'सक्रिय प्रश्न',
    about: 'जानकारी',

    // ── Chat Tabs ──
    tabAIAnalysis: 'AI विश्लेषण',
    tabUploadedImage: 'अपलोड की गई छवि',
    tabOrbitalRadar: 'कक्षीय राडार',
    tabNORADTLE: 'NORAD TLE',

    // ── Chat Header Buttons ──
    saveNote: 'नोट सेव करें',
    share: 'साझा करें',
    export: 'निर्यात',
    regenerate: 'पुनः उत्पन्न करें',

    // ── Chat Messages ──
    you: 'आप',
    stellarAI: 'सैटक्वेरी AI',
    processingQuery: 'उपग्रह डेटा विश्लेषण हो रहा है…',
    attachedImagery: 'संलग्न चित्र',
    apiError: 'API त्रुटि:',

    // ── Follow-up bar ──
    followupPlaceholder: 'अनुवर्ती प्रश्न पूछें या उपग्रह चित्र संलग्न करें…',
    followupLoadingPlaceholder: 'प्रश्न प्रोसेस हो रहा है…',

    // ── Right Summary Panel ──
    querySummary: 'प्रश्न सारांश',
    visual: 'दृश्य',
    rawData: 'कच्चा डेटा',
    confidenceScore: 'विश्वास स्कोर',
    classifiedTask: 'वर्गीकृत कार्य',
    spatialDetections: 'स्थानिक पहचान',
    regions: 'क्षेत्र',
    pipelineStatus: 'पाइपलाइन स्थिति',
    processing: 'प्रोसेसिंग…',
    error: 'त्रुटि',
    clarificationNeeded: 'स्पष्टीकरण आवश्यक ⚠️',
    completed: 'पूर्ण ✓',
    idle: 'निष्क्रिय',
    relatedTopics: 'संबंधित विषय और टैग',

    // ── Orbital Radar Tab ──
    agentSensorMetadata: 'एजेंट सेंसर और कक्षीय मेटाडेटा',
    orbitalSensorSweep: 'कक्षीय सेंसर स्वीप',
    runQueryFirst: 'सेंसर मेटाडेटा भरने के लिए पहले AI विश्लेषण प्रश्न चलाएं।',
    waitingAgent: 'एजेंट परिणाम की प्रतीक्षा…',
    taskType: 'कार्य प्रकार',
    sensorMode: 'सेंसर मोड',
    spectralPolarization: 'स्पेक्ट्रल / ध्रुवीकरण',
    passMode: 'पास मोड',
    offNadir: 'ऑफ-नाडिर कोण',
    confidence: 'विश्वास स्तर',
    toolPipeline: 'टूल पाइपलाइन',
    boundingBoxes: 'बाउंडिंग बॉक्स',
    noResultYet: 'अभी तक कोई परिणाम नहीं',

    // ── TLE Tab ──
    liveNORADTLE: 'लाइव NORAD TLE डेटा',
    fetchingTLE: '// Celestrak से लाइव TLE प्राप्त हो रहा है…',
    tleUnavailable: '// लाइव डेटा के लिए NORAD TLE टैब पर क्लिक करें',

    // ── About Modal & Team ──
    aboutStellar: 'सैटक्वेरी AI के बारे में',
    aboutDescription: 'सैटक्वेरी AI एक अत्याधुनिक पृथ्वी अवलोकन खुफिया मंच है जो संकलित LangGraph मल्टी-एजेंट ऑर्केस्ट्रेटर द्वारा संचालित है। यह प्रश्नों को विशेषज्ञ VQA, स्थानिक ग्राउंडिंग, परिवर्तन पहचान और क्रॉस-मोडल SAR-ऑप्टिकल फ्यूजन मॉडल के माध्यम से रूट करता है।',
    teamName: 'Debugg Dynasty',
    teamTitle: 'टीम Debugg Dynasty से मिलें',
    memberUditRole: 'टीम लीडर और AI & UI लीड',
    memberAadhyaRole: 'शोधकर्ता (Researcher)',
    memberAmanRole: 'बैकएंड लीड (Backend Lead)',
    memberSwastikaRole: 'विजुअल कंटेंट डिजाइनर',
    memberAkashRole: 'बैकएंड डेवलपर',
    memberNishantRole: 'फ्रंटएंड डेवलपर',

    // ── Sidebar — Nav Labels ──
    navSearch: 'खोज',
    navHistory: 'इतिहास',
    navKnowledge: 'ज्ञान आधार',
    navNotesDocs: 'नोट्स & दस्तावेज़',
    navAbout: 'जानकारी & टीम',
    navSettings: 'सेटिंग्स',
    navProfile: 'प्रोफ़ाइल',

    // ── Sidebar — Settings ──
    systemPreferences: 'सिस्टम प्राथमिकताएं',
    dopplerSync: 'रियल-टाइम डॉपलर सिंक',
    highPrecisionTLE: 'उच्च परिशुद्धता TLE गणना',

    // ── Sidebar — Profile ──
    missionOperator: 'मिशन ऑपरेटर',
    orbitalFlightDynamics: 'कक्षीय उड़ान गतिशीलता',
    signOut: 'साइन आउट',

    // ── Sidebar — History Modal ──
    recentQueryHistory: 'हाल के प्रश्न इतिहास',
    historySubheading: 'उपग्रह खुफिया पुनः लॉन्च करने के लिए कोई भी पुराना प्रश्न चुनें',
    clearHistory: 'इतिहास साफ़ करें',
    searchHistoryPlaceholder: 'कीवर्ड, NORAD ID या मिशन टैग से इतिहास खोजें...',
    launchQuery: 'प्रश्न लॉन्च करें',
    noHistoryFound: 'कोई इतिहास प्रविष्टि नहीं मिली',
    clearSearchFilter: 'खोज फ़िल्टर हटाएं या नया प्रश्न लॉन्च करें!',

    // ── Sidebar — Notes Modal ──
    orbitNotesDocs: 'कक्षा नोट्स और दस्तावेज़',
    notesSubheading: 'कस्टम शोध नोट्स बनाएं और AI प्रश्नों से उपग्रह चित्र सेव करें',
    exportNotes: 'निर्यात',
    newNote: 'नया नोट',
    cancel: 'रद्द करें',
    updateNote: 'नोट अपडेट करें',
    saveNote2: 'नोट सेव करें',
    noteTitlePlaceholder: 'नोट का शीर्षक (जैसे Cartosat-3 सोलर पैनल निरीक्षण)...',
    noteContentPlaceholder: 'अपने नोट्स, कक्षीय गणनाएं या उपग्रह विश्लेषण अवलोकन टाइप करें...',
    attachDocument: 'दस्तावेज़ संलग्न करें (.pdf, .txt, .json, .csv, .docx)',
    attachImage: 'तस्वीर / उपग्रह चित्र जोड़ें',
    searchNotesPlaceholder: 'शीर्षक, टैग, दस्तावेज़ या सामग्री से नोट्स खोजें...',
    allNotes: 'सभी नोट्स',
    noNotesYet: 'अभी तक कोई नोट नहीं बना',
    noNotesHint: '"+ नया नोट" पर क्लिक करके उपग्रह खुफिया, टेलीमेट्री और दस्तावेज़ सेव करें!',

    // ── Notes Tags ──
    tagTelemetry: 'टेलीमेट्री',
    tagEarthScan: 'पृथ्वी स्कैन',
    tagDebrisRisk: 'मलबा जोखिम',
    tagMissionLog: 'मिशन लॉग',
    tagResearch: 'अनुसंधान',
    tagGeneral: 'सामान्य',

    // ── Related Topics & Tech Chips ──
    topicSatelliteVQA: 'उपग्रह-VQA',
    topicISROAgent: 'इसरो-एजेंट',
    topicLangGraph: 'लैंगग्राफ',
    topicCartosat3: 'कार्टोसैट-3',
    topicSentinel2: 'सेंटिनल-2',
    langGraphOrchestrated: 'लैंगग्राफ ऑर्केस्ट्रेटेड',
    isroCompliant: 'इसरो अनुपालित',
    liquidGlassUI: 'लिक्विड ग्लास UI',

    // ── Note Actions ──
    copyNoteText: 'नोट कॉपी करें',
    editNoteTitle: 'नोट संपादित करें',
    deleteNoteTitle: 'नोट हटाएं',
    closeModal: 'बंद करें',

    // ── Translating indicator ──
    translating: 'अनुवाद हो रहा है…',

    // ── Auth & Hero Screen ──
    brandBadge: 'सैटक्वेरी AI इंजन • सक्रिय',
    heroHeading: 'स्वायत्त उपग्रह विजुअल QA',
    heroSubtitle: 'प्राकृतिक AI बातचीत के माध्यम से किसी भी पृथ्वी अवलोकन दृश्य, STAC सेंटिनल-2 और लैंडसैट-9 इमेजरी, निर्देशांक या स्वचालित परिवर्तन पहचान को तुरंत खोजें।',
    telemetryStac: 'STAC सेंटिनल-2 & लैंडसैट-9',
    telemetryIsro: 'इसरो पृथ्वी अवलोकन',
    signInTab: 'साइन इन',
    createAccountTab: 'खाता बनाएं',
    orbitalEmail: 'कक्षीय ईमेल / कॉल साइन',
    securityKey: 'सुरक्षा कुंजी',
    keepSessionActive: 'सत्र सक्रिय रखें',
    resetSecurityKey: 'सुरक्षा कुंजी रीसेट करें?',
    launchSession: 'सत्र शुरू करें',
    authenticating: 'प्रमाणीकरण जारी...',
    accessGranted: '✓ प्रवेश स्वीकृत',
    orAuthenticateVia: 'या इसके माध्यम से प्रमाणित करें',
    commanderName: 'कमांडर नाम',
    createSecurityKey: 'सुरक्षा कुंजी बनाएं',
    atLeast8Chars: 'कम से कम 8 वर्ण',
    agreeTerms: 'मैं सहमत हूँ',
    orbitalCharter: 'कक्षीय चार्टर',
    privacyProtocol: '& गोपनीयता प्रोटोकॉल से',
    createExplorerAccount: 'अन्वेषक खाता बनाएं',
    provisioning: 'खाता तैयार हो रहा है...',
    accountCreated: '✓ खाता बन गया',
    strengthWeak: 'कमज़ोर',
    strengthFair: 'ठीक',
    strengthStrong: 'मजबूत',
    strengthCelestial: 'दिव्य',

    // ── Badges & Home UI ──
    isroBadge: 'इसरो',
    indiaBadge: 'भारत',
    stellarHeroTitle: 'सैटक्वेरी एआई.',
    queryBarAria: 'उपग्रह खुफिया प्रश्न पट्टी',
    queryInputAria: 'अपना उपग्रह प्रश्न दर्ज करें',
    attachTooltip: 'टेलीमेट्री दस्तावेज़, डेटासेट या उपग्रह चित्र संलग्न करें',
    removeAttachment: 'संलग्नक हटाएं',
  },
};
