import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LearningAnalysis.css';

const LearningAnalysis = () => {
  const navigate = useNavigate();

  const handleBack = () => {
    navigate('/study-assistant');
  };

  return (
    <div className="learning-analysis-container">
      <div className="header">
        <button className="back-button" onClick={handleBack}>
          ← 返回
        </button>
        <h1>学情分析</h1>
      </div>
      
      <div className="content">
        <p>功能开发中...</p>
      </div>
    </div>
  );
};

export default LearningAnalysis;
