import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import StudyAssistant from './pages/StudyAssistant';
import KnowledgeManagement from './pages/KnowledgeManagement';
import LearningAnalysis from './pages/LearningAnalysis';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/profile" element={localStorage.getItem('userId') ? <Profile /> : <Navigate to="/login" replace />} />
          <Route path="/study-assistant" element={localStorage.getItem('userId') ? <StudyAssistant /> : <Navigate to="/login" replace />} />
          <Route path="/knowledge-management" element={localStorage.getItem('userId') ? <KnowledgeManagement /> : <Navigate to="/login" replace />} />
          <Route path="/learning-analysis" element={localStorage.getItem('userId') ? <LearningAnalysis /> : <Navigate to="/login" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;