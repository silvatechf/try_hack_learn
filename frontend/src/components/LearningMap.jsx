import React from 'react';

export default function LearningMap({ missions, onSelect, progress }) {
  const missionsState = progress?.missions || {};

  const isLocked = (mission) => {
    if (!mission.prerequisites || mission.prerequisites.length === 0) return false;
    return mission.prerequisites.some(preReq => missionsState[preReq]?.status !== 'completed');
  };

  // Agrupamento lógico por Domínios (Os 5 Invariáveis)
  const domains = [
    { id: 'application_security', title: 'Application Security', tier: 'FOUNDATION', icon: '🛡️' },
    { id: 'devsecops', title: 'DevSecOps', tier: 'INTERMEDIATE', icon: '⚙️' },
    { id: 'cloud_security', title: 'Cloud & AWS Security', tier: 'INTERMEDIATE', icon: '☁️' },
    { id: 'privacy_engineering', title: 'Privacy Engineering', tier: 'SPECIALIZATION', icon: '🔐' },
    { id: 'ai_security', title: 'AI Security & Governance', tier: 'ADVANCED', icon: '🤖' }
  ];

  return (
    <div className="max-w-6xl mx-auto p-4 animate-fadeIn">
      <div className="mb-10 border-b border-slate-800 pb-6">
        <h2 className="text-2xl font-black text-slate-100 tracking-tight">SECURITY ENGINEERING LAB</h2>
        <p className="text-sm text-cyan-500 font-mono mt-2">Build, execute and validate defensive architectures against controlled adversarial scenarios.</p>
      </div>
      
      <div className="space-y-12">
        {domains.map(domain => {
          const domainMissions = missions.filter(m => m.domain === domain.id);
          if (domainMissions.length === 0) return null;

          return (
            <div key={domain.id}>
              <div className="flex items-baseline gap-3 mb-4">
                <span className="text-2xl">{domain.icon}</span>
                <h3 className="text-lg font-bold text-slate-200">{domain.title}</h3>
                <span className="text-[10px] font-mono text-slate-500 border border-slate-700 px-2 py-0.5 rounded uppercase tracking-wider">{domain.tier}</span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {domainMissions.map((mission) => {
                  const locked = isLocked(mission);
                  const missionRecord = missionsState[mission.mission_id];
                  const isDone = missionRecord?.status === 'completed';

                  return (
                    <div 
                      key={mission.mission_id} 
                      className={`bg-[#0f1722] p-5 rounded-xl border transition-all ${locked ? 'border-slate-800 opacity-60' : 'border-slate-700 hover:border-cyan-500 hover:shadow-[0_0_15px_rgba(34,211,238,0.15)] cursor-pointer'}`} 
                      onClick={() => !locked && onSelect(mission)}
                    >
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h4 className="font-bold text-slate-200 text-sm">{mission.title}</h4>
                          <p className="text-[10px] font-mono text-slate-500 uppercase mt-1">{mission.threat}</p>
                        </div>
                        {locked && <span className="text-slate-600 text-lg" title="Locked">🔒</span>}
                        {isDone && <span className="text-emerald-500 text-lg" title="Completed">✅</span>}
                      </div>

                      {missionRecord?.attempts > 0 && (
                        <div className="mb-3 text-[10px] font-mono text-slate-400">
                          Attempts: <span className="text-slate-200 font-bold">{missionRecord.attempts}</span>
                        </div>
                      )}

                      <div className="mt-4 pt-4 border-t border-slate-800/50 flex justify-between items-center">
                        {!locked ? (
                          <span className="text-[10px] font-bold text-cyan-500 uppercase tracking-widest flex items-center gap-1">
                            {isDone ? 'RE-RUN LAB' : 'START LAB'} <span className="text-lg leading-none">→</span>
                          </span>
                        ) : (
                          <span className="text-[9px] text-rose-500 font-mono uppercase">
                            Requires: {mission.prerequisites.join(', ')}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}