import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const navItems = [
    { path: '/', icon: '🏠', label: 'Dashboard' },
    { path: '/symptom', icon: '🩺', label: 'Symptom Analysis' },
    { path: '/report', icon: '📄', label: 'Upload Report' },
    { path: '/recommendations', icon: '💊', label: 'Recommendations' },
    { path: '/emergency', icon: '🚨', label: 'Emergency Check' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h1>🏥 MyHealth AI</h1>
        <p>Health Companion</p>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <button
            key={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            onClick={() => navigate(item.path)}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>
      <div style={{ padding: '16px 24px', borderTop: '1px solid var(--border)' }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
          {user?.first_name ? `${user.first_name} ${user.last_name}` : user?.email}
        </div>
        <button className="btn btn-outline" style={{ width: '100%', fontSize: '0.85rem' }} onClick={logout}>
          Sign Out
        </button>
      </div>
    </aside>
  );
};

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    analyses: 0,
    reports: 0,
    recommendations: 0,
    alerts: 0,
  });

  const quickActions = [
    {
      title: 'Describe Symptoms',
      description: 'Get AI-powered symptom analysis using ClinicalBERT',
      icon: '🩺',
      action: () => navigate('/symptom'),
      color: '#1a73e8',
    },
    {
      title: 'Upload Medical Report',
      description: 'Extract and summarize PDF, image, or CSV reports',
      icon: '📄',
      action: () => navigate('/report'),
      color: '#34a853',
    },
    {
      title: 'Health Recommendations',
      description: 'Get personalized diet, exercise, and medication advice',
      icon: '💊',
      action: () => navigate('/recommendations'),
      color: '#fbbc04',
    },
    {
      title: 'Emergency Check',
      description: 'Assess symptom severity and get emergency guidance',
      icon: '🚨',
      action: () => navigate('/emergency'),
      color: '#ea4335',
    },
  ];

  return (
    <div className="layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-header">
          <h1>Welcome back, {user?.first_name || user?.email?.split('@')[0]}! 👋</h1>
          <p>Your intelligent health companion is ready to assist you.</p>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">🛡️</div>
            <div className="stat-label">AI-Powered Analysis</div>
          </div>
          <div className="stat-card" style={{ borderColor: '#34a853' }}>
            <div className="stat-value" style={{ color: '#34a853' }}>📊</div>
            <div className="stat-label">Personalized Insights</div>
          </div>
          <div className="stat-card" style={{ borderColor: '#fbbc04' }}>
            <div className="stat-value" style={{ color: '#fbbc04' }}>⚡</div>
            <div className="stat-label">Real-Time Detection</div>
          </div>
          <div className="stat-card" style={{ borderColor: '#ea4335' }}>
            <div className="stat-value" style={{ color: '#ea4335' }}>🔒</div>
            <div className="stat-label">HIPAA-Compliant</div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
          {quickActions.map((action) => (
            <div
              key={action.title}
              className="card"
              style={{ cursor: 'pointer', borderTop: `4px solid ${action.color}`, transition: 'transform 0.2s' }}
              onClick={action.action}
              onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
              onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
            >
              <div style={{ fontSize: '2rem', marginBottom: '12px' }}>{action.icon}</div>
              <h3 style={{ fontSize: '1rem', fontWeight: '700', marginBottom: '8px' }}>{action.title}</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{action.description}</p>
              <button
                className="btn btn-primary"
                style={{ marginTop: '16px', background: action.color, fontSize: '0.85rem' }}
              >
                Get Started →
              </button>
            </div>
          ))}
        </div>

        <div className="card" style={{ marginTop: '8px', background: 'linear-gradient(135deg, #1a73e8, #0d47a1)', color: 'white' }}>
          <h3 style={{ color: 'white', marginBottom: '8px' }}>ℹ️ Important Disclaimer</h3>
          <p style={{ fontSize: '0.85rem', opacity: 0.9 }}>
            MyHealth AI is an educational prototype and should not replace professional medical advice.
            Always consult a qualified healthcare provider for diagnosis and treatment.
            In an emergency, call 911 immediately.
          </p>
        </div>
      </main>
    </div>
  );
};

export { Sidebar };
export default Dashboard;
