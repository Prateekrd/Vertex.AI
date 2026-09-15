import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import UploadPage from './pages/UploadPage';
import ProcessingPage from './pages/ProcessingPage';
import ReviewPage from './pages/ReviewPage';
import ResultsPage from './pages/ResultsPage';
import SearchPage from './pages/SearchPage';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/upload" replace />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/process" element={<ProcessingPage />} />
        <Route path="/review" element={<ReviewPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="*" element={<Navigate to="/upload" replace />} />
      </Routes>
    </Layout>
  );
}
