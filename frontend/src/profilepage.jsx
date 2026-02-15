import React, { useState } from 'react';
import { Zap, Brain, Target, Flame, ShieldAlert, ZapOff, Clock, Gauge, Activity, ChevronRight, Eye, Layers } from 'lucide-react';
import axios from 'axios';

const ProfilePage = ({ sessionId, energy, setEnergy, onComplete }) => {
  const [loading, setLoading] = useState(false);
  
  const [responses, setResponses] = useState({
    condition: "adhd", // New: Core condition selection
    difficulty_starting_tasks: true,
    time_blindness: true,
    easily_overwhelmed: true,
    loses_focus_easily: true,
    needs_encouragement: true,
    visual_clarity_mode: true, // Replaced Step Breakdown with Dyslexia-relevant feature
    hyperfocus_traps: false,
    sensory_overload: false
  });

  const toggleTrait = (key) => {
    setResponses(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleStart = async () => {
    setLoading(true);
    try {
      await axios.post(`http://localhost:8000/onboarding/calibrate`, {
        session_id: sessionId,
        responses: responses,
        energy_level: energy
      });
      onComplete(); 
    } catch (err) {
      console.error("Calibration failed", err);
      onComplete(); 
    } finally {
      setLoading(false);
    }
  };

  const DiagnosticTile = ({ id, label, icon: Icon, active }) => (
    <button 
      onClick={() => toggleTrait(id)}
      className={`w-full p-6 rounded-3xl border transition-all flex items-center gap-5 ${
        active 
        ? 'bg-cyan-500/10 border-cyan-500 shadow-[0_0_20px_rgba(6,182,212,0.2)]' 
        : 'bg-black/40 border-white/5 hover:border-white/20'
      }`}
    >
      <div className={`p-3 rounded-2xl flex-shrink-0 ${active ? 'bg-cyan-500 text-black' : 'bg-slate-800 text-slate-400'}`}>
        <Icon size={24} />
      </div>
      <span className={`text-lg font-bold tracking-tight text-left ${active ? 'text-white' : 'text-slate-400'}`}>{label}</span>
    </button>
  );

  return (
    <div className="fixed inset-0 w-full h-full bg-[#050507] text-slate-100 overflow-y-auto scrollbar-hide z-[300]">
      <div className="max-w-7xl mx-auto w-full p-8 lg:p-16">
        
        {/* HEADER */}
        <div className="mb-16">
            <div className="flex items-center gap-3 mb-4">
                <div className="h-1 w-12 bg-cyan-500 shadow-[0_0_10px_cyan]"></div>
                <span className="text-cyan-500 font-black tracking-[0.4em] uppercase text-xs">Biometric Sync Required</span>
            </div>
            <h1 className="text-6xl lg:text-8xl font-black tracking-tighter leading-none">
                CALIBRATE <br/> <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">COMPANION</span>
            </h1>
        </div>

        {/* CONDITION SELECTOR - NEW DROPDOWN */}
        <div className="mb-12 p-8 bg-white/[0.03] border border-white/10 rounded-[3rem]">
            <p className="text-xs font-black text-cyan-500 uppercase tracking-widest mb-4">Select Primary Neuro-Profile</p>
            <select 
                value={responses.condition}
                onChange={(e) => setResponses({...responses, condition: e.target.value})}
                className="w-full bg-black border border-white/10 text-white p-6 rounded-2xl text-2xl font-bold focus:ring-2 focus:ring-cyan-500 outline-none appearance-none cursor-pointer"
            >
                <option value="adhd">ADHD (Attention & Initiation)</option>
                <option value="dyslexia">Dyslexia (Reading & Visual Processing)</option>
                <option value="autism">Autism (Sensory & Routine)</option>
                <option value="executive">Executive Dysfunction (General)</option>
            </select>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
          
          {/* LEFT: PRIMARY */}
          <div className="lg:col-span-4 space-y-4">
            <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-6 px-2">Core Diagnostics</h3>
            <DiagnosticTile id="difficulty_starting_tasks" label="Task Paralysis" icon={ZapOff} active={responses.difficulty_starting_tasks} />
            <DiagnosticTile id="time_blindness" label="Time Blindness" icon={Clock} active={responses.time_blindness} />
            <DiagnosticTile id="easily_overwhelmed" label="High Anxiety" icon={ShieldAlert} active={responses.easily_overwhelmed} />
            <DiagnosticTile id="loses_focus_easily" label="Focus Drifting" icon={Target} active={responses.loses_focus_easily} />
          </div>

          {/* MIDDLE: ENERGY BAR */}
          <div className="lg:col-span-4 bg-white/[0.02] border border-white/5 rounded-[4rem] p-10 flex flex-col items-center justify-center relative overflow-hidden h-fit min-h-[500px]">
            <h3 className="text-xs font-black text-cyan-500 uppercase tracking-widest mb-12">Neural Energy (Spoons)</h3>
            <div className="flex flex-col-reverse items-center gap-3 w-full max-w-[120px]">
                {[...Array(10)].map((_, i) => (
                    <div key={i} className={`w-full h-6 rounded-lg transition-all duration-700 ${i < energy ? 'bg-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.4)]' : 'bg-slate-800/30'}`} style={{ opacity: (i + 1) * 0.1 }} />
                ))}
            </div>
            <div className="mt-12 w-full text-center">
                <input type="range" min="1" max="10" value={energy} onChange={(e) => setEnergy(parseInt(e.target.value))} className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500 mb-6" />
                <p className="text-6xl font-black text-white">{energy * 10}%</p>
                <p className="text-[10px] text-slate-500 uppercase font-black mt-2 tracking-widest">Cognitive Fuel</p>
            </div>
          </div>

          {/* RIGHT: SECONDARY & SUBMIT */}
          <div className="lg:col-span-4 flex flex-col gap-4">
            <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-6 px-2">Neural Directives</h3>
            <DiagnosticTile id="needs_encouragement" label="Positive Reinforcement" icon={Flame} active={responses.needs_encouragement} />
            <DiagnosticTile id="visual_clarity_mode" label="Visual Clarity (Dyslexia)" icon={Eye} active={responses.visual_clarity_mode} />
            <DiagnosticTile id="hyperfocus_traps" label="Hyperfocus Alerts" icon={Gauge} active={responses.hyperfocus_traps} />
            <DiagnosticTile id="sensory_overload" label="Minimalist Mode" icon={Activity} active={responses.sensory_overload} />
            
            <div className="mt-8 p-8 bg-white text-black rounded-[3rem] shadow-[0_20px_50px_rgba(255,255,255,0.1)] group cursor-pointer hover:scale-[1.02] transition-transform" onClick={handleStart}>
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-[10px] font-black uppercase tracking-widest opacity-50 mb-1">Calibration Ready</p>
                        <h4 className="text-2xl font-black italic uppercase">Initiate Link</h4>
                    </div>
                    <div className="w-16 h-16 bg-black rounded-full flex items-center justify-center text-white group-hover:scale-110 transition-transform flex-shrink-0">
                        {loading ? <div className="w-6 h-6 border-2 border-white border-t-transparent animate-spin rounded-full"></div> : <ChevronRight size={32} />}
                    </div>
                </div>
            </div>
          </div>
        </div>

        {/* FOOTER */}
        <div className="mt-20 pb-12 text-center border-t border-white/5 pt-12">
            <p className="text-[10px] font-black text-slate-600 uppercase tracking-[0.5em]">
                Neural Architecture Protocol | Smart Companion OS v3.0
            </p>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;