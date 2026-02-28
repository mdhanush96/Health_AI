import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { symptomAPI } from '../api';
import { Sidebar } from './Dashboard';

const SeverityBadge = ({ level }) => {
  const normalized = String(level || '').toUpperCase();
  const classes = {
    LOW: 'badge badge-low',
    MEDIUM: 'badge badge-medium',
    HIGH: 'badge badge-high',
    CRITICAL: 'badge badge-critical',
  };
  return <span className={classes[normalized] || 'badge'}>{normalized || 'UNKNOWN'}</span>;
};

const SymptomForm = () => {
  const navigate = useNavigate();
  const [symptomText, setSymptomText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!symptomText.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const analysisResponse = await symptomAPI.analyze(symptomText);
      const analysisData = analysisResponse.data;

      setResult(analysisData);

      if (analysisData.emergency === true) {
        toast.error('⚠️ CRITICAL: Seek immediate medical attention!', { autoClose: false });
      } else {
        toast.success('Analysis complete!');
      }
    } catch (err) {
      toast.error('Analysis failed. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const exampleSymptoms = [
    'I have chest pain and shortness of breath for the past 2 hours',
    'Severe headache, nausea and sensitivity to light',
    'Persistent cough, fever of 101°F, and fatigue for 3 days',
    'Joint pain and stiffness in both knees, worse in the morning',
  ];

  return (
    <div className="layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-header">
          <h1>🩺 Symptom Analysis</h1>
          <p>Describe your symptoms and get AI-powered classification and guidance</p>
        </div>

        <div className="card">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Describe Your Symptoms</label>
              <textarea
                className="form-textarea"
                value={symptomText}
                onChange={(e) => setSymptomText(e.target.value)}
                placeholder="Describe your symptoms in detail. Include duration, severity, location, and any associated symptoms..."
                minLength={5}
                maxLength={2000}
                required
              />
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                {symptomText.length}/2000 characters
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <p className="form-label">Quick Examples</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {exampleSymptoms.map((example, i) => (
                  <button
                    key={i}
                    type="button"
                    className="btn btn-outline"
                    style={{ fontSize: '0.8rem', padding: '6px 12px' }}
                    onClick={() => setSymptomText(example)}
                  >
                    {example.substring(0, 40)}...
                  </button>
                ))}
              </div>
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading || symptomText.length < 5}>
              {loading ? <><span className="spinner" /> Analyzing...</> : '🔍 Analyze Symptoms'}
            </button>
          </form>
        </div>

        {result && (
          <>
            {/* Emergency Alert */}
            {result.emergency === true && (
              <div className={`emergency-banner ${String(result.severity).toUpperCase() === 'CRITICAL' ? 'critical' : ''}`}>
                <div className="emergency-title">
                  🚨 {String(result.severity).toUpperCase()} ALERT
                </div>
                <p style={{ marginBottom: '8px' }}>{result.action}</p>
                <strong>Recommended Specialist: {result.specialist}</strong>
              </div>
            )}

            {/* Analysis Results */}
            {result.emergency !== true && (
            <div className="card">
              <h2 className="card-title">📊 Analysis Results</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '20px' }}>
                <div>
                  <div className="form-label">Condition</div>
                  <strong style={{ textTransform: 'capitalize', fontSize: '1.1rem' }}>
                    {String(result.condition || '').replaceAll('_', ' ')}
                  </strong>
                </div>
                <div>
                  <div className="form-label">Severity</div>
                  <SeverityBadge level={result.severity} />
                </div>
                <div>
                  <div className="form-label">Specialist</div>
                  <strong>{result.specialist}</strong>
                </div>
              </div>

              <div className="form-label">Educational Explanation (RAG)</div>
              <div className="response-box">
                {result.educational_explanation}
              </div>

              {result.safe_otc?.length > 0 && (
                <div style={{ marginTop: '12px' }}>
                  <span className="form-label">Safe OTC Options: </span>
                  <div className="sources-list">
                    {result.safe_otc.map((med, i) => (
                      <span key={i} className="source-tag">{med}</span>
                    ))}
                  </div>
                </div>
              )}

              <div style={{ marginTop: '16px' }}>
                <div className="form-label">Diet</div>
                <ul className="rec-list">
                  {(result.diet || []).slice(0, 5).map((item, i) => <li key={`diet-${i}`}>{item}</li>)}
                </ul>
                <div className="form-label">Exercise</div>
                <ul className="rec-list">
                  {(result.exercise || []).slice(0, 4).map((item, i) => <li key={`exercise-${i}`}>{item}</li>)}
                </ul>
                <div className="form-label">Lifestyle</div>
                <ul className="rec-list">
                  {(result.lifestyle || []).slice(0, 4).map((item, i) => <li key={`life-${i}`}>{item}</li>)}
                </ul>
              </div>

              <div style={{ marginTop: '20px', display: 'flex', gap: '12px' }}>
                <button
                  className="btn btn-primary"
                  onClick={() => navigate('/recommendations')}
                >
                  💊 Get Recommendations
                </button>
                <button
                  className="btn btn-outline"
                  onClick={() => { setResult(null); setSymptomText(''); }}
                >
                  New Analysis
                </button>
              </div>
            </div>
            )}
          </>
        )}
      </main>
    </div>
  );
};

export default SymptomForm;
