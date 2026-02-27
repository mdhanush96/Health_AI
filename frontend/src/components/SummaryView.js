import React from 'react';
import { useLocation, useParams, useNavigate } from 'react-router-dom';
import { Sidebar } from './Dashboard';

const SummaryView = () => {
  const location = useLocation();
  const { reportId } = useParams();
  const navigate = useNavigate();
  const report = location.state?.report;

  if (!report) {
    return (
      <div className="layout">
        <Sidebar />
        <main className="main-content">
          <div className="page-header">
            <h1>📋 Report Summary</h1>
          </div>
          <div className="card">
            <p>No report data available. Please upload and analyze a report first.</p>
            <button className="btn btn-primary" style={{ marginTop: '16px' }} onClick={() => navigate('/report')}>
              Upload Report
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-header">
          <h1>📋 Report Summary</h1>
          <p>AI-generated clinical summary of your medical report</p>
        </div>

        <div className="card">
          <h2 className="card-title">🤖 AI-Generated Clinical Summary</h2>
          <div className="response-box" style={{ fontSize: '0.95rem', lineHeight: '1.8' }}>
            {report.summary || 'Summary not available.'}
          </div>
        </div>

        {report.extracted_text && (
          <div className="card">
            <h2 className="card-title">📝 Extracted Text</h2>
            <div
              className="response-box"
              style={{
                maxHeight: '300px',
                overflowY: 'auto',
                fontSize: '0.85rem',
                fontFamily: 'monospace',
                whiteSpace: 'pre-wrap',
              }}
            >
              {report.extracted_text}
            </div>
          </div>
        )}

        <div className="card" style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-primary" onClick={() => navigate('/symptom')}>
            🩺 Analyze Related Symptoms
          </button>
          <button className="btn btn-outline" onClick={() => navigate('/recommendations')}>
            💊 View Recommendations
          </button>
          <button className="btn btn-outline" onClick={() => navigate('/report')}>
            📄 Upload Another Report
          </button>
        </div>

        <div className="card" style={{ background: '#f8faff', boxShadow: 'none' }}>
          <h3 style={{ marginBottom: '8px', fontSize: '0.9rem' }}>ℹ️ About This Summary</h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
            This summary was generated using T5/BART transformer models fine-tuned for medical text summarization.
            The model identifies key clinical findings, measurements, and diagnoses from your report.
            Always have your healthcare provider review your medical reports for accurate interpretation.
          </p>
        </div>
      </main>
    </div>
  );
};

export default SummaryView;
