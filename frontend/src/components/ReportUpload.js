import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { reportAPI } from '../api';
import { Sidebar } from './Dashboard';

const ReportUpload = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [uploadedReport, setUploadedReport] = useState(null);

  const supportedTypes = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.csv'];

  const handleFile = (selectedFile) => {
    if (!selectedFile) return;
    const ext = '.' + selectedFile.name.split('.').pop().toLowerCase();
    if (!supportedTypes.includes(ext)) {
      toast.error(`Unsupported file type. Supported: ${supportedTypes.join(', ')}`);
      return;
    }
    if (selectedFile.size > 20 * 1024 * 1024) {
      toast.error('File too large. Maximum size is 20MB.');
      return;
    }
    setFile(selectedFile);
    setUploadedReport(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFile(droppedFile);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const response = await reportAPI.upload(file);
      setUploadedReport(response.data);
      toast.success('Report uploaded and text extracted successfully!');
    } catch (err) {
      toast.error(err.response?.data?.file?.[0] || 'Upload failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!uploadedReport) return;
    setLoading(true);
    try {
      const response = await reportAPI.analyze(uploadedReport.id);
      navigate(`/summary/${uploadedReport.id}`, { state: { report: response.data } });
    } catch (err) {
      toast.error('Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getFileIcon = (fileName) => {
    const ext = fileName?.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return '📄';
    if (['png', 'jpg', 'jpeg', 'tiff', 'bmp'].includes(ext)) return '🖼️';
    if (ext === 'csv') return '📊';
    return '📁';
  };

  return (
    <div className="layout">
      <Sidebar />
      <main className="main-content">
        <div className="page-header">
          <h1>📄 Upload Medical Report</h1>
          <p>Upload your medical report for AI-powered text extraction and summarization</p>
        </div>

        <div className="card">
          <div
            className={`upload-zone ${dragging ? 'dragging' : ''}`}
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
          >
            <div className="upload-icon">📁</div>
            <p style={{ fontWeight: '600', marginBottom: '8px' }}>
              {file ? file.name : 'Click to upload or drag and drop'}
            </p>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Supported formats: PDF, PNG, JPG, TIFF, BMP, CSV (max 20MB)
            </p>
            <input
              ref={fileInputRef}
              type="file"
              style={{ display: 'none' }}
              accept=".pdf,.png,.jpg,.jpeg,.tiff,.bmp,.csv"
              onChange={(e) => handleFile(e.target.files[0])}
            />
          </div>

          {file && (
            <div style={{ marginTop: '20px', padding: '16px', background: '#f8faff', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontSize: '2rem' }}>{getFileIcon(file.name)}</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: '600' }}>{file.name}</div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                  {(file.size / 1024).toFixed(1)} KB
                </div>
              </div>
              <button
                className="btn btn-primary"
                onClick={handleUpload}
                disabled={loading}
              >
                {loading ? <><span className="spinner" /> Uploading...</> : '⬆️ Upload & Extract'}
              </button>
            </div>
          )}
        </div>

        {uploadedReport && (
          <div className="card">
            <h2 className="card-title">✅ Text Extracted Successfully</h2>
            <div style={{ marginBottom: '16px' }}>
              <span className="form-label">Report Type: </span>
              <span style={{ fontWeight: '600' }}>{uploadedReport.report_type}</span>
              {'  '}
              <span className="form-label">Status: </span>
              <span className={`badge ${uploadedReport.status === 'COMPLETED' ? 'badge-low' : 'badge-medium'}`}>
                {uploadedReport.status}
              </span>
            </div>

            {uploadedReport.extracted_text && (
              <div style={{ marginBottom: '20px' }}>
                <div className="form-label">Extracted Text Preview</div>
                <div className="response-box" style={{ maxHeight: '200px', overflowY: 'auto', fontSize: '0.85rem', fontFamily: 'monospace' }}>
                  {uploadedReport.extracted_text.substring(0, 800)}
                  {uploadedReport.extracted_text.length > 800 && '...'}
                </div>
              </div>
            )}

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                className="btn btn-primary"
                onClick={handleAnalyze}
                disabled={loading || !uploadedReport.extracted_text}
              >
                {loading ? <><span className="spinner" /> Summarizing...</> : '🤖 Summarize with AI'}
              </button>
              <button
                className="btn btn-outline"
                onClick={() => { setFile(null); setUploadedReport(null); }}
              >
                Upload Another
              </button>
            </div>
          </div>
        )}

        {/* OCR Technology info */}
        <div className="card" style={{ background: '#f0f4f8', boxShadow: 'none' }}>
          <h3 style={{ marginBottom: '12px', fontSize: '0.95rem' }}>🔬 How Report Analysis Works</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            <div>
              <strong>📄 PDF Documents</strong>
              <p>Extracted using PyMuPDF + Tesseract OCR for scanned documents</p>
            </div>
            <div>
              <strong>🖼️ Medical Images</strong>
              <p>Processed with Tesseract OCR (LSTM engine) for text recognition</p>
            </div>
            <div>
              <strong>📊 CSV Files</strong>
              <p>Parsed with pandas for structured lab result data</p>
            </div>
            <div>
              <strong>🤖 AI Summarization</strong>
              <p>Summarized using T5/BART transformer models</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ReportUpload;
