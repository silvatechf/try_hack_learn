import React from 'react';

export default function RoadmapView() {
  const steps = [
    { id: 1, title: 'Learn', desc: 'Identify the threat vector and mission objectives.' },
    { id: 2, title: 'Investigate', desc: 'Study the target architecture and risk context.' },
    { id: 3, title: 'Hypothesize', desc: 'Select and inspect defensive control trade-offs.' },
    { id: 4, title: 'Experiment', desc: 'Deploy controls to the isolated sandbox.' },
    { id: 5, title: 'Measure', desc: 'Analyze telemetry and security delta.' },
    { id: 6, title: 'Evidence', desc: 'Generate and review the Security Decision Record.' }
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-xl mb-8">
      <h3 className="text-sm font-bold text-emerald-400 uppercase tracking-widest mb-6">SentinelForge Engineering Lifecycle</h3>
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        {steps.map((step, idx) => (
          <div key={step.id} className="relative flex flex-col items-center text-center space-y-2">
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-emerald-500/50 flex items-center justify-center text-emerald-400 font-bold text-xs">
              {step.id}
            </div>
            <h4 className="text-xs font-bold text-slate-200">{step.title}</h4>
            <p className="text-[10px] text-slate-500 hidden md:block">{step.desc}</p>
            {idx < steps.length - 1 && (
              <div className="absolute top-4 left-[60%] w-full h-[1px] bg-slate-800 hidden md:block" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}