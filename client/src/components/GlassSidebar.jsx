import React, { useState, useEffect, useRef } from 'react';
import {
  Search,
  Clock,
  FileText,
  Settings,
  User,
  Trash2,
  X,
  ChevronRight,
  Plus,
  Image as ImageIcon,
  Tag,
  Save,
  Edit3,
  Paperclip,
  Copy,
  Check,
  Download,
  LogOut,
  FileCheck,
  Info,
  Lightbulb,
  Layers,
  Sparkles,
  Send,
  PlusCircle
} from 'lucide-react';
import './GlassSidebar.css';
import { useT, useLanguage } from '../context/LanguageContext';
import { translations } from '../utils/translations';
import AboutModal from './AboutModal';

const NOTE_TAGS = [
  { id: 'Telemetry', labelKey: 'tagTelemetry' },
  { id: 'Earth Scan', labelKey: 'tagEarthScan' },
  { id: 'Debris Risk', labelKey: 'tagDebrisRisk' },
  { id: 'Mission Log', labelKey: 'tagMissionLog' },
  { id: 'Research', labelKey: 'tagResearch' },
  { id: 'General', labelKey: 'tagGeneral' },
];

const getTagDisplay = (tagId, t, isHindi) => {
  const item = NOTE_TAGS.find(nt => nt.id.toLowerCase() === (tagId || '').toLowerCase());
  if (item && t[item.labelKey]) return t[item.labelKey];
  if (isHindi && item && translations.hi[item.labelKey]) return translations.hi[item.labelKey];
  return tagId;
};

const NAV_ITEMS = [
  { id: 'history',   icon: Clock,     labelKey: 'navHistory' },
  { id: 'documents', icon: FileText,  labelKey: 'navNotesDocs', title: 'Orbit Notes & Documents' },
  { id: 'knowledge', icon: Lightbulb, labelKey: 'navKnowledge', title: 'Knowledge Base (NODUS)' },
  { id: 'settings',  icon: Settings,  labelKey: 'navSettings' },
  { id: 'profile',   icon: User,      labelKey: 'navProfile' },
];

const INITIAL_HISTORY = [
  {
    id: 1,
    query: 'Track ISRO Cartosat-3 orbit',
    query_hi: 'इसरो कार्टोसैट-3 कक्षा को ट्रैक करें',
    time: '12m ago',
    time_hi: '12 मिनट पहले',
    tag: 'ISRO',
    tag_hi: 'इसरो',
    desc: 'Real-time telemetry and Doppler shift analysis for LEO orbit node.',
    desc_hi: 'LEO ऑर्बिट नोड के लिए रीयल-टाइम टेलीमेट्री और डॉपलर शिफ्ट विश्लेषण।'
  },
  {
    id: 2,
    query: 'Query ISS position & TLE catalog',
    query_hi: 'ISS स्थिति और TLE कैटलॉग खोजें',
    time: '1h ago',
    time_hi: '1 घंटा पहले',
    tag: 'NORAD',
    tag_hi: 'नोराड',
    desc: 'NORAD Two-Line Element sets updated with current ISS altitude.',
    desc_hi: 'वर्तमान ISS ऊंचाई के साथ अद्यतित NORAD टू-लाइन एलिमेंट सेट।'
  },
  {
    id: 3,
    query: 'Find space debris in Low Earth Orbit',
    query_hi: 'लो अर्थ ऑर्बिट (LEO) में अंतरिक्ष मलबा खोजें',
    time: '3h ago',
    time_hi: '3 घंटे पहले',
    tag: 'Debris',
    tag_hi: 'मलबा',
    desc: 'Collision avoidance risk calculations for active satellite mesh.',
    desc_hi: 'सक्रिय उपग्रह मेश के लिए टकराव परिहार जोखिम गणनाएं।'
  },
  {
    id: 4,
    query: 'Predict Chandrayaan-3 trajectory decay',
    query_hi: 'चंद्रयान-3 प्रक्षेपवक्र क्षय का अनुमान लगाएं',
    time: 'Yesterday',
    time_hi: 'कल',
    tag: 'Moon',
    tag_hi: 'चंद्रमा',
    desc: 'Lunar transfer trajectory & apogee distance modeling.',
    desc_hi: 'चंद्र स्थानांतरण प्रक्षेपवक्र और अपोजी दूरी मॉडलिंग।'
  },
  {
    id: 5,
    query: 'Analyse Sentinel-2 SAR radar imagery',
    query_hi: 'सेंटिनल-2 SAR रडार इमेजरी का विश्लेषण करें',
    time: '2 days ago',
    time_hi: '2 दिन पहले',
    tag: 'Radar',
    tag_hi: 'रडार',
    desc: 'Multispectral false-color infrared terrain scan inspection.',
    desc_hi: 'मल्टीस्पेक्ट्रल फॉल्स-कलर इन्फ्रारेड भूभाग स्कैन निरीक्षण।'
  },
];

const INITIAL_NOTES = [
  {
    id: 1,
    title: 'ISRO Cartosat-3 Orbit & Node Telemetry',
    title_hi: 'इसरो कार्टोसैट-3 कक्षा और नोड टेलीमेट्री',
    content: 'Inclination: 97.5° SSO. Operating altitude ~509 km. High-resolution panchromatic & multispectral sensors active with Doppler frequency correction.',
    content_hi: 'झुकाव: 97.5° SSO। परिचालन ऊंचाई ~509 किमी। डॉपलर आवृत्ति सुधार के साथ उच्च-रिज़ॉल्यूशन पैनक्रोमैटिक और मल्टीस्पेक्ट्रल सेंसर सक्रिय।',
    tag: 'Telemetry',
    tag_hi: 'टेलीमेट्री',
    color: '#D8D365',
    image: '/sat_orbit.jpg',
    date: 'Sep 10, 2026',
    date_hi: '10 सित, 2026'
  },
  {
    id: 2,
    title: 'Sentinel-2 Infrared Coastal Scan Analysis',
    title_hi: 'सेंटिनल-2 इन्फ्रारेड तटीय स्कैन विश्लेषण',
    content: 'Multispectral false-color infrared highlights active coral reef ecosystems and coastal erosion patterns along Australian shoreline.',
    content_hi: 'मल्टीस्पेक्ट्रल फॉल्स-कलर इन्फ्रारेड ऑस्ट्रेलियाई तटरेखा के साथ सक्रिय कोरल रीफ पारिस्थितिकी तंत्र और तटीय कटाव पैटर्न को उजागर करता है।',
    tag: 'Earth Scan',
    tag_hi: 'पृथ्वी स्कैन',
    color: '#38bdf8',
    image: '/earth_scan.jpg',
    date: 'Sep 09, 2026',
    date_hi: '09 सित, 2026'
  }
];

