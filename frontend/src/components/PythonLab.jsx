import React, { useState, useEffect } from 'react';
import { useI18n } from '../i18n/i18nContext';
import ThreatBriefing from './ThreatBriefing';

const PYTHON_LAB_API_URL = "http://localhost:8002/api/v1/python-lab";

export default function PythonLab({ onBack }) {
  const { t } = useI18n();
  const [exercises, setExercises] = useState([]);
  const [selectedExerciseId, setSelectedExerciseId] = useState('PY-001');
  const [exercise, setExercise] = useState(null);
  const [labMode, setLabMode] = useState('guided'); // guided | assisted | free_code
  const [guidedStep, setGuidedStep] = useState(0);
  const [guidedSelectedOption, setGuidedSelectedOption] = useState(null);
  const [guidedFeedback, setGuidedFeedback] = useState(null);
  const [assistedStep, setAssistedStep] = useState(0);
  const [assistedSelectedOption, setAssistedSelectedOption] = useState(null);
  const [assistedFeedback, setAssistedFeedback] = useState(null);
  const [userCode, setUserCode] = useState('');
  const [execResult, setExecResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isFreeCodeUnlocked, setIsFreeCodeUnlocked] = useState(false);
  const [guidedCompleted, setGuidedCompleted] = useState(false);
  const [codeUpdatedAnim, setCodeUpdatedAnim] = useState(false);
  const [lastInjectedSnippet, setLastInjectedSnippet] = useState('');

  useEffect(() => {
    fetch(`${PYTHON_LAB_API_URL}/exercises`)
      .then(res => res.json())
      .then(data => {
        const list = Array.isArray(data)
          ? data
          : Array.isArray(data?.value)
            ? data.value
            : [];
        if (list.length > 0) {
          setExercises(list);
          setExercise(list[0]);
          setSelectedExerciseId(list[0].exercise_id);
          setUserCode(list[0].starter_code || '');
        }
      })
      .catch(err => console.error("Failed to load exercises", err));
  }, []);

  const handleSelectExercise = (e) => {
    const exId = e.target.value;
    setSelectedExerciseId(exId);
    const found = exercises.find(ex => ex.exercise_id === exId);
    if (found) {
      setExercise(found);
      setUserCode(found.starter_code || '');
      setGuidedStep(0);
      setGuidedSelectedOption(null);
      setGuidedFeedback(null);
      setAssistedStep(0);
      setAssistedSelectedOption(null);
      setAssistedFeedback(null);
      setExecResult(null);
      setIsFreeCodeUnlocked(false);
      setGuidedCompleted(false);
      setCodeUpdatedAnim(false);
      setLastInjectedSnippet('');
    }
  };

  const handleRunCode = async () => {
    setLoading(true);
    setExecResult(null);
    try {
      const res = await fetch(`${PYTHON_LAB_API_URL}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exercise_id: selectedExerciseId,
          student_code: userCode
        })
      });
      const data = await res.json();
      setExecResult(data);
      if (labMode === 'assisted' && data?.evaluation?.passed_all === true) {
        setIsFreeCodeUnlocked(true);
      }
    } catch (err) {
      console.error("Execution failed", err);
      setExecResult({ status: 'ERROR', evaluation: { status: 'ERROR', error: err.toString() } });
    } finally {
      setLoading(false);
    }
  };

  const translateWithFallback = (key, fallback) => {
    if (!key) return fallback;
    const translated = t(key);
    return translated === key ? fallback : translated;
  };

  const handleGuidedSubmit = () => {
    if (!exercise?.pedagogy?.guided?.steps) return;
    const steps = exercise.pedagogy.guided.steps;
    const current = steps[guidedStep];
    if (guidedSelectedOption === current.correct_index) {
      setGuidedFeedback({ correct: true, message: t('pedagogy.correct_feedback') });
      if (guidedStep === steps.length - 1) {
        setGuidedCompleted(true);
      }
    } else {
      setGuidedFeedback({ correct: false, message: t('pedagogy.incorrect_feedback') });
    }
  };

  const handleGuidedNext = () => {
    setGuidedFeedback(null);
    setGuidedSelectedOption(null);
    if (guidedStep < (exercise.pedagogy.guided.steps.length - 1)) {
      setGuidedStep(prev => prev + 1);
    }
  };

  const handleContinueToAssisted = () => {
    setLabMode('assisted');
    setAssistedStep(0);
    setAssistedSelectedOption(null);
    setAssistedFeedback(null);
    setExecResult(null);

    const assistedStarter = exercise?.pedagogy?.assisted?.starter_code;
    if (assistedStarter) {
      setUserCode(assistedStarter);
    }
  };

  const handleAssistedSubmit = () => {
    if (!exercise?.pedagogy?.assisted?.steps) return;
    const steps = exercise.pedagogy.assisted.steps;
    const current = steps[assistedStep];
    if (assistedSelectedOption === current.correct_index) {
      setAssistedFeedback({ correct: true, message: t('python_lab.assisted_completed') });
      if (current.code_snapshot) {
        const previousCode = userCode;
        const nextCode = current.code_snapshot;

        const previousLines = previousCode.split('\n');
        const nextLines = nextCode.split('\n');

        const addedLines = nextLines.filter(line => {
          const trimmed = line.trim();
          const isPlaceholder = /\[\s*.*_BLOCK\s*\]/.test(trimmed);
          const existedBefore = previousLines.some(
            prevLine => prevLine.trim() === trimmed
          );

          return trimmed !== '' && !isPlaceholder && !existedBefore;
        });

        const changedSnippet = addedLines.join('\n').trim();

        setUserCode(nextCode);
        setLastInjectedSnippet(changedSnippet);
        setCodeUpdatedAnim(true);
        setTimeout(() => setCodeUpdatedAnim(false), 1800);
      }
    } else {
      setAssistedFeedback({ correct: false, message: t('python_lab.assisted_incorrect') });
    }
  };

  const handleAssistedNext = () => {
    setAssistedFeedback(null);
    setAssistedSelectedOption(null);
    if (assistedStep < (exercise.pedagogy.assisted.steps.length - 1)) {
      setAssistedStep(prev => prev + 1);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto text-slate-100 font-sans">
      <div className="flex justify-between items-center mb-6 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">{t('python_lab.title')}</h1>
          <p className="text-xs text-slate-400 mt-1">{t('python_lab.subtitle')}</p>
        </div>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-mono rounded-lg transition-colors cursor-pointer"
        >
          {t('lab_back')}
        </button>
      </div>

      <div className="mb-6 flex gap-4 items-center">
        <select
          value={selectedExerciseId}
          onChange={handleSelectExercise}
          className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
        >
          {exercises.map(ex => {
            const exTitle = translateWithFallback(ex.title_id, ex.title);
            return (
              <option key={ex.exercise_id} value={ex.exercise_id}>
                {ex.exercise_id} - {exTitle}
              </option>
            );
          })}
        </select>

        <div className="flex gap-2 border-b border-slate-800">
          <button
            onClick={() => setLabMode('guided')}
            className={`px-3 py-1.5 text-xs font-medium transition-colors ${labMode === 'guided' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            {t('pedagogy.mode_guided')}
          </button>
          <button
            onClick={() => setLabMode('assisted')}
            className={`px-3 py-1.5 text-xs font-medium transition-colors ${labMode === 'assisted' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            {t('pedagogy.mode_assisted')}
          </button>
          <button
            onClick={() => isFreeCodeUnlocked && setLabMode('free_code')}
            disabled={!isFreeCodeUnlocked}
            className={`px-3 py-1.5 text-xs font-medium transition-colors ${!isFreeCodeUnlocked ? 'opacity-50 cursor-not-allowed text-slate-500' : labMode === 'free_code' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-slate-400 hover:text-slate-200'}`}
          >
            {t('pedagogy.mode_free_code')}
          </button>
        </div>
      </div>

      {labMode !== 'free_code' && (
        <ThreatBriefing context={exercise?.threat_context} />
      )}

      {labMode === 'free_code' && (
        <div className="p-5 mb-6 border border-slate-800 rounded-xl bg-slate-900 shadow-md">
          <h3 className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-widest mb-2">
            🚀 {t('exercises.py001.free_code.title')}
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed font-sans">
            {t('exercises.py001.free_code.message')}
          </p>
        </div>
      )}

      {labMode === 'guided' && exercise?.pedagogy?.guided?.steps && (
        <div className="p-5 mb-6 border border-slate-800 rounded-xl bg-slate-900 shadow-md">
          {(() => {
            if (guidedCompleted) {
              return (
                <div className="text-center py-6 space-y-4 animate-fadeIn">
                  <div className="w-12 h-12 rounded-full bg-emerald-950 border border-emerald-800 flex items-center justify-center text-emerald-400 text-xl mx-auto">
                    🎉
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-slate-100 uppercase tracking-widest text-emerald-400 mb-1">
                      {t('exercises.py001.guided.completed_title')}
                    </h3>
                    <p className="text-xs text-slate-300 max-w-lg mx-auto leading-relaxed">
                      {t('exercises.py001.guided.completed_message')}
                    </p>
                  </div>
                  <button
                    onClick={handleContinueToAssisted}
                    className="px-6 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold rounded-lg transition-colors cursor-pointer shadow-lg inline-flex items-center gap-2"
                  >
                    {t('exercises.py001.guided.continue_assisted')} →
                  </button>
                </div>
              );
            }
            const steps = exercise.pedagogy.guided.steps;
            const currentStep = steps[guidedStep];
            return (
              <div>
                <div className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest mb-1">
                  {t('python_lab.step_label')} {guidedStep + 1} / {steps.length}
                </div>
                <h3 className="text-sm font-bold text-slate-200 mb-4">
                  {translateWithFallback(currentStep.question_id, currentStep.question)}
                </h3>

                <div className="space-y-2 mb-4">
                  {currentStep.options.map((opt, idx) => {
                    const optId = currentStep.option_ids?.[idx];
                    const displayOpt = translateWithFallback(optId, opt);
                    return (
                    <label key={idx} className="flex items-center gap-3 p-3 rounded-lg border border-slate-800 bg-slate-950/40 hover:bg-slate-800/50 cursor-pointer transition-colors text-xs">
                      <input
                        type="radio"
                        name={`guided_step_${guidedStep}`}
                        checked={guidedSelectedOption === idx}
                        onChange={() => {
                          setGuidedSelectedOption(idx);
                          setGuidedFeedback(null);
                        }}
                        className="text-cyan-500 focus:ring-0"
                      />
                      <span className="text-slate-300">{displayOpt}</span>
                    </label>
                  );})}
                </div>

                {(!guidedFeedback || !guidedFeedback.correct) ? (
                  <div className="space-y-3">
                    {guidedFeedback && (
                      <div className="p-3 rounded-lg border text-xs bg-red-950/40 border-red-900/50 text-red-300">
                        {guidedFeedback.message}
                      </div>
                    )}
                    <button
                      onClick={handleGuidedSubmit}
                      disabled={guidedSelectedOption === null}
                      className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors cursor-pointer"
                    >
                      {guidedFeedback ? t('pedagogy.try_again') : t('pedagogy.submit')}
                    </button>
                  </div>
                ) : (
                  <div className="p-3 rounded-lg border text-xs flex justify-between items-center bg-emerald-950/40 border-emerald-900/50 text-emerald-300">
                    <span>{guidedFeedback.message}</span>
                    {guidedStep < steps.length - 1 && (
                      <button
                        onClick={handleGuidedNext}
                        className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium rounded transition-colors cursor-pointer"
                      >
                        {t('python_lab.next_step')}
                      </button>
                    )}
                  </div>
                )}
              </div>
            );
          })()}
        </div>
      )}

      {labMode === 'assisted' && exercise?.pedagogy?.assisted?.steps && (
        <div className="p-5 mb-6 border border-slate-800 rounded-xl bg-slate-900 shadow-md">
          {(() => {
            const steps = exercise.pedagogy.assisted.steps;
            const currentStep = steps[assistedStep];
            return (
              <div>
                <div className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest mb-1">
                  {t('python_lab.assisted_step_label')} {assistedStep + 1} / {steps.length}
                </div>
                <h3 className="text-sm font-bold text-slate-200 mb-4">{t(currentStep.question_id)}</h3>

                <div className="space-y-2 mb-4">
                  {currentStep.option_ids.map((optId, idx) => (
                    <label key={idx} className="flex items-center gap-3 p-3 rounded-lg border border-slate-800 bg-slate-950/40 hover:bg-slate-800/50 cursor-pointer transition-colors text-xs font-mono">
                      <input
                        type="radio"
                        name={`assisted_step_${assistedStep}`}
                        checked={assistedSelectedOption === idx}
                        onChange={() => {
                          setAssistedSelectedOption(idx);
                          setAssistedFeedback(null);
                        }}
                        className="text-cyan-500 focus:ring-0"
                      />
                      <span className="text-slate-300">{t(optId)}</span>
                    </label>
                  ))}
                </div>

                {(!assistedFeedback || !assistedFeedback.correct) ? (
                  <div className="space-y-3">
                    {assistedFeedback && (
                      <div className="p-3 rounded-lg border text-xs bg-red-950/40 border-red-900/50 text-red-300">
                        {assistedFeedback.message}
                      </div>
                    )}
                    <button
                      onClick={handleAssistedSubmit}
                      disabled={assistedSelectedOption === null}
                      className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition-colors cursor-pointer"
                    >
                      {assistedFeedback ? t('pedagogy.try_again') : t('pedagogy.submit')}
                    </button>
                  </div>
                ) : (
                  <div className="p-3 rounded-lg border text-xs flex justify-between items-center bg-emerald-950/40 border-emerald-900/50 text-emerald-300">
                    <span>{assistedFeedback.message}</span>
                    {assistedStep < steps.length - 1 && (
                      <button
                        onClick={handleAssistedNext}
                        className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium rounded transition-colors cursor-pointer"
                      >
                        {t('python_lab.next_step')}
                      </button>
                    )}
                  </div>
                )}
              </div>
            );
          })()}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className={`border rounded-xl bg-slate-900 p-4 shadow-md flex flex-col transition-all duration-500 ${codeUpdatedAnim ? 'border-emerald-500 shadow-[0_0_25px_rgba(16,185,129,0.35)] scale-[1.01]' : 'border-slate-800'}`}>
          <div className="mb-2 flex justify-between items-center">
            <div>
              <h3 className="text-sm font-bold text-white">{translateWithFallback(exercise?.title_id, exercise?.title)}</h3>
              <p className="text-xs text-slate-400 mt-0.5">{translateWithFallback(exercise?.description_id, exercise?.description)}</p>
            </div>
            {codeUpdatedAnim && (
              <span className="text-[10px] font-mono bg-emerald-950 text-emerald-400 px-2.5 py-1 rounded-md border border-emerald-800 animate-pulse font-bold tracking-wider uppercase">
                ✨ {t('exercises.py001.assisted.code_updated')}
              </span>
            )}
          </div>

          {codeUpdatedAnim && lastInjectedSnippet && (
            <div className="mb-3 p-2.5 rounded-lg bg-emerald-950/80 border border-emerald-500/60 shadow-[0_0_15px_rgba(16,185,129,0.3)] animate-fadeIn">
              <div className="flex items-center justify-between text-[10px] font-mono text-emerald-400 mb-1 font-bold">
                <span>{t('exercises.py001.assisted.snapshot_injected')}:</span>
              </div>
              <pre className="text-[11px] font-mono text-emerald-300 overflow-x-auto p-1 bg-emerald-950/50 rounded">{lastInjectedSnippet.startsWith('+') ? lastInjectedSnippet : '+ ' + lastInjectedSnippet}</pre>
            </div>
          )}

          <div className="flex-1 my-3">
            <textarea
              value={userCode}
              onChange={(e) => setUserCode(e.target.value)}
              rows={12}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 font-mono text-xs text-cyan-300 focus:outline-none focus:border-cyan-500 leading-relaxed"
              spellCheck={false}
            />
          </div>

          <button
            onClick={handleRunCode}
            disabled={
              loading ||
              (
                labMode === 'assisted' &&
                exercise?.pedagogy?.assisted?.steps &&
                assistedStep < exercise.pedagogy.assisted.steps.length - 1
              )
            }
            className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-bold rounded-lg transition-colors cursor-pointer shadow-lg"
          >
            {loading ? t('python_lab.running_tests') : t('python_lab.run_code')}
          </button>
        </div>

        <div className="border border-slate-800 rounded-xl bg-slate-900 p-4 shadow-md flex flex-col">
          <h3 className="text-sm font-bold text-white mb-2">{t('python_lab.execution_results')}</h3>

          <div className="flex-1 bg-slate-950 border border-slate-800 rounded-lg p-4 font-mono text-xs overflow-y-auto max-h-[350px]">
            {!execResult && (
              <span className="text-slate-500">{t('python_lab.run_prompt')}</span>
            )}

            {execResult && execResult.evaluation && (
              <div>
                <div className={`mb-3 font-bold ${execResult.evaluation.passed_all ? 'text-emerald-400' : 'text-red-400'}`}>
                  {execResult.evaluation.passed_all ? `✅ ${t('python_lab.passed_success')}` : `❌ ${t('python_lab.failed_errors')}`}
                  {execResult.evaluation.results && ` (${execResult.evaluation.results.filter(r => r.passed).length} / ${execResult.evaluation.results.length} ${t('python_lab.tests_passed_summary')})`}
                </div>

                {execResult.evaluation.results && execResult.evaluation.results.map((res, idx) => (
                  <div key={idx} className={`mb-3 p-3 rounded border font-mono text-xs ${res.passed ? 'border-emerald-900/50 bg-emerald-950/20 text-emerald-300' : 'border-red-900/50 bg-red-950/20 text-red-300'}`}>
                    <div className="font-bold mb-1 flex items-center gap-1.5">
                      <span>{res.passed ? '✅' : '❌'}</span>
                      <span>{t('python_lab.test_label')} {res.test_idx !== undefined ? res.test_idx + 1 : idx + 1} — {res.passed ? t('python_lab.test_passed') : t('python_lab.test_failed')}</span>
                    </div>
                    <div className="pl-4 space-y-0.5 text-[11px] text-slate-300">
                      <div><span className="text-slate-500">{t('python_lab.test_expected')}:</span> {JSON.stringify(res.expected)}</div>
                      <div><span className="text-slate-500">{t('python_lab.test_received')}:</span> {JSON.stringify(res.output)}</div>
                    </div>
                  </div>
                ))}
              </div>
                )}

              {execResult?.pedagogical_result && (
                  <div className="mt-4 p-4 rounded-lg border border-sky-900/50 bg-sky-950/20">
                    <h4 className="text-sm font-bold text-sky-300 mb-3">
                      {t('python_lab.pedagogical_result')}
                    </h4>

                    <div className="space-y-2 text-xs">
                      <div>
                        <span className="text-slate-500">{t('python_lab.outcome')}:</span>{' '}
                        <span className="font-bold">
                          {translateWithFallback(
                            `python_lab.${String(execResult.pedagogical_result.outcome || '').toLowerCase()}`,
                            execResult.pedagogical_result.outcome || 'UNKNOWN'
                          )}
                        </span>
                      </div>

                      <div>
                        <span className="text-slate-500">{t('python_lab.feedback')}:</span>{' '}
                        {translateWithFallback(
                          {
                            'python_lab.feedback.mastered': 'python_lab.feedback_mastered',
                            'python_lab.feedback.partial': 'python_lab.feedback_partial',
                            'python_lab.feedback.failed': 'python_lab.feedback_failed',
                            'python_lab.feedback.syntax_error': 'python_lab.feedback_syntax_error',
                            'python_lab.feedback.timeout': 'python_lab.feedback_timeout',
                            'python_lab.feedback.execution_error': 'python_lab.feedback_execution_error',
                            'python_lab.feedback.runtime_error': 'python_lab.feedback_runtime_error'
                          }[execResult.pedagogical_result.feedback_key] ||
                          execResult.pedagogical_result.feedback_key,
                          execResult.pedagogical_result.feedback_key || 'UNKNOWN'
                        )}
                      </div>

                      <div>
                        <span className="text-slate-500">{t('python_lab.next_step_result')}:</span>{' '}
                        {translateWithFallback(
                          {
                            'python_lab.next_step.mastered': 'python_lab.next_step_mastered',
                            'python_lab.next_step.partial': 'python_lab.next_step_partial',
                            'python_lab.next_step.failed': 'python_lab.next_step_failed',
                            'python_lab.next_step.syntax_error': 'python_lab.next_step_syntax_error',
                            'python_lab.next_step.timeout': 'python_lab.next_step_timeout',
                            'python_lab.next_step.execution_error': 'python_lab.next_step_execution_error',
                            'python_lab.next_step.runtime_error': 'python_lab.next_step_runtime_error'
                          }[execResult.pedagogical_result.next_step_key] ||
                          execResult.pedagogical_result.next_step_key,
                          execResult.pedagogical_result.next_step_key || 'UNKNOWN'
                        )}
                      </div>

                      {execResult.pedagogical_result.concepts?.length > 0 && (
                        <div>
                          <span className="text-slate-500">{t('python_lab.concepts')}:</span>{' '}
                          {execResult.pedagogical_result.concepts.join(', ')}
                        </div>
                      )}

                      {execResult.pedagogical_result.score && (
                        <div>
                          <span className="text-slate-500">{t('python_lab.score')}:</span>{' '}
                          {execResult.pedagogical_result.score.passed}{' '}
                          {t('python_lab.score_separator')}{' '}
                          {execResult.pedagogical_result.score.total}
                        </div>
                      )}
                    </div>
                  </div>

            )}
          </div>
        </div>
      </div>
    </div>
  );
}
