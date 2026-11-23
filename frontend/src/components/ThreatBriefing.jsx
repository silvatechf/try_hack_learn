import React, { useState } from 'react';
import { useI18n } from '../i18n/i18nContext';

export default function ThreatBriefing({ context }) {
  const { t } = useI18n();
  const [isOpen, setIsOpen] = useState(false);

  if (!context) return null;

  const title = t(context.title_id);
  const scenario = t(context.scenario_id);
  const objective = t(context.objective_id);

  const briefingTitle = t('exercises.py001.threat.briefing_title');
  const viewContextText = t('exercises.py001.threat.view_context');
  const hideContextText = t('exercises.py001.threat.hide_context');
  const scenarioLabel = t('exercises.py001.threat.scenario_label');
  const objectiveLabel = t('exercises.py001.threat.objective_label');

  return (
    <div className="mb-6 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-md transition-all">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 bg-slate-950/50 hover:bg-slate-900 flex justify-between items-center text-left transition-colors cursor-pointer"
      >
        <div className="flex items-center gap-2">
          <span className="text-cyan-400 text-xs">🛡️</span>
          <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-widest">
            {briefingTitle}: <span className="text-cyan-400">{title}</span>
          </span>
        </div>

        <span className="text-xs font-mono text-slate-500 underline">
          {isOpen ? hideContextText : viewContextText}
        </span>
      </button>

      {isOpen && (
        <div className="p-4 space-y-3 border-t border-slate-800 text-xs animate-fadeIn">
          <div>
            <span className="text-slate-500 font-bold uppercase block text-[10px] mb-0.5">
              {scenarioLabel}
            </span>
            <p className="text-slate-300 leading-relaxed font-sans">
              {scenario}
            </p>
          </div>

          <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
            <span className="text-cyan-500 font-bold uppercase block text-[10px] mb-0.5">
              {objectiveLabel}
            </span>
            <p className="text-slate-200 font-mono">
              {objective}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}