function GlassSidebar({ activeNav, onNavChange, onSelectQuery, currentUser, onLogout }) {
  const t = useT();
  const { isHindi } = useLanguage();
  const [active, setActive] = useState(activeNav || null);
  const [historyList, setHistoryList] = useState(INITIAL_HISTORY);
  const [historyFilter, setHistoryFilter] = useState('');
  
  // Note Taking State with LocalStorage Persistence
  const [notesList, setNotesList] = useState(() => {
    try {
      const saved = localStorage.getItem('stellar_orbit_notes');
      if (saved) {
        return JSON.parse(saved);
      }
      return INITIAL_NOTES;
    } catch {
      return INITIAL_NOTES;
    }
  });
  const [noteFilter, setNoteFilter] = useState('');
  const [activeTagFilter, setActiveTagFilter] = useState('All');
  const [isCreatingNote, setIsCreatingNote] = useState(false);
  const [editingNoteId, setEditingNoteId] = useState(null);
  const [copiedId, setCopiedId] = useState(null);
  const [selectedNoteId, setSelectedNoteId] = useState(() => notesList[0]?.id || null);
  
  // New Note Form State
  const [noteTitle, setNoteTitle] = useState(() => notesList[0]?.title || '');
  const [noteContent, setNoteContent] = useState(() => notesList[0]?.content || '');
  const [noteTag, setNoteTag] = useState(() => notesList[0]?.tag || 'Telemetry');
  const [noteDocument, setNoteDocument] = useState(() => notesList[0]?.document || null); // { name, size, data }
  const [noteImage, setNoteImage] = useState(() => notesList[0]?.image || null); // base64 or URL

  const sidebarRef = useRef(null);

  // Sync editor fields with active note when switching notes
  useEffect(() => {
    if (selectedNoteId && !isCreatingNote) {
      const activeNote = notesList.find(n => n.id === selectedNoteId);
      if (activeNote) {
        setNoteTitle(activeNote.title || '');
        setNoteContent(activeNote.content || '');
        setNoteTag(activeNote.tag || 'Telemetry');
        setNoteDocument(activeNote.document || null);
        setNoteImage(activeNote.image || null);
        setEditingNoteId(activeNote.id);
      }
    }
  }, [selectedNoteId, isCreatingNote]);

  useEffect(() => {
    try {
      localStorage.setItem('stellar_orbit_notes', JSON.stringify(notesList));
    } catch (e) {
      console.error('Failed to persist notes:', e);
    }
  }, [notesList]);

  // ── NODUS-Inspired Knowledge Reuse State ──
  const [knowledgeTab, setKnowledgeTab] = useState('cards'); // 'cards' | 'chains'
  const [knowledgeCards, setKnowledgeCards] = useState([
    {
      id: 'kcard_sample_1',
      title: 'Cartosat-3 High-Res Urban Segmentation',
      query_text: 'Identify dense built-up residential clusters and estimate road density',
      summary: 'Segmentation identified 4 distinct urban sub-clusters with high building density (>75%). Spectral signature shows asphalt paving and concrete roof dominance.',
      queue: 'default',
      tags: ['cartosat3', 'urban', 'segmentation'],
      created_at: new Date(Date.now() - 3600000).toISOString(),
    },
    {
      id: 'kcard_sample_2',
      title: 'Sentinel-2 Monsoonal Flood Inundation Baseline',
      query_text: 'Detect inundated agricultural parcels in Godavari river basin',
      summary: 'MNDWI index indicated 34.2 sq km of waterlogging. Pre-monsoon baseline confirmed intact embankments with post-event overflow.',
      queue: 'quick',
      tags: ['sentinel2', 'flood', 'water', 'change_detection'],
      created_at: new Date(Date.now() - 86400000).toISOString(),
    }
  ]);
  const [knowledgeChains, setKnowledgeChains] = useState([
    {
      id: 'kchain_sample_1',
      title: 'Monsoon Hazard Rapid Response Sequence',
      description: 'Ordered multi-stage pipeline: Baseline Surface Water -> Inundation Extent -> Urban Vulnerability',
      card_ids: ['kcard_sample_2', 'kcard_sample_1'],
      created_at: new Date(Date.now() - 7200000).toISOString(),
    }
  ]);
  const [knowledgeFilter, setKnowledgeFilter] = useState('');
  const [selectedQueue, setSelectedQueue] = useState('all');
  const [isCreatingChain, setIsCreatingChain] = useState(false);
  const [newChainTitle, setNewChainTitle] = useState('');
  const [newChainDesc, setNewChainDesc] = useState('');
  const [selectedChainCardIds, setSelectedChainCardIds] = useState([]);

  // Fetch knowledge from backend when tab opens
  const fetchKnowledge = useCallback(async () => {
    try {
      const token = localStorage.getItem('stellar_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const [cardsRes, chainsRes] = await Promise.allSettled([
        fetch('/api/v1/knowledge/cards', { headers }),
        fetch('/api/v1/knowledge/chains', { headers })
      ]);
      if (cardsRes.status === 'fulfilled' && cardsRes.value.ok) {
        const cardsData = await cardsRes.value.json();
        if (Array.isArray(cardsData) && cardsData.length > 0) {
          setKnowledgeCards(cardsData);
        }
      }
      if (chainsRes.status === 'fulfilled' && chainsRes.value.ok) {
        const chainsData = await chainsRes.value.json();
        if (Array.isArray(chainsData) && chainsData.length > 0) {
          setKnowledgeChains(chainsData);
        }
      }
    } catch (e) {
      console.warn('Using local knowledge store fallback:', e);
    }
  }, []);

  useEffect(() => {
    if (active === 'knowledge') {
      fetchKnowledge();
    }
  }, [active, fetchKnowledge]);

  const handleDeleteCard = async (cardId, e) => {
    if (e) e.stopPropagation();
    try {
      const token = localStorage.getItem('stellar_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      await fetch(`/api/v1/knowledge/cards/${cardId}`, { method: 'DELETE', headers });
    } catch (_) {}
    setKnowledgeCards(prev => prev.filter(c => c.id !== cardId));
  };

  const handleDeleteChain = async (chainId, e) => {
    if (e) e.stopPropagation();
    try {
      const token = localStorage.getItem('stellar_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      await fetch(`/api/v1/knowledge/chains/${chainId}`, { method: 'DELETE', headers });
    } catch (_) {}
    setKnowledgeChains(prev => prev.filter(c => c.id !== chainId));
  };

  const handleSaveChain = async (e) => {
    e.preventDefault();
    if (!newChainTitle.trim() || selectedChainCardIds.length === 0) return;
    const newChain = {
      id: `kchain_${Date.now()}`,
      title: newChainTitle.trim(),
      description: newChainDesc.trim(),
      card_ids: selectedChainCardIds,
      created_at: new Date().toISOString()
    };
    try {
      const token = localStorage.getItem('stellar_token');
      const headers = { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) };
      const res = await fetch('/api/v1/knowledge/chains', {
        method: 'POST',
        headers,
        body: JSON.stringify(newChain)
      });
      if (res.ok) {
        const data = await res.json();
        setKnowledgeChains(prev => [data, ...prev]);
      } else {
        setKnowledgeChains(prev => [newChain, ...prev]);
      }
    } catch (_) {
      setKnowledgeChains(prev => [newChain, ...prev]);
    }
    setIsCreatingChain(false);
    setNewChainTitle('');
    setNewChainDesc('');
    setSelectedChainCardIds([]);
  };

  const handleInjectKnowledge = (queryText) => {
    if (onSelectQuery) onSelectQuery(queryText);
    setActive(null);
  };

  const handleSelect = (id, e) => {
    if (e) e.stopPropagation();
    const nextActive = active === id ? null : id;
    setActive(nextActive);
    if (onNavChange) onNavChange(nextActive);
  };

  const handleHistoryClick = (queryText) => {
    if (onSelectQuery) onSelectQuery(queryText);
    setActive(null);
  };

  const clearHistory = () => {
    setHistoryList([]);
  };

  // Note Taking Actions
  const handleStartNewNote = () => {
    setIsCreatingNote(true);
    setEditingNoteId(null);
    setSelectedNoteId(null);
    setNoteTitle('');
    setNoteContent('');
    setNoteTag('Telemetry');
    setNoteDocument(null);
    setNoteImage(null);
  };

  const handleSelectNote = (note) => {
    setIsCreatingNote(false);
    setSelectedNoteId(note.id);
    setEditingNoteId(note.id);
    setNoteTitle(note.title || '');
    setNoteContent(note.content || '');
    setNoteTag(note.tag || 'Telemetry');
    setNoteDocument(note.document || null);
    setNoteImage(note.image || null);
  };

  const handleSaveNote = (e) => {
    e?.preventDefault();
    if (!noteTitle.trim() && !noteContent.trim()) return;

    const currentTagObj = NOTE_TAGS.find(nt => nt.id === noteTag);
    const tagHi = translations.hi[currentTagObj?.labelKey] || noteTag;
    const finalTitle = noteTitle.trim() || (isHindi ? 'शीर्षकहीन नोट' : 'Untitled Note');

    if (editingNoteId) {
      setNotesList(prev => prev.map(n => n.id === editingNoteId ? {
        ...n,
        title: finalTitle,
        content: noteContent.trim(),
        tag: noteTag,
        tag_hi: tagHi,
        document: noteDocument,
        image: noteImage
      } : n));
      setSelectedNoteId(editingNoteId);
      setIsCreatingNote(false);
    } else {
      const newId = Date.now();
      const newNote = {
        id: newId,
        title: finalTitle,
        content: noteContent.trim(),
        tag: noteTag,
        tag_hi: tagHi,
        color: '#D8D365',
        document: noteDocument,
        image: noteImage,
        date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        date_hi: new Date().toLocaleDateString('hi-IN', { month: 'short', day: 'numeric', year: 'numeric' })
      };
      setNotesList(prev => [newNote, ...prev]);
      setSelectedNoteId(newId);
      setEditingNoteId(newId);
      setIsCreatingNote(false);
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (uploadEvent) => {
      setNoteImage(uploadEvent.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleEditNote = (note) => {
    handleSelectNote(note);
  };

  const handleDeleteNote = (id, e) => {
    e?.stopPropagation();
    setNotesList(prev => {
      const remaining = prev.filter(n => n.id !== id);
      if (selectedNoteId === id) {
        const next = remaining[0]?.id || null;
        setSelectedNoteId(next);
        if (next) {
          const nextNote = remaining[0];
          setNoteTitle(nextNote.title || '');
          setNoteContent(nextNote.content || '');
          setNoteTag(nextNote.tag || 'Telemetry');
          setNoteDocument(nextNote.document || null);
          setNoteImage(nextNote.image || null);
          setEditingNoteId(nextNote.id);
        } else {
          setNoteTitle('');
          setNoteContent('');
          setNoteDocument(null);
          setNoteImage(null);
          setEditingNoteId(null);
        }
      }
      return remaining;
    });
  };

  const handleCopyNote = (note, e) => {
    e?.stopPropagation();
    const tagText = getTagDisplay(note.tag, t, isHindi);
    const textToCopy = `[${tagText}] ${note.title}\nDate: ${note.date}\n\n${note.content}${note.document ? `\nAttached Document: ${note.document.name}` : ''}`;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(textToCopy);
      setCopiedId(note.id);
      setTimeout(() => setCopiedId(null), 2000);
    }
  };

  const handleExportNotes = () => {
    const exportData = JSON.stringify(notesList, null, 2);
    const blob = new Blob([exportData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `stellar_notes_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (uploadEvent) => {
      setNoteDocument({
        name: file.name,
        size: file.size < 1024 * 1024 ? `${(file.size / 1024).toFixed(1)} KB` : `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
        type: file.type || 'document',
        data: uploadEvent.target.result
      });
    };
    reader.readAsDataURL(file);
  };

  const filteredHistory = historyList.filter(item => {
    const q = isHindi ? (item.query_hi || item.query) : item.query;
    const tg = isHindi ? (item.tag_hi || item.tag) : item.tag;
    const d = isHindi ? (item.desc_hi || item.desc) : item.desc;
    const filter = historyFilter.toLowerCase();
    return (
      item.query.toLowerCase().includes(filter) ||
      item.tag.toLowerCase().includes(filter) ||
      item.desc.toLowerCase().includes(filter) ||
      q.toLowerCase().includes(filter) ||
      tg.toLowerCase().includes(filter) ||
      d.toLowerCase().includes(filter)
    );
  });

  const filteredNotes = notesList.filter(note => {
    const title = isHindi ? (note.title_hi || note.title) : note.title;
    const content = isHindi ? (note.content_hi || note.content) : note.content;
    const tag = isHindi ? (note.tag_hi || note.tag) : note.tag;
    const tagDisplay = getTagDisplay(note.tag, t, isHindi);
    const filter = noteFilter.toLowerCase();
    const matchesTag = activeTagFilter === 'All' || 
      note.tag.toLowerCase() === activeTagFilter.toLowerCase() || 
      tag.toLowerCase() === activeTagFilter.toLowerCase() ||
      tagDisplay.toLowerCase() === activeTagFilter.toLowerCase();
    const matchesKeyword = 
      note.title.toLowerCase().includes(filter) ||
      note.content.toLowerCase().includes(filter) ||
      note.tag.toLowerCase().includes(filter) ||
      title.toLowerCase().includes(filter) ||
      content.toLowerCase().includes(filter) ||
      tag.toLowerCase().includes(filter) ||
      tagDisplay.toLowerCase().includes(filter) ||
      (note.document && note.document.name.toLowerCase().includes(filter));
    return matchesTag && matchesKeyword;
  });

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (sidebarRef.current && !sidebarRef.current.contains(event.target)) {
        if (active !== 'history' && active !== 'documents' && active !== 'knowledge') {
          setActive(null);
          if (onNavChange) onNavChange(null);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [active, onNavChange]);

  return (
    <>
      <div className="glass-sidebar-wrapper" ref={sidebarRef}>
        <div className="glass-sidebar">
          {/* Floating Nav Pills */}
          <nav className="glass-sidebar-nav">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = active === item.id;

              return (
                <div key={item.id} className="nav-item-rel-wrap">
                  <button
                    className={`glass-nav-pill ${isActive ? 'active' : ''}`}
                    data-item={item.id}
                    onClick={(e) => handleSelect(item.id, e)}
                    title={t[item.labelKey]}
                    aria-label={t[item.labelKey]}
                  >
                    <span className="glass-nav-pill-icon">
                      <Icon size={18} />
                    </span>
                    <span className="glass-nav-pill-label">
                      {t[item.labelKey]}
                    </span>
                  </button>

                  {/* ── Settings Flyout ── */}
                  {isActive && item.id === 'settings' && (
                    <div className="sidebar-flyout-panel settings-flyout" onClick={(e) => e.stopPropagation()}>
                      <div className="flyout-header">
                        <span className="flyout-title">
                          <Settings size={15} /> {t.systemPreferences}
                        </span>
                        <button className="flyout-icon-btn" onClick={() => setActive(null)}>
                          <X size={14} />
                        </button>
                      </div>
                      <div className="setting-toggle-row">
                        <span>{t.dopplerSync}</span>
                        <input type="checkbox" defaultChecked />
                      </div>
                      <div className="setting-toggle-row">
                        <span>{t.highPrecisionTLE}</span>
                        <input type="checkbox" defaultChecked />
                      </div>
                    </div>
                  )}

                  {/* ── Profile Flyout ── */}
                  {isActive && item.id === 'profile' && (
                    <div className="sidebar-flyout-panel profile-flyout" onClick={(e) => e.stopPropagation()}>
                      <div className="flyout-header">
                        <span className="flyout-title">
                          <User size={15} /> {t.missionOperator}
                        </span>
                        <button className="flyout-icon-btn" onClick={() => setActive(null)}>
                          <X size={14} />
                        </button>
                      </div>
                      <div className="profile-badge-row">
                        <div className="profile-avatar">
                          {currentUser?.username ? currentUser.username.charAt(0).toUpperCase() : 'ISRO'}
                        </div>
                        <div className="profile-meta">
                          <span className="profile-name">{currentUser?.username || 'ISRO Command Center'}</span>
                          <span className="profile-desc">{t.orbitalFlightDynamics}</span>
                        </div>
                      </div>
                      {onLogout && (
                        <button 
                          className="profile-signout-btn" 
                          onClick={() => { onLogout(); setActive(null); }}
                          title={t.signOut}
                        >
                          <LogOut size={14} /> {t.signOut}
                        </button>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </nav>
        </div>
      </div>

      {/* ── Center Transparent Big History Card Modal ── */}
      {active === 'history' && (
        <div className="history-modal-backdrop" onClick={() => setActive(null)}>
          <div className="history-center-card" onClick={(e) => e.stopPropagation()}>
            <div className="history-card-header">
              <div className="history-title-amber">
                <div className="history-amber-icon-badge">
                  <Clock size={20} />
                </div>
                <div>
                  <h2 className="history-main-heading">{t.recentQueryHistory}</h2>
                  <p className="history-sub-heading">{t.historySubheading}</p>
                </div>
              </div>

              <div className="history-header-actions">
                {historyList.length > 0 && (
                  <button className="history-clear-btn" onClick={clearHistory} title={t.clearHistory}>
                    <Trash2 size={15} /> {t.clearHistory}
                  </button>
                )}
                <button className="history-close-btn" onClick={() => setActive(null)} title="Close">
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Amber Filter Input Bar */}
            <div className="history-search-bar-amber">
              <Search size={16} style={{ color: '#eab308' }} />
              <input 
                type="text" 
                className="history-filter-input"
                placeholder={t.searchHistoryPlaceholder}
                value={historyFilter}
                onChange={(e) => setHistoryFilter(e.target.value)}
                autoFocus
              />
              {historyFilter && (
                <button className="history-filter-clear" onClick={() => setHistoryFilter('')}>
                  <X size={13} />
                </button>
              )}
            </div>

            {/* Big History Grid / List */}
            <div className="history-big-list">
              {filteredHistory.length > 0 ? (
                filteredHistory.map((item) => {
                  const displayQuery = isHindi ? (item.query_hi || item.query) : item.query;
                  const displayTag   = isHindi ? (item.tag_hi || item.tag) : item.tag;
                  const displayTime  = isHindi ? (item.time_hi || item.time) : item.time;
                  const displayDesc  = isHindi ? (item.desc_hi || item.desc || '') : (item.desc || '');
                  return (
                    <div 
                      key={item.id} 
                      className="history-big-item-card"
                      onClick={() => handleHistoryClick(displayQuery)}
                    >
                      <div className="history-item-top">
                        <span className="history-query-title">"{displayQuery}"</span>
                        <span className="history-amber-tag">#{displayTag}</span>
                      </div>
                      <p className="history-query-desc">{displayDesc}</p>
                      <div className="history-item-bottom">
                        <span className="history-time-badge">
                          <Clock size={12} /> {displayTime}
                        </span>
                        <span className="history-launch-prompt">
                          {t.launchQuery} <ChevronRight size={14} />
                        </span>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="history-empty-box">
                  <Clock size={36} style={{ color: 'rgba(251, 191, 36, 0.4)', marginBottom: '10px' }} />
                  <p style={{ margin: 0, fontWeight: 600 }}>{t.noHistoryFound}</p>
                  <span style={{ fontSize: '0.8rem', opacity: 0.6 }}>{t.clearSearchFilter}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Orbit Notes App (Split 2-Pane Side Panel Covering Half the Page) ── */}
      {active === 'documents' && (
        <div className="notes-app-backdrop" onClick={() => setActive(null)}>
          <div className="notes-app-container" onClick={(e) => e.stopPropagation()}>
            {/* Top Bar */}
            <div className="notes-app-topbar">
              <div className="notes-app-brand">
                <div className="notes-app-icon-badge">
                  <FileText size={18} />
                </div>
                <div>
                  <div className="notes-app-title-row">
                    <h2 className="notes-app-heading">{t.orbitNotesDocs}</h2>
                    <span className="notes-app-count-badge">{filteredNotes.length}</span>
                  </div>
                  <p className="notes-app-subheading">{t.notesSubheading}</p>
                </div>
              </div>

              <div className="notes-app-top-actions">
                <button 
                  className="notes-app-new-btn" 
                  onClick={handleStartNewNote}
                  title={t.newNote}
                >
                  <Plus size={15} /> {t.newNote}
                </button>
                {notesList.length > 0 && (
                  <button className="notes-app-export-btn" onClick={handleExportNotes} title={t.exportNotes}>
                    <Download size={14} /> {t.exportNotes}
                  </button>
                )}
                <button className="history-close-btn" onClick={() => setActive(null)} title="Close">
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Split 2-Pane Body */}
            <div className="notes-app-body">
              {/* Left Column: Notes List & Filter (~38%) */}
              <div className="notes-app-list-pane">
                {/* Search Bar */}
                <div className="notes-search-bar">
                  <Search size={15} style={{ color: '#D8D365' }} />
                  <input 
                    type="text" 
                    className="notes-search-input"
                    placeholder={t.searchNotesPlaceholder}
                    value={noteFilter}
                    onChange={(e) => setNoteFilter(e.target.value)}
                  />
                  {noteFilter && (
                    <button className="history-filter-clear" onClick={() => setNoteFilter('')}>
                      <X size={13} />
                    </button>
                  )}
                </div>

                {/* Tag Filter Pills */}
                <div className="notes-tag-pills">
                  <button
                    className={`notes-tag-pill ${activeTagFilter === 'All' ? 'active' : ''}`}
                    onClick={() => setActiveTagFilter('All')}
                  >
                    {t.allNotes}
                  </button>
                  {NOTE_TAGS.map(({ id, labelKey }) => (
                    <button
                      key={id}
                      className={`notes-tag-pill ${activeTagFilter === id ? 'active' : ''}`}
                      onClick={() => setActiveTagFilter(id)}
                    >
                      #{t[labelKey] || id}
                    </button>
                  ))}
                </div>

                {/* Notes List Scrollable */}
                <div className="notes-list-items">
                  {filteredNotes.length > 0 ? (
                    filteredNotes.map((note) => {
                      const displayTitle = isHindi ? (note.title_hi || note.title) : note.title;
                      const displayTag = getTagDisplay(note.tag, t, isHindi);
                      const displayContent = isHindi ? (note.content_hi || note.content) : note.content;
                      const displayDate = isHindi ? (note.date_hi || note.date) : note.date;
                      const isSelected = (!isCreatingNote && selectedNoteId === note.id);

                      return (
                        <div 
                          key={note.id} 
                          className={`notes-item-row ${isSelected ? 'selected' : ''}`}
                          onClick={() => handleSelectNote(note)}
                        >
                          <div className="notes-item-row-header">
                            <h4 className="notes-item-row-title">{displayTitle}</h4>
                            <span className="notes-item-tag">#{displayTag}</span>
                          </div>
                          <p className="notes-item-row-snippet">{displayContent}</p>
                          <div className="notes-item-row-footer">
                            <span className="notes-item-row-date">{displayDate}</span>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                              {note.image && (
                                <span className="notes-item-doc-indicator" title="Has Image Attachment">
                                  <ImageIcon size={11} /> Photo
                                </span>
                              )}
                              {note.document && (
                                <span className="notes-item-doc-indicator" title={note.document.name}>
                                  <Paperclip size={11} /> {note.document.name}
                                </span>
                              )}
                            </div>
                            <div className="notes-item-actions-hover">
                              <button 
                                className="note-action-icon" 
                                onClick={(e) => handleCopyNote({ ...note, title: displayTitle, content: displayContent, tag: displayTag, date: displayDate }, e)}
                                title="Copy"
                              >
                                {copiedId === note.id ? <Check size={13} color="#34d399" /> : <Copy size={13} />}
                              </button>
                              <button 
                                className="note-action-icon delete" 
                                onClick={(e) => handleDeleteNote(note.id, e)}
                                title="Delete"
                              >
                                <Trash2 size={13} />
                              </button>
                            </div>
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <div className="notes-list-empty">
                      <FileText size={28} style={{ color: 'rgba(216, 211, 101, 0.4)', marginBottom: '8px' }} />
                      <p>{t.noNotesYet}</p>
                      <button className="notes-create-first-btn" onClick={handleStartNewNote}>
                        <Plus size={13} /> {t.newNote}
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Right Column: Note Editor / Detail View (Dominant Area ~74%) */}
              <div className="notes-app-editor-pane">
                {(isCreatingNote || selectedNoteId) ? (
                  <form className="notes-editor-form" onSubmit={handleSaveNote}>
                    {/* Editor Header: Title & Tag Selector */}
                    <div className="notes-editor-top">
                      <input 
                        type="text" 
                        className="notes-editor-title-input" 
                        placeholder={t.noteTitlePlaceholder}
                        value={noteTitle}
                        onChange={(e) => setNoteTitle(e.target.value)}
                        required
                        autoFocus={isCreatingNote}
                      />
                      <div className="notes-editor-meta-row">
                        <select 
                          className="notes-editor-tag-select"
                          value={noteTag}
                          onChange={(e) => setNoteTag(e.target.value)}
                        >
                          {NOTE_TAGS.map(({ id, labelKey }) => (
                            <option key={id} value={id}>
                              #{t[labelKey] || id}
                            </option>
                          ))}
                        </select>
                        <span className="notes-editor-timestamp">
                          {isCreatingNote ? (isHindi ? 'नया नोट ड्राफ्ट' : 'New Note Draft') : (isHindi ? 'सहेजा गया नोट' : 'Saved Note')}
                        </span>
                      </div>
                    </div>

                    {/* Attachments Section: Image Preview & Doc Badges */}
                    <div className="notes-editor-attachments-row">
                      {/* Attached Image Preview */}
                      {noteImage && (
                        <div className="attached-image-badge">
                          <img src={noteImage} alt="Satellite Attachment" className="attached-image-thumb" />
                          <span className="attached-image-label">{isHindi ? 'उपग्रह छवि' : 'Attached Photo'}</span>
                          <button 
                            type="button" 
                            className="doc-remove-btn" 
                            onClick={() => setNoteImage(null)}
                            title="Remove Image"
                          >
                            <X size={12} />
                          </button>
                        </div>
                      )}

                      {/* Attached Document Badge */}
                      {noteDocument && (
                        <div className="attached-doc-badge">
                          <FileCheck size={14} />
                          <span className="doc-name">{noteDocument.name} ({noteDocument.size})</span>
                          <button type="button" className="doc-remove-btn" onClick={() => setNoteDocument(null)}>
                            <X size={12} />
                          </button>
                        </div>
                      )}

                      {/* Attachment Buttons */}
                      <div className="notes-attach-btn-group">
                        <label className="upload-custom-lbl doc-upload" title={t.attachImage}>
                          <ImageIcon size={13} /> {t.attachImage}
                          <input type="file" accept="image/*" onChange={handleImageUpload} style={{ display: 'none' }} />
                        </label>

                        {!noteDocument && (
                          <label className="upload-custom-lbl doc-upload" title={t.attachDocument}>
                            <Paperclip size={13} /> {t.attachDocument}
                            <input type="file" accept=".pdf,.txt,.json,.csv,.doc,.docx" onChange={handleFileUpload} style={{ display: 'none' }} />
                          </label>
                        )}
                      </div>
                    </div>

                    {/* Editor Main Content Textarea */}
                    <textarea 
                      className="notes-editor-textarea"
                      placeholder={t.noteContentPlaceholder}
                      value={noteContent}
                      onChange={(e) => setNoteContent(e.target.value)}
                      required
                    />

                    {/* Editor Bottom Actions */}
                    <div className="notes-editor-actions-bar">
                      <div className="notes-editor-actions-left">
                        {editingNoteId && (
                          <button 
                            type="button" 
                            className="notes-action-subtle-btn"
                            onClick={() => {
                              const activeNote = notesList.find(n => n.id === editingNoteId);
                              if (activeNote) handleCopyNote(activeNote);
                            }}
                          >
                            <Copy size={13} /> {isHindi ? 'कॉपी करें' : 'Copy'}
                          </button>
                        )}
                        {editingNoteId && (
                          <button 
                            type="button" 
                            className="notes-action-subtle-btn delete"
                            onClick={(e) => handleDeleteNote(editingNoteId, e)}
                          >
                            <Trash2 size={13} /> {isHindi ? 'हटाएं' : 'Delete'}
                          </button>
                        )}
                      </div>

                      <div className="notes-editor-actions-right">
                        {isCreatingNote && (
                          <button 
                            type="button" 
                            className="history-clear-btn"
                            onClick={() => {
                              setIsCreatingNote(false);
                              if (notesList.length > 0) {
                                handleSelectNote(notesList[0]);
                              }
                            }}
                          >
                            {t.cancel}
                          </button>
                        )}
                        <button type="submit" className="save-note-submit-btn">
                          <Save size={14} /> {isCreatingNote ? t.saveNote2 : t.updateNote}
                        </button>
                      </div>
                    </div>
                  </form>
                ) : (
                  <div className="notes-editor-empty-state">
                    <FileText size={42} style={{ color: 'rgba(216, 211, 101, 0.3)', marginBottom: '12px' }} />
                    <h3>{isHindi ? 'कोई नोट चुना नहीं गया' : 'Select or Create a Note'}</h3>
                    <p>{isHindi ? 'बाईं सूची से एक नोट चुनें या नया नोट बनाना शुरू करें।' : 'Choose a note from the left sidebar or start typing a new research observation.'}</p>
                    <button className="notes-app-new-btn" onClick={handleStartNewNote}>
                      <Plus size={15} /> {t.newNote}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── NODUS Knowledge Base Modal (Cards, Queues & Reasoning Chains) ── */}
      {active === 'knowledge' && (
        <div className="knowledge-modal-backdrop" onClick={() => setActive(null)}>
          <div className="knowledge-center-card" onClick={(e) => e.stopPropagation()}>
            {/* Header */}
            <div className="knowledge-card-header">
              <div className="knowledge-title-cyan">
                <div className="knowledge-cyan-icon-badge">
                  <Lightbulb size={20} />
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <h2 className="knowledge-main-heading">
                      {isHindi ? 'नोडस ज्ञान आधार (NODUS)' : 'NODUS Knowledge Base'}
                    </h2>
                    <span className="knowledge-native-pill">SatQuery Native</span>
                  </div>
                  <p className="knowledge-sub-heading">
                    {isHindi
                      ? 'पुन: प्रयोज्य उपग्रह विश्लेषण कार्ड, प्राथमिकता कतारें और मल्टी-स्टेज रीजनिंग चेन।'
                      : 'Reusable satellite analysis cards, priority queues, and multi-stage reasoning chains.'}
                  </p>
                </div>
              </div>

              <div className="knowledge-header-actions">
                <button className="history-close-btn" onClick={() => setActive(null)} title="Close">
                  <X size={18} />
                </button>
              </div>
            </div>

            {/* Subnav Tabs: Cards vs Chains */}
            <div className="knowledge-subnav-row">
              <div className="knowledge-tab-buttons">
                <button
                  className={`knowledge-subnav-btn ${knowledgeTab === 'cards' ? 'active' : ''}`}
                  onClick={() => setKnowledgeTab('cards')}
                >
                  <Sparkles size={14} /> {isHindi ? 'ज्ञान कार्ड' : 'Knowledge Cards'} ({knowledgeCards.length})
                </button>
                <button
                  className={`knowledge-subnav-btn ${knowledgeTab === 'chains' ? 'active' : ''}`}
                  onClick={() => setKnowledgeTab('chains')}
                >
                  <Layers size={14} /> {isHindi ? 'रीजनिंग चेन' : 'Reasoning Chains'} ({knowledgeChains.length})
                </button>
              </div>

              {knowledgeTab === 'chains' && !isCreatingChain && (
                <button className="knowledge-new-chain-btn" onClick={() => setIsCreatingChain(true)}>
                  <Plus size={14} /> {isHindi ? 'नई चेन बनाएं' : 'New Chain'}
                </button>
              )}
            </div>

            {/* TAB 1: KNOWLEDGE CARDS */}
            {knowledgeTab === 'cards' && (
              <>
                {/* Search & Queue Bar */}
                <div className="knowledge-control-bar">
                  <div className="knowledge-search-input-wrap">
                    <Search size={15} style={{ color: '#00f2fe' }} />
                    <input
                      type="text"
                      className="knowledge-search-input"
                      placeholder={isHindi ? 'शीर्षक, टैग या सारांश खोजें...' : 'Search title, tags, or summary...'}
                      value={knowledgeFilter}
                      onChange={(e) => setKnowledgeFilter(e.target.value)}
                    />
                    {knowledgeFilter && (
                      <button className="history-filter-clear" onClick={() => setKnowledgeFilter('')}>
                        <X size={12} />
                      </button>
                    )}
                  </div>

                  {/* Queue Selector Filter */}
                  <div className="knowledge-queue-pills">
                    {['all', 'default', 'quick', 'q1', 'q2'].map((q) => (
                      <button
                        key={q}
                        className={`knowledge-queue-pill ${selectedQueue === q ? 'active' : ''}`}
                        onClick={() => setSelectedQueue(q)}
                      >
                        {q === 'all' ? (isHindi ? 'सभी कतारें' : 'All Queues') : q}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Cards List */}
                <div className="knowledge-cards-scroll">
                  {(() => {
                    const filtered = knowledgeCards.filter((card) => {
                      const matchesQueue = selectedQueue === 'all' || (card.queue || 'default').toLowerCase() === selectedQueue.toLowerCase();
                      const filter = knowledgeFilter.toLowerCase();
                      const matchesFilter =
                        !filter ||
                        (card.title || '').toLowerCase().includes(filter) ||
                        (card.summary || '').toLowerCase().includes(filter) ||
                        (card.query_text || '').toLowerCase().includes(filter) ||
                        (card.tags || []).some((t) => t.toLowerCase().includes(filter));
                      return matchesQueue && matchesFilter;
                    });

                    if (filtered.length === 0) {
                      return (
                        <div className="knowledge-empty-state">
                          <Lightbulb size={36} style={{ color: 'rgba(0, 242, 254, 0.4)', marginBottom: '10px' }} />
                          <p style={{ margin: 0, fontWeight: 600 }}>
                            {isHindi ? 'कोई ज्ञान कार्ड नहीं मिला' : 'No Knowledge Cards Found'}
                          </p>
                          <span style={{ fontSize: '0.8rem', opacity: 0.6 }}>
                            {isHindi
                              ? 'चैट में किसी भी विश्लेषण को ज्ञान कार्ड के रूप में सहेजें।'
                              : 'Save any AI response in chat using "💡 Save to Knowledge (NODUS)" or clear search filter.'}
                          </span>
                        </div>
                      );
                    }

                    return (
                      <div className="knowledge-cards-grid">
                        {filtered.map((card) => (
                          <div key={card.id} className="knowledge-card-item">
                            <div className="knowledge-card-top">
                              <span className="knowledge-card-title">{card.title}</span>
                              <span className={`knowledge-queue-tag queue-${card.queue || 'default'}`}>
                                {card.queue || 'default'}
                              </span>
                            </div>

                            {card.query_text && (
                              <p className="knowledge-card-query">
                                <strong>Query:</strong> "{card.query_text}"
                              </p>
                            )}

                            <p className="knowledge-card-summary">{card.summary}</p>

                            <div className="knowledge-card-tags">
                              {(card.tags || []).map((tg, idx) => (
                                <span key={idx} className="knowledge-tag-chip">
                                  #{tg}
                                </span>
                              ))}
                            </div>

                            <div className="knowledge-card-footer">
                              <span className="knowledge-card-date">
                                <Clock size={11} /> {new Date(card.created_at || Date.now()).toLocaleDateString()}
                              </span>
                              <div className="knowledge-card-actions">
                                <button
                                  className="knowledge-card-action-btn inject"
                                  onClick={() => handleInjectKnowledge(card.query_text || card.title)}
                                  title="Inject into Query Input"
                                >
                                  <Send size={12} /> {isHindi ? 'क्वेरी में उपयोग करें' : 'Use in Query'}
                                </button>
                                <button
                                  className="knowledge-card-action-btn delete"
                                  onClick={(e) => handleDeleteCard(card.id, e)}
                                  title="Delete Card"
                                >
                                  <Trash2 size={12} />
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    );
                  })()}
                </div>
              </>
            )}

            {/* TAB 2: REASONING CHAINS */}
            {knowledgeTab === 'chains' && (
              <div className="knowledge-chains-container">
                {isCreatingChain ? (
                  <form className="knowledge-chain-builder" onSubmit={handleSaveChain}>
                    <h3 className="chain-builder-heading">
                      <PlusCircle size={16} /> {isHindi ? 'नई नॉलेज चेन बनाएं' : 'Create New Knowledge Chain'}
                    </h3>
                    <input
                      type="text"
                      className="chain-input-text"
                      placeholder="Chain Title (e.g. Coastal Hazard Rapid Assessment Sequence)"
                      value={newChainTitle}
                      onChange={(e) => setNewChainTitle(e.target.value)}
                      required
                    />
                    <textarea
                      className="chain-input-desc"
                      placeholder="Chain Description / Workflow Purpose..."
                      value={newChainDesc}
                      onChange={(e) => setNewChainDesc(e.target.value)}
                    />

                    <div className="chain-card-picker">
                      <label style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 600 }}>
                        {isHindi ? 'चेन में शामिल करने के लिए कार्ड चुनें:' : 'Select Knowledge Cards for this Sequence:'}
                      </label>
                      <div className="chain-card-checklist">
                        {knowledgeCards.map((c) => {
                          const isSelected = selectedChainCardIds.includes(c.id);
                          return (
                            <label key={c.id} className={`chain-pick-row ${isSelected ? 'selected' : ''}`}>
                              <input
                                type="checkbox"
                                checked={isSelected}
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    setSelectedChainCardIds((prev) => [...prev, c.id]);
                                  } else {
                                    setSelectedChainCardIds((prev) => prev.filter((id) => id !== c.id));
                                  }
                                }}
                              />
                              <span style={{ fontWeight: 600, color: '#f1f5f9' }}>{c.title}</span>
                              <span style={{ fontSize: '0.72rem', color: '#94a3b8', marginLeft: 'auto' }}>
                                #{c.queue || 'default'}
                              </span>
                            </label>
                          );
                        })}
                      </div>
                    </div>

                    <div className="chain-builder-actions">
                      <button
                        type="button"
                        className="history-clear-btn"
                        onClick={() => {
                          setIsCreatingChain(false);
                          setSelectedChainCardIds([]);
                        }}
                      >
                        {isHindi ? 'रद्द करें' : 'Cancel'}
                      </button>
                      <button
                        type="submit"
                        className="save-note-submit-btn"
                        disabled={!newChainTitle.trim() || selectedChainCardIds.length === 0}
                      >
                        <Save size={14} /> {isHindi ? 'चेन सहेजें' : 'Save Chain'}
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="knowledge-chains-scroll">
                    {knowledgeChains.length === 0 ? (
                      <div className="knowledge-empty-state">
                        <Layers size={36} style={{ color: 'rgba(0, 242, 254, 0.4)', marginBottom: '10px' }} />
                        <p style={{ margin: 0, fontWeight: 600 }}>
                          {isHindi ? 'कोई रीजनिंग चेन नहीं मिली' : 'No Reasoning Chains Created'}
                        </p>
                        <span style={{ fontSize: '0.8rem', opacity: 0.6 }}>
                          {isHindi
                            ? 'विश्लेषणों को क्रमबद्ध अनुक्रम में जोड़ने के लिए "New Chain" पर क्लिक करें।'
                            : 'Click "New Chain" above to link related analytical steps into an ordered sequence.'}
                        </span>
                      </div>
                    ) : (
                      <div className="knowledge-chains-list">
                        {knowledgeChains.map((chain) => (
                          <div key={chain.id} className="knowledge-chain-card">
                            <div className="chain-card-header">
                              <div>
                                <h4 className="chain-card-title">{chain.title}</h4>
                                <p className="chain-card-desc">{chain.description}</p>
                              </div>
                              <button
                                className="knowledge-card-action-btn delete"
                                onClick={(e) => handleDeleteChain(chain.id, e)}
                                title="Delete Chain"
                              >
                                <Trash2 size={13} />
                              </button>
                            </div>

                            {/* Sequential Steps Timeline */}
                            <div className="chain-steps-track">
                              {(chain.card_ids || []).map((cardId, stepIdx) => {
                                const cardObj = knowledgeCards.find((c) => c.id === cardId);
                                const cardName = cardObj ? cardObj.title : `Knowledge Step (${cardId.slice(0, 8)})`;
                                return (
                                  <div key={stepIdx} className="chain-step-node">
                                    <span className="chain-step-number">Step {stepIdx + 1}</span>
                                    <span className="chain-step-title">{cardName}</span>
                                    {stepIdx < chain.card_ids.length - 1 && (
                                      <span className="chain-step-arrow">➔</span>
                                    )}
                                  </div>
                                );
                              })}
                            </div>

                            <div className="chain-card-footer">
                              <span className="knowledge-card-date">
                                <Clock size={11} /> {new Date(chain.created_at || Date.now()).toLocaleDateString()}
                              </span>
                              <button
                                className="knowledge-card-action-btn inject"
                                onClick={() => handleInjectKnowledge(`Execute sequential analysis workflow: ${chain.title}`)}
                              >
                                <Send size={12} /> {isHindi ? 'चेन निष्पादित करें' : 'Run Chain Query'}
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── About & Team Modal ── */}
      <AboutModal isOpen={active === 'about'} onClose={() => setActive(null)} />
    </>
  );
}

export default GlassSidebar;
