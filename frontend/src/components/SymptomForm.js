import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { symptomAPI, emergencyAPI } from '../api';
import { Sidebar } from './Dashboard';

const RiskBadge = ({ level }) => {
  const classes = {
    LOW: 'badge badge-low',
    MEDIUM: 'badge badge-medium',
    HIGH: 'badge badge-high',
    CRITICAL: 'badge badge-critical',
  };
  return <span className={classes[level] || 'badge'}>{level}</span>;
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
      // Check for emergency first
      const emergencyResponse = await emergencyAPI.check(symptomText);
      const emergencyData = emergencyResponse.data;

      // Perform symptom analysis
      const analysisResponse = await symptomAPI.analyze(symptomText);
      const analysisData = analysisResponse.data;

      setResult({ analysis: analysisData, emergency: emergencyData });

      if (emergencyData.severity === 'CRITICAL') {
        toast.error('⚠️ CRITICAL: Seek immediate medical attention!', { autoClose: false });
      } else if (emergencyData.severity === 'HIGH') {
        toast.warning('⚠️ HIGH: Please see a doctor today.');
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
            {result.emergency.severity !== 'LOW' && (
              <div className={`emergency-banner ${result.emergency.severity === 'CRITICAL' ? 'critical' : ''}`}>
                <div className="emergency-title">
                  🚨 {result.emergency.severity} ALERT
                </div>
                <p style={{ marginBottom: '8px' }}>{result.emergency.recommended_action}</p>
                <strong>Emergency Contact: {result.emergency.emergency_contact}</strong>
                {result.emergency.triggered_keywords?.length > 0 && (
                  <div style={{ marginTop: '8px', fontSize: '0.82rem' }}>
                    Detected: {result.emergency.triggered_keywords.join(', ')}
                  </div>
                )}
              </div>
            )}

            {/* Analysis Results */}
            <div className="card">
              <h2 className="card-title">📊 Analysis Results</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '20px' }}>
                <div>
                  <div className="form-label">Classification</div>
                  <strong style={{ textTransform: 'capitalize', fontSize: '1.1rem' }}>
                    {result.analysis.classification}
                  </strong>
                </div>
                <div>
                  <div className="form-label">Risk Level</div>
                  <RiskBadge level={result.analysis.risk_level} />
                </div>
                <div>
                  <div className="form-label">Confidence</div>
                  <strong>{(result.analysis.confidence_score * 100).toFixed(1)}%</strong>
                </div>
              </div>

              <div className="form-label">AI Medical Response (RAG-Powered)</div>
              <div className="response-box">
                {result.analysis.rag_response}
              </div>

              {result.analysis.sources?.length > 0 && (
                <div style={{ marginTop: '12px' }}>
                  <span className="form-label">Sources: </span>
                  <div className="sources-list">
                    {result.analysis.sources.map((src, i) => (
                      <span key={i} className="source-tag">{src}</span>
                    ))}
                  </div>
                </div>
              )}

              <div style={{ marginTop: '20px', display: 'flex', gap: '12px' }}>
                <button
                  className="btn btn-primary"
                  onClick={() => navigate(`/recommendations?analysis_id=${result.analysis.analysis_id}`)}
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
          </>
        )}
      </main>
    </div>
  );
};

export default SymptomForm;
