import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Mic, MicOff, Send, Zap, CheckCircle, Sparkles, X, Heart, Settings, Trophy, Camera, Scan, Eye } from 'lucide-react';
import ProfilePage from './ProfilePage';

// 🔱 FONT INJECTION: Lexend is scientifically proven to help with reading focus.
const fontLink = document.createElement('link');
fontLink.href = 'https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;600;800&display=swap';
fontLink.rel = 'stylesheet';
document.head.appendChild(fontLink);

const API_BASE = import.meta.env.VITE_API_URL || "https://smart-companion-api.onrender.com";

export default function SmartCompanionUI() {
  const [sessionId] = useState(() => localStorage.getItem('soul_sid') || `sid_${Math.random().toString(36).slice(2, 9)}`);
  const [messages, setMessages] = useState([{ type: 'ai', text: "Your Smart Companion is here to help you focus and achieve your goals." }]);
  const [input, setInput] = useState("");
  const [energy, setEnergy] = useState(7); 
  const [activeStep, setActiveStep] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [showProfile, setShowProfile] = useState(true); 
  const [isPulsing, setIsPulsing] = useState(false);

  // 📸 VISION STATE
  const [isScanning, setIsScanning] = useState(false);
  const [previewUrl, setPreviewUrl] = useState(null);
  const fileInputRef = useRef(null);

  // 🎮 GAME STATE
  const [gameStats, setGameStats] = useState({ xp: 0, level: 1, streak: 0 });

  const scrollRef = useRef(null);
  const recognitionRef = useRef(null);

  // 🔊 STRICT FEMININE VOICE ENGINE
  const speak = (text) => {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel(); 
    const cleanText = text.replace(/\*/g, '').replace(/_/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    const voices = window.speechSynthesis.getVoices();
    
    const femaleVoice = 
      voices.find(v => v.name === 'Google US English' && v.name.includes('Female')) || 
      voices.find(v => v.name.includes('Female')) || 
      voices.find(v => v.name.includes('Zira') || v.name.includes('Google')) ||
      voices[0];

    utterance.voice = femaleVoice;
    utterance.pitch = 1.1; 
    utterance.rate = 0.95; 
    window.speechSynthesis.speak(utterance);
  };

  // 💓 HEARTBEAT
  useEffect(() => {
    const heartbeat = setInterval(() => { 
        sendEvent("USER_INPUT", "HEARTBEAT"); 
    }, 45000);
    return () => clearInterval(heartbeat);
  }, []);

  useEffect(() => {
    window.speechSynthesis.getVoices();
  }, []);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.onresult = (e) => handleSend(e.results[0][0].transcript);
      recognitionRef.current.onend = () => setIsListening(false);
    }
  }, []);

  // 📸 VISION HANDLER
  const triggerScan = () => fileInputRef.current.click();

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Show preview on the left side
    setPreviewUrl(URL.createObjectURL(file));
    setIsScanning(true);
    addMessage('user', "[ENVIRONMENT SCAN INITIATED]");

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(`${API_BASE}/vision/${sessionId}`, formData);
      handleBackendDecision(res.data.data);
    } catch (err) {
      addMessage('ai', "Vision sync failed. Neural link too weak for visual data.");
    } finally {
      setIsScanning(false);
    }
  };

  const handleSend = (textOverride) => {
    const val = textOverride || input;
    if (!val.trim()) return;
    addMessage('user', val);
    sendEvent("USER_INPUT", val);
    setInput("");
  };

  const addMessage = (sender, text) => {
    setMessages(prev => [...prev, { type: sender, text }]);
    if (sender === 'ai') speak(text); 
  };

  const sendEvent = async (type, payload) => {
    if (payload !== "HEARTBEAT") {
        setLoading(true);
        setActiveStep(null);
    }
    try {
      const res = await axios.post(`${API_BASE}/event`, {
        session_id: sessionId,
        event_type: type,
        payload: String(payload),
        energy_level: parseInt(energy)
      });

      if (payload === "HEARTBEAT") {
        setIsPulsing(true);
        setTimeout(() => setIsPulsing(false), 1500);
      }

      handleBackendDecision(res.data.data);
    } catch (err) {
      if (payload !== "HEARTBEAT") addMessage('ai', "Neural link severed. Is the server running?");
    } finally { setLoading(false); }
  };

  const handleBackendDecision = (decision) => {
    if (!decision || decision.text === "IDLE") return;

    if (decision.xp_total !== undefined) {
        setGameStats({
            xp: decision.xp_total,
            level: decision.level,
            streak: decision.streak
        });
    }

    if (decision.type === 'celebration') {
        setActiveStep(decision);
        speak(`Fantastic job! ${decision.text}. You gained ${decision.gained_xp} experience points.`);
        return;
    }

    if (decision.type === 'step' || decision.actions || decision.options) {
        setActiveStep(decision);
        speak(decision.text); 
    } else {
        addMessage('ai', decision.text);
    }
  };

  const badges = [
    { name: "Initiate", minLvl: 1, icon: "🛡️" },
    { name: "Focus Knight", minLvl: 3, icon: "⚔️" },
    { name: "Task Titan", minLvl: 5, icon: "💎" },
    { name: "Task King", minLvl: 10, icon: "👑" },
  ];
  const unlockedBadges = badges.filter(b => gameStats.level >= b.minLvl);
  const currentRank = unlockedBadges[unlockedBadges.length - 1]?.name || "Recruit";

  return (
    <div className="h-screen w-screen bg-[#050507] text-slate-100 flex flex-col overflow-hidden relative" style={{ fontFamily: "'Lexend', sans-serif" }}>
      
      <input type="file" ref={fileInputRef} onChange={handleFileUpload} accept="image/*" className="hidden" />

      {/* BACKGROUND AMBIENCE */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] border rounded-full transition-all duration-1000 ${isPulsing ? 'border-cyan-500 shadow-[0_0_50px_rgba(6,182,212,0.2)] scale-110' : 'border-white/[0.02] scale-100'} animate-[ping_10s_linear_infinite]`}></div>
      </div>

      {/* TOP HEADER */}
      <header className="h-24 border-b border-white/5 bg-black/40 backdrop-blur-xl flex items-center justify-between px-10 z-50 shrink-0">
        <div className="flex items-center gap-6">
          <div className={`p-3 rounded-full transition-all duration-500 ${isPulsing ? 'bg-cyan-500 shadow-[0_0_25px_cyan]' : 'bg-slate-800'}`}>
            <Heart className={`${isPulsing ? 'text-black' : 'text-cyan-400'}`} size={24} fill={isPulsing ? "currentColor" : "none"} />
          </div>
          <div>
              <h1 className="text-xs font-black tracking-[0.3em] uppercase opacity-50">Smart Companion OS</h1>
              <div className="flex items-center gap-2 text-cyan-400 text-sm font-bold">
                <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></div>
                NEURAL LINK ACTIVE
              </div>
          </div>
        </div>

        <div className="flex-1 max-w-sm mx-12">
            <div className="flex justify-between text-[11px] uppercase font-bold text-cyan-500 mb-2">
                <span>Focus Energy</span>
                <span>{energy * 10}%</span>
            </div>
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden border border-white/5">
                <div className="h-full bg-cyan-500 transition-all duration-1000" style={{ width: `${energy * 10}%` }}></div>
            </div>
        </div>

        <button onClick={() => setShowProfile(true)} className="p-4 hover:bg-white/5 rounded-2xl transition-all border border-white/5 bg-black/20">
            <Settings size={24} className="text-slate-400" />
        </button>
      </header>

      {/* WORKSPACE */}
      <main className="flex-1 flex relative overflow-hidden">
        
        {/* 📸 LEFT SIDE: VISION SCANNER */}
        <div className="hidden lg:flex w-80 border-r border-white/5 bg-black/20 flex-col p-6 gap-6 shrink-0 z-30">
            <div className="flex items-center gap-2 text-[10px] font-black text-slate-500 uppercase tracking-widest">
                <Eye size={14} /> Environment Sensor
            </div>
            
            <div className={`relative flex-1 rounded-[2rem] border-2 border-dashed transition-all overflow-hidden flex flex-col items-center justify-center gap-4 ${isScanning ? 'border-cyan-500 bg-cyan-500/5' : 'border-white/10 bg-white/[0.02]'}`}>
                {previewUrl ? (
                    <>
                        <img src={previewUrl} className="absolute inset-0 w-full h-full object-cover opacity-40" alt="Scan preview" />
                        <div className="relative z-10 flex flex-col items-center">
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center ${isScanning ? 'bg-cyan-500 animate-bounce' : 'bg-white/10'}`}>
                                <Scan className={isScanning ? 'text-black' : 'text-white'} />
                            </div>
                            <p className="mt-4 text-[10px] font-bold uppercase tracking-tighter text-center px-4">
                                {isScanning ? "Processing..." : "Sync Complete"}
                            </p>
                        </div>
                    </>
                ) : (
                    <div className="text-center p-6 cursor-pointer" onClick={triggerScan}>
                        <Camera size={40} className="mx-auto mb-4 text-slate-600" />
                        <p className="text-[10px] font-bold text-slate-500 uppercase leading-relaxed text-center">Tap to sync<br/>visual context</p>
                    </div>
                )}
            </div>
            <button onClick={triggerScan} className="py-4 rounded-2xl bg-white/5 border border-white/10 text-[10px] font-black uppercase tracking-widest hover:bg-white/10 transition-all">
                New Scan
            </button>
        </div>

        {/* 💬 CENTER: CHAT AREA & INTEGRATED INPUT */}
        <div className="flex-1 flex flex-col relative border-r border-white/5 bg-black/5">
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-10 space-y-8 scrollbar-hide pb-32">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.type === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-4 duration-500`}>
                <div className={`max-w-[85%] lg:max-w-[65%] p-6 rounded-[1.5rem] ${m.type === 'user' ? 'bg-cyan-600 text-white shadow-xl' : 'bg-slate-900/60 border border-white/10 backdrop-blur-md'}`}>
                  <p className="text-lg leading-relaxed font-light">{m.text}</p>
                </div>
              </div>
            ))}
          </div>

          {/* MINIMAL CHAT INPUT - ANCHORED BUT SLEEK */}
          <div className="px-10 py-6 bg-gradient-to-t from-[#050507] to-transparent z-[110]">
              <div className="max-w-2xl mx-auto flex items-center gap-3 bg-white/[0.03] border border-white/5 p-1.5 pl-6 rounded-full backdrop-blur-md focus-within:border-cyan-500/50 transition-all">
                <input 
                  value={input} 
                  onChange={(e) => setInput(e.target.value)} 
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()} 
                  placeholder="Talk here..." 
                  className="flex-1 bg-transparent border-none focus:ring-0 text-sm py-3 opacity-60 focus:opacity-100" 
                />
                <button onClick={() => handleSend()} className="p-3 bg-white/5 text-cyan-400 rounded-full hover:bg-cyan-500 hover:text-black transition-all">
                  <Send size={18} />
                </button>
              </div>
          </div>
        </div>

        {/* 🎮 RIGHT CHANNEL: RPG & VOICE */}
        <div className="w-96 flex flex-col p-8 gap-6 shrink-0 relative bg-black/20">
            <div className="flex flex-col items-end gap-3 z-50">
                <div className="w-full bg-slate-900/90 border border-white/10 p-6 rounded-[2.5rem] flex items-center justify-between backdrop-blur-xl shadow-2xl">
                    <div className="text-left">
                        <p className="text-[10px] font-black text-yellow-500 uppercase tracking-widest">{currentRank}</p>
                        <p className="text-2xl font-black text-white leading-none">LVL {gameStats.level}</p>
                        <p className="text-[10px] font-bold opacity-40 uppercase mt-1">{gameStats.xp} Total XP</p>
                    </div>
                    <div className="flex gap-2 p-3 bg-white/5 rounded-2xl border border-white/5">
                        {unlockedBadges.map((b, i) => (
                            <span key={i} title={b.name} className="text-2xl drop-shadow-lg">{b.icon}</span>
                        ))}
                    </div>
                </div>
            </div>

            <div className="flex-1"></div>

            {/* VOICE ORB - PRIMARY INTERRUPT TOOL */}
            <div className="flex justify-end pb-4 z-[110]">
                <button 
                    onClick={() => { 
                        if (isListening) recognitionRef.current?.stop(); 
                        else { setIsListening(true); recognitionRef.current?.start(); } 
                    }} 
                    className={`w-32 h-32 rounded-full flex items-center justify-center transition-all duration-500 shadow-2xl relative ${
                        isListening ? 'bg-red-500 scale-110 shadow-red-900/60' : 'bg-cyan-600 hover:scale-105 shadow-cyan-900/40'
                    }`}
                >
                    {isListening && <div className="absolute inset-0 bg-red-500 rounded-full animate-ping opacity-50"></div>}
                    {isListening ? <MicOff size={48} className="text-white relative z-10" /> : <Mic size={48} className="text-white relative z-10" />}
                </button>
            </div>
        </div>
      </main>

      {/* 🔱 TASK MODAL */}
      {activeStep && (
        <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-3xl flex items-center justify-center p-8 overflow-y-auto">
          <div className={`w-full max-w-4xl rounded-[4rem] p-16 shadow-2xl animate-in zoom-in duration-300 my-auto ${activeStep.type === 'celebration' ? 'bg-cyan-500 text-black' : 'bg-white text-black'}`}>
            <div className="flex justify-between items-center mb-8">
                <div className="flex items-center gap-4">
                    <Trophy className={activeStep.type === 'celebration' ? 'text-black' : 'text-cyan-500'} size={32} />
                    <span className="text-sm font-black tracking-[0.5em] uppercase opacity-60">Neural Protocol</span>
                </div>
                <button onClick={() => setActiveStep(null)} className="p-4 hover:bg-black/10 rounded-full transition-all"><X size={40}/></button>
            </div>
            
            <div className="max-h-[45vh] overflow-y-auto pr-4 custom-scrollbar">
                <h2 className="text-5xl md:text-7xl font-extrabold tracking-tighter leading-tight mb-8">
                    {activeStep.text}
                </h2>
            </div>

            <div className="grid grid-cols-1 gap-4 mt-8">
                {(activeStep.actions || activeStep.options || ["DONE"]).map((act, idx) => (
                    <button 
                        key={idx}
                        onClick={() => { sendEvent("USER_ACTION", act.payload || act); setActiveStep(null); }}
                        className="py-12 bg-cyan-600 text-white rounded-[3rem] font-black text-4xl flex items-center justify-center gap-6 hover:bg-cyan-500 transition-all shadow-xl active:scale-95"
                    >
                        <CheckCircle size={48} /> {act.label || act}
                    </button>
                ))}
            </div>
          </div>
        </div>
      )}

      {showProfile && (
        <div className="fixed inset-0 z-[200] bg-[#050507] flex items-center justify-center">
            <ProfilePage sessionId={sessionId} energy={energy} setEnergy={setEnergy} onComplete={() => setShowProfile(false)} />
        </div>
      )}
    </div>
  );}