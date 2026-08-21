import React from 'react';

export default function MissionBrief({ mission, onStart }) {
  if (!mission) return null;
  return (
    <div className="max-w-4xl mx-auto bg-[#0f1722] border border-slate-800 rounded-xl p-8 shadow-2xl animate-fadeIn">
      <div className="flex items-center gap-3 mb-6">
        <span className="text-xs font-mono bg-cyan-950/40 text-cyan-500 px-2 py-1 rounded border border-cyan-900">{mission.mission_id}</span>
        <h2 className="text-2xl font-black text-slate-100">{mission.title}</h2>
      </div>
      
      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="bg-slate-900 p-5 rounded-lg border border-slate-800 shadow-inner">
          <h3 className="text-[10px] font-bold text-cyan-500 uppercase tracking-widest mb-2">🎯 Learning Objective</h3>
          <p className="text-sm text-slate-300 leading-relaxed">{mission.learning_objective}</p>
        </div>
        <div className="bg-slate-900 p-5 rounded-lg border border-slate-800 shadow-inner">
          <h3 className="text-[10px] font-bold text-rose-400 uppercase tracking-widest mb-2">⚠️ Threat Vector Context</h3>
          <p className="text-sm text-slate-300 leading-relaxed">{mission.threat_context || mission.threat}</p>
        </div>
      </div>

      {mission.vulnerable_code && (
        <div className="mb-8">
          <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2 flex items-center gap-2">
            <span>🔍</span> Target Application Source Code (Vulnerable)
          </h3>
          <div className="bg-black p-4 rounded-lg border border-slate-700 shadow-inner overflow-x-auto">
            <pre className="text-[11px] font-mono text-emerald-400/90 leading-relaxed">
              <code>{mission.vulnerable_code}</code>
            </pre>
          </div>
        </div>
      )}

      <div className="flex justify-between items-center bg-slate-900 p-4 rounded-lg border border-slate-800 mb-8 font-mono text-[11px] text-slate-400 shadow-inner">
        <span className="uppercase tracking-widest">Engineering Constraints:</span>
        <div className="flex gap-6">
          <span className="flex items-center gap-2">Max Control Overhead: <span className="text-cyan-400 font-bold">&lt; {mission.constraints?.max_control_overhead_ms || mission.constraints?.max_latency_ms}ms</span></span>
          <span className="flex items-center gap-2">Min Availability: <span className="text-cyan-400 font-bold">&gt; {mission.constraints?.min_availability_percent}%</span></span>
        </div>
      </div>

      <div className="text-right border-t border-slate-800 pt-6">
        <button onClick={onStart} className="px-8 py-3 bg-cyan-700 hover:bg-cyan-600 text-white font-bold rounded shadow-lg transition-all transform hover:scale-105 flex items-center gap-2 ml-auto">
          Enter Security Arena <span>🚀</span>
        </button>
      </div>
    </div>
  );
}