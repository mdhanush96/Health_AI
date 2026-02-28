import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { recommendationAPI } from '../api';
import { Sidebar } from './Dashboard';

const Section = ({ title, icon, items }) => {
  if (!items || items.length === 0) return null;
  return (
    <div className="rec-section">
      <h3>{icon} {title}</h3>
      <ul className="rec-list">
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </div>
  );
};

const Recommendations = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const analysisId = searchParams.get('analysis_id');
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState(null);
  const [activeTab, setActiveTab] = useState('diet');

  useEffect(() => {
    fetchRecommendations();
  }, [analysisId]);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const response = await recommendationAPI.get(analysisId);
      if (response.data.diet) {
        setRecommendations(response.data);
      }
    } catch (err) {
      toast.error('Failed to load recommendations.');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'diet', label: '🥗 Diet', data: recommendations?.diet },
    { id: 'exercise', label: '🏃 Exercise', data: recommendations?.exercise },
    { id: 'lifestyle', label: '🌟 Lifestyle', data: recommendations?.lifestyle },
    { id: 'medicines', label: '💊 Medications', data: recommendations?.medicines },
  ];

  return (
    <div className="layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-header">
          <h1>💊 Health Recommendations</h1>
          <p>Personalized diet, exercise, lifestyle, and medication guidance</p>
        </div>

        {loading && (
          <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
            <span className="spinner" style={{ borderColor: 'var(--primary)', borderTopColor: 'transparent', width: '40px', height: '40px' }} />
            <p style={{ marginTop: '16px' }}>Loading your personalized recommendations...</p>
          </div>
        )}

        {!loading && !recommendations && (
          <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>💊</div>
            <h3>No Recommendations Yet</h3>
            <p style={{ color: 'var(--text-secondary)', margin: '12px 0 24px' }}>
              Analyze your symptoms first to get personalized health recommendations.
            </p>
            <button className="btn btn-primary" onClick={() => navigate('/symptom')}>
              🩺 Analyze Symptoms
            </button>
          </div>
        )}

        {!loading && recommendations && (
          <>
            {/* Urgent notes */}
            {recommendations.notes && (
              <div className={`emergency-banner ${recommendations.notes.includes('URGENT') ? 'critical' : ''}`}>
                <div className="emergency-title">
                  {recommendations.notes.includes('URGENT') ? '🚨' : '⚠️'} Important Notice
                </div>
                <p>{recommendations.notes}</p>
              </div>
            )}

            {/* Specialist recommendation */}
            {recommendations.specialist && (
              <div className="card" style={{ borderLeft: '4px solid var(--primary)', padding: '16px 24px' }}>
                <span className="form-label">Recommended Specialist</span>
                <div style={{ fontSize: '1.2rem', fontWeight: '700', color: 'var(--primary)', marginTop: '4px' }}>
                  👨‍⚕️ {recommendations.specialist}
                </div>
              </div>
            )}

            <div className="card">
              <div className="tabs">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    className={`tab ${activeTab === tab.id ? 'active' : ''}`}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {tabs.map((tab) =>
                tab.id === activeTab && tab.data ? (
                  <ul key={tab.id} className="rec-list">
                    {tab.data.map((item, i) => (
                      <li key={i}>{item}</li>
                    ))}
                  </ul>
                ) : null
              )}
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button className="btn btn-outline" onClick={() => navigate('/symptom')}>
                🩺 New Symptom Analysis
              </button>
              <button className="btn btn-outline" onClick={() => navigate('/report')}>
                📄 Upload Report
              </button>
            </div>

            <div className="card" style={{ background: '#fff3e0', boxShadow: 'none', marginTop: '16px' }}>
              <p style={{ fontSize: '0.82rem', color: '#7b3f00' }}>
                <strong>⚕️ Medical Disclaimer:</strong> These recommendations are generated by AI for educational purposes only.
                Always consult with a qualified healthcare professional before starting any new diet, exercise regimen, or medication.
                Never stop or change prescribed medications without medical advice.
              </p>
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default Recommendations;
