import React from 'react';
import { useI18n } from '../i18n/i18nContext';

export default function ControlInspector({ control, onClose }) {
  const { t } = useI18n();
  if (!control) return null;

  const controlI18n = control.control_id
    ? `debrief.controls.${control.control_id}`
    : null;

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 max-w-lg w-full p-6 rounded-2xl shadow-2xl space-y-6">
        <div className="flex justify-between items-start border-b border-slate-800 pb-4">
          <div>
            <span className="text-[10px] font-mono text-emerald-400 uppercase tracking-widest bg-emerald-950 px-2 py-0.5 rounded border border-emerald-900">
              {t('inspector.title')}
            </span>
            <h3 className="text-xl font-black text-slate-100 mt-1">🛡️ {controlI18n ? t(`${controlI18n}.name`) : control.name}</h3>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 text-lg font-bold px-2 py-1 rounded bg-slate-800"
          >
            ✕
          </button>
        </div>

        <div className="space-y-4 text-xs text-slate-300">
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-1">
            <span className="text-slate-500 font-bold uppercase block text-[10px]">{t('inspector.layer')}</span>
            <p className="text-slate-200 font-mono capitalize">{controlI18n ? t(`${controlI18n}.layer`) : control.layer}</p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-500 font-bold uppercase block text-[10px]">{t('inspector.latency')}</span>
              <p className="text-emerald-400 font-mono font-bold mt-0.5">+{control.tradeoffs?.latency_ms || 2}ms</p>
            </div>
            <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
              <span className="text-slate-500 font-bold uppercase block text-[10px]">{t('inspector.complexity')}</span>
              <p className="text-slate-200 font-mono font-bold mt-0.5 capitalize">{control.tradeoffs?.complexity
  ? t(`inspector.complexity_${control.tradeoffs.complexity.toLowerCase()}`)
  : t('inspector.low')}</p>
            </div>
          </div>

          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-1">
            <span className="text-slate-500 font-bold uppercase block text-[10px]">{t('inspector.rationale')}</span>
            <p className="leading-relaxed text-slate-300 font-sans">
              {control.rationale || t('inspector.rationale_default')}
            </p>
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            onClick={onClose}
            className="bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold py-2 px-6 rounded-xl text-xs transition-all"
          >
            {t('inspector.close')}
          </button>
        </div>
      </div>
    </div>
  );
}