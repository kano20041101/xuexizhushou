import React from 'react';
import { useNavigate } from 'react-router-dom';
import './StudyAssistant.css';

const StudyAssistant = () => {
  const navigate = useNavigate();

  const handleKnowledgeManagement = () => {
    navigate('/knowledge-management');
  };

  const handleLearningAnalysis = () => {
    navigate('/learning-analysis');
  };

  return (
    <div className="study-assistant-container">
      <h1>学习助手</h1>
      <p>欢迎使用学习助手，请选择功能模块：</p>
      
      <div className="button-container">
        <button 
          className="feature-button knowledge-button"
          onClick={handleKnowledgeManagement}
        >
          知识点管理
        </button>
        
        <button 
          className="feature-button analysis-button"
          onClick={handleLearningAnalysis}
        >
          学情分析
        </button>
      </div>
    </div>
  );
};

export default StudyAssistant;
