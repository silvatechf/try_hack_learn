import React from 'react';
import { useI18n } from '../i18n/i18nContext';

export default function LearningMap({ missions, onSelect, progress }) {
  const { t } = useI18n();
  const missionsState = progress?.missions || {};

  const isLocked = (mission) => {
    if (!mission.prerequisites || mission.prerequisites.length === 0) return false;
    return mission.prerequisites.some(preReq => missionsState[preReq]?.status !== 'completed');
  };

  const domains = [
    { id: 'application_security', titleKey: 'domains.application_security', fallbackTitle: 'Application Security', tierKey: 'tiers.foundation', fallbackTier: 'FOUNDATION', icon: '🛡️' },
    { id: 'devsecops', titleKey: 'domains.devsecops', fallbackTitle: 'DevSecOps', tierKey: 'tiers.intermediate', fallbackTier: 'INTERMEDIATE', icon: '⚙️' },
    { id: 'cloud_security', titleKey: 'domains.cloud_security', fallbackTitle: 'Cloud & AWS Security', tierKey: 'tiers.intermediate', fallbackTier: 'INTERMEDIATE', icon: '☁️' },
    { id: 'privacy_engineering', titleKey: 'domains.privacy_engineering', fallbackTitle: 'Privacy Engineering', tierKey: 'tiers.specialization', fallbackTier: 'SPECIALIZATION', icon: '🔐' },
    { id: 'ai_security', titleKey: 'domains.ai_security', fallbackTitle: 'AI Security & Governance', tierKey: 'tiers.advanced', fallbackTier: 'ADVANCED', icon: '🤖' }
  ];

  return (
    <div className="max-w-6xl mx-auto p-4 animate-fadeIn">
      <div className="mb-10 border-b border-slate-800 pb-6">
        <h2 className="text-2xl font-black text-slate-100 tracking-tight">{t('map.title') !== 'map.title' ? t('map.title') : 'SECURITY ENGINEERING LAB'}</h2>
        <p className="text-sm text-cyan-500 font-mono mt-2">{t('map.subtitle') !== 'map.subtitle' ? t('map.subtitle') : 'Build, execute and validate defensive architectures against controlled adversarial scenarios.'}</p>
      </div>

      <div className="space-y-12">
        {domains.map(domain => {
          const domainMissions = missions.filter(m => m.domain === domain.id);
          if (domainMissions.length === 0) return null;

          const domainTitle = t(domain.titleKey) !== domain.titleKey ? t(domain.titleKey) : domain.fallbackTitle;
          const domainTier = t(domain.tierKey) !== domain.tierKey ? t(domain.tierKey) : domain.fallbackTier;

          return (
            <div key={domain.id}>
              <div className="flex items-baseline gap-3 mb-4">
                <span className="text-2xl">{domain.icon}</span>
                <h3 className="text-lg font-bold text-slate-200">{domainTitle}</h3>
                <span className="text-[10px] font-mono text-slate-500 border border-slate-700 px-2 py-0.5 rounded uppercase tracking-wider">{domainTier}</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {domainMissions.map((mission) => {
                  const locked = isLocked(mission);
                  const missionRecord = missionsState[mission.mission_id];
                  const isDone = missionRecord?.status === 'completed';

                  const missionNormId = mission.mission_id?.toLowerCase().replace('-', '_');
                  const missionKey = `missions.${missionNormId}.title`;
                  const translatedTitle = t(missionKey);
                  const title = translatedTitle !== missionKey ? translatedTitle : mission.title;

                  const threatKey = `missions.${missionNormId}.threat`;
                  const translatedThreat = t(threatKey);
                  const threat = translatedThreat !== threatKey ? translatedThreat : mission.threat;

                  return (
                    <div
                      key={mission.mission_id}
                      className={`bg-[#0f1722] p-5 rounded-xl border transition-all ${locked ? 'border-slate-800 opacity-60' : 'border-slate-700 hover:border-cyan-500 hover:shadow-[0_0_15px_rgba(34,211,238,0.15)] cursor-pointer'}`}
                      onClick={() => !locked && onSelect(mission)}
                    >
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h4 className="font-bold text-slate-200 text-sm">{title}</h4>
                          <p className="text-[10px] font-mono text-slate-500 uppercase mt-1">{threat}</p>
                        </div>
                        {locked && <span className="text-slate-600 text-lg" title="Locked">🔒</span>}
                        {isDone && <span className="text-emerald-500 text-lg" title="Completed">✅</span>}
                      </div>

                      {missionRecord?.attempts > 0 && (
                        <div className="mb-3 text-[10px] font-mono text-slate-400">
                          {t('map.attempts') !== 'map.attempts' ? t('map.attempts') : 'Attempts'}: <span className="text-slate-200 font-bold">{missionRecord.attempts}</span>
                        </div>
                      )}

                      <div className="mt-4 pt-4 border-t border-slate-800/50 flex justify-between items-center">
                        {!locked ? (
                          <span className="text-[10px] font-bold text-cyan-500 uppercase tracking-widest flex items-center gap-1">
                            {isDone
                              ? (t('map.rerun') !== 'map.rerun' ? t('map.rerun') : 'RE-RUN LAB')
                              : (t('map.start') !== 'map.start' ? t('map.start') : 'START LAB')} <span className="text-lg leading-none">→</span>
                          </span>
                        ) : (
                          <span className="text-[9px] text-rose-500 font-mono uppercase">
                            {t('map.requires') !== 'map.requires' ? t('map.requires') : 'Requires'}: {mission.prerequisites.join(', ')}
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

