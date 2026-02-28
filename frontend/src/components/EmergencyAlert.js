import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { emergencyAPI } from '../api';
import { Sidebar } from './Dashboard';

const SeverityIcon = ({ severity }) => {
  const icons = { LOW: '🟢', MEDIUM: '🟡', HIGH: '🟠', CRITICAL: '🔴' };
  return <span>{icons[severity] || '⚪'}</span>;
};

const EmergencyAlert = () => {
  const [symptomText, setSymptomText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await emergencyAPI.alerts();
      setAlerts(response.data.results || response.data);
    } catch (err) {
      // Silent fail - user may not have alerts
    }
  };

  const handleCheck = async (e) => {
    e.preventDefault();
    if (!symptomText.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const response = await emergencyAPI.check(symptomText);
      setResult(response.data);

      if (response.data.severity === 'CRITICAL') {
        toast.error('🚨 CRITICAL EMERGENCY DETECTED!', { autoClose: false });
      } else if (response.data.severity === 'HIGH') {
        toast.warning('⚠️ High severity - seek medical attention today.');
      } else if (response.data.severity === 'MEDIUM') {
        toast.info('ℹ️ Moderate severity - schedule a doctor visit.');
      } else {
        toast.success('✅ Low severity - monitor your symptoms.');
      }

      fetchAlerts();
    } catch (err) {
      toast.error('Emergency check failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async (alertId) => {
    try {
      await emergencyAPI.acknowledge(alertId);
      setAlerts((prev) => prev.map((a) => a.id === alertId ? { ...a, is_acknowledged: true } : a));
      toast.success('Alert acknowledged.');
    } catch (err) {
      toast.error('Failed to acknowledge alert.');
    }
  };

  const getSeverityColor = (severity) => {
    const colors = { LOW: '#34a853', MEDIUM: '#fbbc04', HIGH: '#ea4335', CRITICAL: '#b71c1c' };
    return colors[severity] || '#666';
  };

  return (
    <div className="layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-header">
          <h1>🚨 Emergency Severity Check</h1>
          <p>Detect potential medical emergencies and get immediate guidance</p>
        </div>

        {/* Emergency contacts banner */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '12px', marginBottom: '24px' }}>
          {[
            { label: 'Emergency', number: '911', color: '#b71c1c' },
            { label: 'Mental Health Crisis', number: '988', color: '#7b1fa2' },
            { label: 'Poison Control', number: '1-800-222-1222', color: '#e65100' },
            { label: 'Nurse Hotline', number: '1-800-CDC-INFO', color: '#1565c0' },
          ].map((contact) => (
            <div
              key={contact.label}
              style={{
                background: 'white',
                borderRadius: '8px',
                padding: '12px',
                textAlign: 'center',
                boxShadow: 'var(--shadow)',
                borderTop: `3px solid ${contact.color}`,
              }}
            >
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '4px', textTransform: 'uppercase' }}>
                {contact.label}
              </div>
              <div style={{ fontWeight: '700', color: contact.color, fontSize: '1rem' }}>
                {contact.number}
              </div>
            </div>
          ))}
        </div>

        <div className="card">
          <h2 className="card-title">🔍 Check Symptom Severity</h2>
          <form onSubmit={handleCheck}>
            <div className="form-group">
              <label className="form-label">Describe Your Symptoms</label>
              <textarea
                className="form-textarea"
                value={symptomText}
                onChange={(e) => setSymptomText(e.target.value)}
                placeholder="Describe what you're experiencing... Be as specific as possible about severity, location, and duration."
                required
                minLength={5}
              />
            </div>
            <button type="submit" className="btn btn-danger" disabled={loading}>
              {loading ? <><span className="spinner" /> Checking...</> : '🚨 Check Emergency Level'}
            </button>
          </form>
        </div>

        {result && (
          <div
            className="card"
            style={{
              borderLeft: `6px solid ${getSeverityColor(result.severity)}`,
              background: result.severity === 'CRITICAL' ? '#ffebee' : result.severity === 'HIGH' ? '#fff3e0' : '#f1f8e9',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
              <SeverityIcon severity={result.severity} />
              <h2 style={{ fontSize: '1.3rem', fontWeight: '700', color: getSeverityColor(result.severity) }}>
                {result.severity} SEVERITY
              </h2>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <div className="form-label">Recommended Action</div>
              <p style={{ fontSize: '1rem', lineHeight: '1.6', fontWeight: '500' }}>
                {result.recommended_action}
              </p>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <div className="form-label">Emergency Contact</div>
              <strong style={{ fontSize: '1.2rem', color: getSeverityColor(result.severity) }}>
                📞 {result.emergency_contact}
              </strong>
            </div>

            {result.triggered_keywords?.length > 0 && (
              <div>
                <div className="form-label">Detected Warning Signs</div>
                <div className="sources-list">
                  {result.triggered_keywords.map((kw, i) => (
                    <span key={i} className="source-tag" style={{ background: '#ffebee', color: '#c62828' }}>
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Previous Alerts */}
        {alerts.length > 0 && (
          <div className="card">
            <h2 className="card-title">📋 Previous Alerts</h2>
            {alerts.map((alert) => (
              <div
                key={alert.id}
                style={{
                  padding: '12px 0',
                  borderBottom: '1px solid var(--border)',
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'space-between',
                  gap: '12px',
                  opacity: alert.is_acknowledged ? 0.6 : 1,
                }}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <SeverityIcon severity={alert.severity} />
                    <strong style={{ color: getSeverityColor(alert.severity) }}>{alert.severity}</strong>
                    <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                      {new Date(alert.created_at).toLocaleDateString()}
                    </span>
                    {alert.is_acknowledged && <span className="badge badge-low" style={{ fontSize: '0.7rem' }}>Acknowledged</span>}
                  </div>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    {alert.symptom_text?.substring(0, 100)}...
                  </p>
                </div>
                {!alert.is_acknowledged && (
                  <button
                    className="btn btn-outline"
                    style={{ fontSize: '0.78rem', padding: '6px 12px', whiteSpace: 'nowrap' }}
                    onClick={() => handleAcknowledge(alert.id)}
                  >
                    Acknowledge
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default EmergencyAlert;
