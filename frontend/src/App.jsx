import React, { useState, useEffect } from 'react';
import LearningMap from './components/LearningMap';
import MissionBrief from './components/MissionBrief';
import MissionDebrief from './components/MissionDebrief';
import ControlInspector from './components/ControlInspector';
import { useI18n } from './i18n/i18nContext';
import PythonLab from './components/PythonLab';

export default function App() {
  const { t, lang, toggleLang } = useI18n();
  const [view, setView] = useState('HOME');
  const [missions, setMissions] = useState([]);
  const [selectedMission, setSelectedMission] = useState(null);
  const [availableControls, setAvailableControls] = useState([]);
  const [controlStack, setControlStack] = useState([]);
  const [inspectingControl, setInspectingControl] = useState(null);

  // Fase 2: Estado de progresso versionado e tolerante a falhas (sentinelforge.learning.v1)
  const [learningProgress, setLearningProgress] = useState(() => {
    try {
      const saved = localStorage.getItem("sentinelforge.learning.v1");
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && typeof parsed === 'object' && parsed.missions) {
          return parsed;
        }
      }
      // Migração de legado: sf_progress
      const legacy = localStorage.getItem("sf_progress");
      if (legacy) {
        const old = JSON.parse(legacy);
        const migrated = { missions: {} };
        Object.keys(old).forEach(id => {
          migrated.missions[id] = { status: 'completed', attempts: 1, timestamp: new Date().toISOString() };
        });
        return migrated;
      }
    } catch (e) {
      console.error("Error loading learning progress from localStorage, resetting state.", e);
    }
    return { missions: {} };
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/missions/list').then(r => r.json()).then(setMissions).catch(() => { });
    fetch('http://localhost:8000/api/v1/controls/list').then(r => r.json()).then(setAvailableControls).catch(() => { });
  }, []);

  const handleDropToStack = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const cid = e.dataTransfer.getData('text/plain');
    if (cid) {
      const ctrl = availableControls.find(c => c.control_id === cid);
      if (ctrl) setControlStack(prev => [...prev, ctrl]);
    }
  };

  const removeControl = (idx) => {
    setControlStack(prev => prev.filter((_, i) => i !== idx));
  };

  const executeArchitecture = async () => {
    if (controlStack.length === 0 || !selectedMission) return;
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/arena/deploy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mission_id: selectedMission.mission_id,
          control_ids: controlStack.map(c => c.control_id)
        })
      });
      const data = await res.json();
      setResult(data);

      const sdrStatus = data?.security_decision_record?.status;
      const isCompleted = sdrStatus === 'VALIDATED' || sdrStatus === 'MISSION VALIDATED';
      const missionId = selectedMission.mission_id;

      // Atualizar progresso e histórico local (Fase 2)
      setLearningProgress(prev => {
        const currentMissionData = prev.missions?.[missionId] || { attempts: 0 };
        const updatedMissions = {
          ...prev.missions,
          [missionId]: {
            status: isCompleted ? 'completed' : 'failed',
            attempts: (currentMissionData.attempts || 0) + 1,
            lastResult: sdrStatus,
            timestamp: new Date().toISOString()
          }
        };
        const newProgress = { ...prev, missions: updatedMissions };
        try {
          localStorage.setItem("sentinelforge.learning.v1", JSON.stringify(newProgress));
          // Manter compatibilidade com sf_progress legado
          const legacyCompleted = {};
          Object.keys(updatedMissions).forEach(mId => {
            if (updatedMissions[mId].status === 'completed') {
              legacyCompleted[mId] = true;
            }
          });
          localStorage.setItem("sf_progress", JSON.stringify(legacyCompleted));
        } catch (err) {
          console.error("Failed to save progress to localStorage", err);
        }
        return newProgress;
      });

      setView('DEBRIEF');
    } catch (err) {
      console.error("Execution error", err);
    } finally {
      setLoading(false);
    }
  };

  const currentLatency = controlStack.reduce((sum, c) => sum + (c.tradeoffs?.latency_ms || 0), 0);
  const latencyBudget = selectedMission?.constraints?.max_control_overhead_ms || selectedMission?.constraints?.max_latency_ms || 50;

  const missionControls = (selectedMission?.available_controls && selectedMission.available_controls.length > 0)
    ? availableControls.filter(c => selectedMission.available_controls.includes(c.control_id))
    : availableControls;

  return (
    <div className="min-h-screen p-6 max-w-7xl mx-auto font-sans bg-[#0a0f14] text-slate-100 flex flex-col">
      <header className="flex justify-between items-center border-b border-slate-800 pb-4 mb-6">
        <div>
          <h1 className="text-2xl font-black text-cyan-400">{t('arena.title')}</h1>
          <p className="text-xs text-slate-500 font-mono uppercase">{t('arena.subtitle')}</p>
        </div>
        <div className="flex gap-2">
          <button onClick={toggleLang} className="px-3 py-1 bg-slate-900 border border-slate-700 rounded text-xs hover:border-cyan-500 transition-all">{lang.toUpperCase()}</button>
          {view !== 'HOME' && <button onClick={() => { setView('HOME'); setControlStack([]); }} className="px-3 py-1 bg-slate-800 rounded text-xs hover:bg-slate-700 transition-all">Back</button>}
        </div>
        {view === 'HOME' && (
          <button
            onClick={() => setView('LAB')}
            style={{ marginRight: '15px', cursor: 'pointer' }}
          >
            {t('nav_python_lab', 'Python Lab')}
          </button>
        )}
      </header>

      <main className="flex-grow">
        {view === 'HOME' && <LearningMap missions={missions} onSelect={(m) => { setSelectedMission(m); setView('BRIEF'); }} progress={learningProgress} />}
        {view === 'BRIEF' && <MissionBrief mission={selectedMission} onStart={() => setView('ARENA')} />}
        {view === 'DEBRIEF' && <MissionDebrief result={result} mission={selectedMission} onRetry={() => { setControlStack([]); setView('ARENA'); }} onBack={() => setView('HOME')} />}
        {view === 'LAB' && (
  <PythonLab onBack={() => setView('HOME')} />
)}
        {view === 'ARENA' && selectedMission && (
          <div className="grid grid-cols-12 gap-6 pb-20 animate-fadeIn">
            <div className="col-span-4 bg-[#0f1722] p-4 rounded-xl border border-slate-800 h-[650px] flex flex-col">
              <h4 className="text-xs font-bold text-slate-400 uppercase mb-4">Available Controls</h4>
              <div className="space-y-3 overflow-y-auto pr-2 custom-scrollbar flex-grow">
                {missionControls.map(ctrl => (
                  <div key={ctrl.control_id} draggable onDragStart={(e) => { e.dataTransfer.setData('text/plain', ctrl.control_id); }} className="bg-slate-900 p-3 rounded border border-slate-700 cursor-grab hover:border-cyan-500 hover:bg-[#151f2e] transition-all shadow-sm active:cursor-grabbing">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-[9px] bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800 text-cyan-500 uppercase">{ctrl.layer}</span>
                      <button onClick={() => setInspectingControl(ctrl)} className="text-[10px] text-slate-400 hover:text-cyan-400 underline">Inspect</button>
                    </div>
                    <p className="font-bold text-sm text-slate-200">{ctrl.name}</p>
                    <div className="flex justify-between items-center mt-2 border-t border-slate-800 pt-1">
                      <span className="text-[9px] text-slate-500 uppercase">Impact</span>
                      <span className="text-[10px] text-rose-400 font-mono font-bold">+{ctrl.tradeoffs?.latency_ms}ms</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="col-span-8 flex flex-col h-[650px]">
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-xs font-bold text-slate-400 uppercase">{t('stack.title')}</h4>
                <div className="flex gap-4 text-[10px] font-mono bg-slate-900 px-3 py-1.5 rounded border border-slate-700 shadow-inner">
                  <span className={currentLatency > latencyBudget ? 'text-rose-500 font-bold' : 'text-cyan-400 font-bold'}>
                    {t('metrics.latency')}: {currentLatency}ms
                  </span>
                  <span className="text-slate-500">| {t('metrics.budget')}: {latencyBudget}ms</span>
                </div>
              </div>

              <div
                onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
                onDragLeave={() => setIsDragOver(false)}
                onDrop={handleDropToStack}
                className={`flex-grow border-2 border-dashed rounded-xl flex flex-col items-center py-6 overflow-y-auto transition-all duration-200 ${isDragOver ? 'bg-cyan-950/20 border-cyan-500 shadow-[inset_0_0_50px_rgba(34,211,238,0.1)]' : 'bg-[#0f1722] border-slate-700'}`}
              >
                <div className="w-64 text-center border-b border-slate-600 pb-2 mb-2 text-xs font-mono text-cyan-500 tracking-widest uppercase flex items-center justify-center gap-2">
                  <span>☁️</span> INTERNET
                </div>

                {controlStack.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full opacity-50 pointer-events-none">
                    <span className="text-4xl mb-3">🖱️</span>
                    <p className="text-sm font-bold text-slate-400">Drag modules here</p>
                    <p className="text-xs text-slate-500 mt-1">to build your defense pipeline</p>
                  </div>
                ) : (
                  controlStack.map((ctrl, idx) => (
                    <React.Fragment key={`${ctrl.control_id}-${idx}`}>
                      <div className="text-slate-600 my-1 animate-pulse">↓</div>
                      <div className="w-72 bg-slate-900 border-l-4 border-cyan-600 p-3 flex justify-between items-center shadow-lg transform transition-all hover:scale-[1.02]">
                        <div>
                          <p className="text-[9px] text-cyan-500 uppercase tracking-wider">{ctrl.layer}</p>
                          <p className="font-bold text-sm text-slate-100">{ctrl.name}</p>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-[10px] text-rose-400 font-mono">+{ctrl.tradeoffs?.latency_ms}ms</span>
                          <button onClick={() => removeControl(idx)} className="text-slate-500 hover:text-rose-500 text-lg transition-colors p-1">×</button>
                        </div>
                      </div>
                    </React.Fragment>
                  ))
                )}

                {controlStack.length > 0 && <div className="text-slate-600 my-1">↓</div>}
                <div className="w-64 text-center border-t border-slate-600 pt-2 mt-2 text-xs font-mono text-emerald-500 tracking-widest uppercase flex items-center justify-center gap-2">
                  <span>🎯</span> APP TARGET
                </div>
              </div>

              <div className="mt-4 flex gap-4">
                <button onClick={() => setControlStack([])} className="px-6 py-3 bg-slate-800 text-xs rounded font-bold border border-slate-700 hover:bg-slate-700 transition-colors">{t('btn.clear')}</button>
                <button onClick={executeArchitecture} disabled={loading || controlStack.length === 0} className="flex-grow bg-cyan-700 hover:bg-cyan-600 text-white font-bold py-3 rounded text-sm transition-colors shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                  {loading ? (
                    <><span className="animate-spin">⚙️</span> Compiling Architecture...</>
                  ) : (
                    <>{t('btn.deploy')} 🚀</>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
      <ControlInspector control={inspectingControl} onClose={() => setInspectingControl(null)} />
    </div>
  );
}