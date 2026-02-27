import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import SymptomForm from './components/SymptomForm';
import ReportUpload from './components/ReportUpload';
import SummaryView from './components/SummaryView';
import Recommendations from './components/Recommendations';
import EmergencyAlert from './components/EmergencyAlert';
import './App.css';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="loading-screen">Loading...</div>;
  return user ? children : <Navigate to="/login" replace />;
};

function App() {
  const { user } = useAuth();

  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/login" element={user ? <Navigate to="/" replace /> : <Login />} />
          <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
          <Route path="/symptom" element={<PrivateRoute><SymptomForm /></PrivateRoute>} />
          <Route path="/report" element={<PrivateRoute><ReportUpload /></PrivateRoute>} />
          <Route path="/summary/:reportId" element={<PrivateRoute><SummaryView /></PrivateRoute>} />
          <Route path="/recommendations" element={<PrivateRoute><Recommendations /></PrivateRoute>} />
          <Route path="/emergency" element={<PrivateRoute><EmergencyAlert /></PrivateRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
