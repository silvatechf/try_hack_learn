import React, { useState, useEffect } from 'react';
import { useI18n } from '../i18n/i18nContext';

const PYTHON_LAB_API_URL = "http://localhost:8002/api/v1/python-lab";

export default function PythonLab({ onBack }) {
    const { t } = useI18n();
    const [exercises, setExercises] = useState([]);
    const [selectedId, setSelectedId] = useState('');
    const [code, setCode] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch(`${PYTHON_LAB_API_URL}/exercises`)
            .then(res => res.json())
            .then(data => {
                setExercises(data);
                if (data.length > 0) {
                    setSelectedId(data[0].exercise_id);
                    setCode(data[0].starter_code || '');
                }
            })
            .catch(err => setError(err.message));
    }, []);

    const handleSelect = (e) => {
        const id = e.target.value;
        setSelectedId(id);
        const ex = exercises.find(x => x.exercise_id === id);
        if (ex) setCode(ex.starter_code || '');
        setResult(null);
    };

    const handleRun = async () => {
        setLoading(true);
        setError(null);
        setResult(null);
        try {
            const res = await fetch(`${PYTHON_LAB_API_URL}/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    exercise_id: selectedId,
                    student_code: code
                })
            });
            if (!res.ok) throw new Error("Execution failed with status " + res.status);
            const data = await res.json();
            setResult(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const ex = exercises.find(x => x.exercise_id === selectedId);

    return (
        <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto', color: '#fff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
                <h2>{t('lab_title', 'Python Security Lab')}</h2>
                <button onClick={onBack} style={{ padding: '8px 16px', cursor: 'pointer' }}>
                    {t('lab_back', 'Back to Map')}
                </button>
            </div>

            {error && <div style={{ color: '#ff4d4f', marginBottom: '15px' }}>Error: {error}</div>}

            <div style={{ display: 'flex', gap: '20px' }}>
                {/* Panel Esquerdo: Seleção e Info */}
                <div style={{ flex: '1', backgroundColor: '#1e1e1e', padding: '15px', borderRadius: '8px' }}>
                    <select 
                        value={selectedId} 
                        onChange={handleSelect} 
                        style={{ width: '100%', marginBottom: '15px', padding: '8px', backgroundColor: '#2d2d2d', color: '#fff', border: '1px solid #444' }}
                    >
                        {exercises.map(e => (
                            <option key={e.exercise_id} value={e.exercise_id}>
                                {e.exercise_id} - {e.title}
                            </option>
                        ))}
                    </select>

                    {ex && (
                        <div>
                            <p><strong>{t('lab_difficulty', 'Difficulty')}:</strong> {ex.difficulty}</p>
                            <p style={{ marginTop: '10px' }}>{ex.description}</p>
                            <h4 style={{ marginTop: '15px', color: '#aaa' }}>{t('lab_objectives', 'Learning Objectives')}:</h4>
                            <ul style={{ paddingLeft: '20px' }}>
                                {ex.learning_objectives?.map((obj, i) => <li key={i}>{obj}</li>)}
                            </ul>
                        </div>
                    )}
                </div>

                {/* Panel Direito: Editor e Resultados */}
                <div style={{ flex: '2', display: 'flex', flexDirection: 'column' }}>
                    <textarea
                        value={code}
                        onChange={e => setCode(e.target.value)}
                        style={{ 
                            width: '100%', 
                            height: '250px', 
                            fontFamily: 'monospace', 
                            padding: '10px', 
                            backgroundColor: '#000', 
                            color: '#00ff00',
                            border: '1px solid #444',
                            borderRadius: '4px'
                        }}
                    />
                    <button 
                        onClick={handleRun} 
                        disabled={loading || !selectedId} 
                        style={{ 
                            marginTop: '10px', 
                            padding: '12px', 
                            backgroundColor: '#0052cc', 
                            color: 'white', 
                            border: 'none', 
                            borderRadius: '4px',
                            cursor: loading ? 'not-allowed' : 'pointer'
                        }}
                    >
                        {loading ? 'Executing...' : t('lab_run_code', 'Run Code')}
                    </button>

                    {/* Área de Resultados */}
                    {result && (
                        <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#1e1e1e', border: '1px solid #333', borderRadius: '4px' }}>
                            <h3 style={{ borderBottom: '1px solid #333', paddingBottom: '10px' }}>
                                {t('lab_results', 'Execution Results')} <span style={{ fontSize: '0.8em', color: '#888' }}>({result.duration_ms?.toFixed(0)} ms)</span>
                            </h3>
                            
                            {result.status !== 'EXECUTED' ? (
                                <div style={{ color: '#ff4d4f', marginTop: '10px' }}>
                                    <p>Status: {result.status}</p>
                                    {result.message && <p>{result.message}</p>}
                                    {result.stderr && <pre style={{ backgroundColor: '#000', padding: '10px' }}>{result.stderr}</pre>}
                                </div>
                            ) : (
                                <div style={{ marginTop: '10px' }}>
                                    <h4 style={{ color: result.evaluation?.passed_all ? '#4caf50' : '#ff4d4f' }}>
                                        {result.evaluation?.passed_all ? t('lab_passed_all', 'All tests passed!') : t('lab_failed', 'Some tests failed or encountered errors.')}
                                    </h4>
                                    
                                    {result.evaluation?.status && result.evaluation.status !== 'SUCCESS' && (
                                        <div style={{ color: '#ff4d4f', margin: '10px 0' }}>{result.evaluation.message}</div>
                                    )}

                                    <div style={{ marginTop: '15px' }}>
                                        {result.evaluation?.results?.map((r, i) => (
                                            <div key={i} style={{ padding: '8px', borderBottom: '1px solid #333' }}>
                                                <strong>Test {i + 1}:</strong> {r.passed ? <span style={{color: '#4caf50'}}>✅ Passed</span> : <span style={{color: '#ff4d4f'}}>❌ Failed</span>}
                                                {!r.passed && (
                                                    <div style={{ fontSize: '0.9em', color: '#aaa', marginTop: '5px', backgroundColor: '#000', padding: '5px' }}>
                                                        {r.error ? `Error: ${r.error}` : `Expected: ${r.expected} | Output: ${r.output}`}
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}