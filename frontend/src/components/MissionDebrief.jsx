import React, { useState } from 'react';

export default function MissionDebrief({ result, onBack, onRetry }) {
  const [showJson, setShowJson] = useState(false);
  const sdr = result?.security_decision_record || {};
  const isValidated = sdr.status === 'VALIDATED';

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn">
      <div className={`p-6 rounded-xl border flex justify-between items-center ${isValidated ? 'bg-emerald-950/20 border-emerald-600 text-emerald-400' : 'bg-rose-950/20 border-rose-600 text-rose-400'}`}>
        <h2 className="text-xl font-bold">{isValidated ? 'ARCHITECTURE VALIDATED' : 'ARCHITECTURAL TRADE-OFF VIOLATION'}</h2>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {/* Mitigation Card */}
        <div className="bg-[#0f1722] p-4 rounded-lg border border-slate-800 shadow-inner">
          <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Observed Mitigation</p>
          <p className="text-xl font-mono font-black text-slate-200 mt-1">{sdr.observed?.prevented} / {sdr.observed?.total_probes}</p>
          <p className="text-sm font-mono text-cyan-400 mt-1">{sdr.observed?.mitigation_percent}%</p>
        </div>
        
        {/* Causal Latency Card (Refactored) */}
        <div className="bg-[#0f1722] p-4 rounded-lg border border-slate-800 shadow-inner flex flex-col justify-between">
          <div>
            <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider flex justify-between">
              <span>Baseline (Network)</span>
              <span className="text-slate-400">{sdr.latency?.baseline_p95_ms?.toFixed(2)}ms</span>
            </p>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-800/50">
            <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider flex justify-between">
              <span>Architectural Delta</span>
              <span className={`font-black ${sdr.latency?.within_budget ? 'text-cyan-400' : 'text-rose-400'}`}>
                {sdr.latency?.delta_ms > 0 ? '+' : ''}{sdr.latency?.delta_ms?.toFixed(2)}ms
              </span>
            </p>
          </div>
        </div>

        {/* Availability Card */}
        <div className="bg-[#0f1722] p-4 rounded-lg border border-slate-800 shadow-inner">
          <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Observed Availability</p>
          <p className="text-xl font-mono font-black text-slate-200 mt-1">{sdr.observed?.availability_percent}%</p>
        </div>
      </div>

      <div className="bg-[#0f1722] p-6 rounded-xl border border-slate-800">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest border-b border-slate-700 pb-2 mb-4">Engineering Trade-off / Rationale</h3>
        <p className="text-sm text-slate-300 leading-relaxed">{sdr.architectural_rationale}</p>
        
        {sdr.pedagogical_feedback && sdr.pedagogical_feedback.length > 0 && (
          <div className="mt-6 space-y-4">
            <h4 className="text-[11px] font-bold text-rose-400 uppercase tracking-widest flex items-center gap-2">
              <span>⚠️</span> Failure Must Teach: Lessons Learned
            </h4>
            {sdr.pedagogical_feedback.map((lesson, idx) => (
              <div key={idx} className="bg-slate-900 border-l-4 border-rose-500 p-4 rounded shadow-sm">
                <div className="flex gap-2 items-center mb-2">
                  <span className="text-[10px] font-mono text-cyan-500 uppercase">{lesson.layer}</span>
                  <span className="text-xs font-bold text-slate-200">{lesson.control}</span>
                </div>
                <div className="space-y-3">
                  <div>
                    <span className="text-[10px] uppercase text-slate-500 block mb-0.5">Why it failed</span>
                    <p className="text-sm text-slate-300 leading-relaxed">{lesson.why_it_failed}</p>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase text-slate-500 block mb-0.5">What this demonstrates</span>
                    <p className="text-sm text-slate-400 leading-relaxed">{lesson.demonstrates}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* JSON Inspector para auditar a execução causal (Opcional) */}
      <div className="bg-slate-900 p-4 rounded-xl border border-slate-800">
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Security Decision Record (Evidence)</h3>
          <button onClick={() => setShowJson(!showJson)} className="text-[10px] text-cyan-500 hover:text-cyan-400 underline font-mono transition-colors">Inspect JSON</button>
        </div>
        {showJson && <pre className="mt-3 p-4 bg-black text-[11px] text-cyan-400 font-mono rounded overflow-auto max-h-64 border border-slate-800 custom-scrollbar">{JSON.stringify(sdr, null, 2)}</pre>}
      </div>

      <div className="flex justify-between pt-4">
        <button onClick={onRetry} className="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded transition-colors shadow">← Revise Architecture</button>
        <button onClick={onBack} className="px-6 py-2.5 bg-cyan-700 hover:bg-cyan-600 text-white font-bold text-xs rounded transition-colors shadow-lg">Return to Dashboard →</button>
      </div>
    </div>
  );
}