import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './KnowledgeManagement.css';
import {
  getKnowledgePoints,
  createKnowledgePoint,
  updateKnowledgePoint,
  deleteKnowledgePoint
} from '../services/knowledgePointService';

const KnowledgeManagement = () => {
  const navigate = useNavigate();
  const userId = parseInt(localStorage.getItem('userId'));
  
  const [knowledgePoints, setKnowledgePoints] = useState([]);
  const [filteredPoints, setFilteredPoints] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState('全部');
  const [showModal, setShowModal] = useState(false);
  const [editingPoint, setEditingPoint] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  
  const [formData, setFormData] = useState({
    subject: '',
    point_name: '',
    category: '',
    importance: '中',
    difficulty: '中',
    exam_points: '',
    content: ''
  });

  const subjects = ['数据结构', '计算机组成原理', '操作系统', '计算机网络', '全部'];
  const importanceOptions = ['低', '中', '高', '必考'];
  const difficultyOptions = ['易', '较易', '中', '较难', '难'];

  useEffect(() => {
    loadKnowledgePoints();
  }, [userId]);

  useEffect(() => {
    filterKnowledgePoints();
  }, [knowledgePoints, selectedSubject, searchTerm]);

  const loadKnowledgePoints = async () => {
    try {
      const data = await getKnowledgePoints(userId);
      setKnowledgePoints(data);
    } catch (error) {
      console.error('加载知识点失败:', error);
      alert('加载知识点失败，请稍后重试');
    }
  };

  const filterKnowledgePoints = () => {
    let filtered = [...knowledgePoints];
    
    if (selectedSubject !== '全部') {
      filtered = filtered.filter(kp => kp.subject === selectedSubject);
    }
    
    if (searchTerm) {
      filtered = filtered.filter(kp => 
        kp.point_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        kp.category.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    setFilteredPoints(filtered);
  };

  const handleBack = () => {
    navigate('/study-assistant');
  };

  const handleAdd = () => {
    setEditingPoint(null);
    setFormData({
      subject: '',
      point_name: '',
      category: '',
      importance: '中',
      difficulty: '中',
      exam_points: '',
      content: ''
    });
    setShowModal(true);
  };

  const handleEdit = (point) => {
    setEditingPoint(point);
    setFormData({
      subject: point.subject,
      point_name: point.point_name,
      category: point.category,
      importance: point.importance,
      difficulty: point.difficulty,
      exam_points: point.exam_points || '',
      content: point.content || ''
    });
    setShowModal(true);
  };

  const handleDelete = async (kpId) => {
    if (!window.confirm('确定要删除这个知识点吗？')) {
      return;
    }
    
    try {
      await deleteKnowledgePoint(kpId);
      alert('删除成功');
      loadKnowledgePoints();
    } catch (error) {
      console.error('删除失败:', error);
      alert('删除失败，请稍后重试');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingPoint) {
        await updateKnowledgePoint(editingPoint.kp_id, formData);
        alert('更新成功');
      } else {
        await createKnowledgePoint({
          ...formData,
          id: userId
        });
        alert('创建成功');
      }
      setShowModal(false);
      loadKnowledgePoints();
    } catch (error) {
      console.error('操作失败:', error);
      alert(error.response?.data?.detail || '操作失败，请稍后重试');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const getImportanceColor = (importance) => {
    const colors = {
      '低': '#4caf50',
      '中': '#ff9800',
      '高': '#f44336',
      '必考': '#9c27b0'
    };
    return colors[importance] || '#666';
  };

  const getDifficultyColor = (difficulty) => {
    const colors = {
      '易': '#4caf50',
      '较易': '#8bc34a',
      '中': '#ff9800',
      '较难': '#ff5722',
      '难': '#f44336'
    };
    return colors[difficulty] || '#666';
  };

  return (
    <div className="knowledge-management-container">
      <div className="header">
        <button className="back-button" onClick={handleBack}>
          ← 返回
        </button>
        <h1>知识点管理</h1>
      </div>
      
      <div className="toolbar">
        <div className="toolbar-left">
          <select
            className="subject-select"
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
          >
            {subjects.map(subject => (
              <option key={subject} value={subject}>{subject}</option>
            ))}
          </select>
          <input
            type="text"
            className="search-input"
            placeholder="搜索知识点名称或分类..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <button className="add-button" onClick={handleAdd}>
          + 添加知识点
        </button>
      </div>
      
      <div className="content">
        {filteredPoints.length === 0 ? (
          <div className="empty-state">
            <p>暂无知识点数据</p>
            <button className="add-button" onClick={handleAdd}>
              添加第一个知识点
            </button>
          </div>
        ) : (
          <div className="knowledge-grid">
            {filteredPoints.map(point => (
              <div key={point.kp_id} className="knowledge-card">
                <div className="card-header">
                  <span className="subject-tag">{point.subject}</span>
                  <div className="card-actions">
                    <button 
                      className="action-button edit"
                      onClick={() => handleEdit(point)}
                    >
                      编辑
                    </button>
                    <button 
                      className="action-button delete"
                      onClick={() => handleDelete(point.kp_id)}
                    >
                      删除
                    </button>
                  </div>
                </div>
                <h3 className="point-name">{point.point_name}</h3>
                <p className="category">分类: {point.category}</p>
                <div className="card-tags">
                  <span 
                    className="tag importance"
                    style={{ backgroundColor: getImportanceColor(point.importance) }}
                  >
                    {point.importance}
                  </span>
                  <span 
                    className="tag difficulty"
                    style={{ backgroundColor: getDifficultyColor(point.difficulty) }}
                  >
                    {point.difficulty}
                  </span>
                </div>
                {point.exam_points && (
                  <p className="exam-points">考点: {point.exam_points}</p>
                )}
                {point.content && (
                  <p className="content-preview">{point.content.substring(0, 100)}...</p>
                )}
                <p className="time-info">
                  创建于: {new Date(point.create_time).toLocaleString('zh-CN')}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingPoint ? '编辑知识点' : '添加知识点'}</h2>
              <button className="close-button" onClick={() => setShowModal(false)}>
                ×
              </button>
            </div>
            <form onSubmit={handleSubmit} className="modal-form">
              <div className="form-group">
                <label>科目 *</label>
                <select
                  name="subject"
                  value={formData.subject}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">请选择科目</option>
                  {subjects.filter(s => s !== '全部').map(subject => (
                    <option key={subject} value={subject}>{subject}</option>
                  ))}
                </select>
              </div>
              
              <div className="form-group">
                <label>知识点名称 *</label>
                <input
                  type="text"
                  name="point_name"
                  value={formData.point_name}
                  onChange={handleInputChange}
                  required
                  placeholder="如：二叉树遍历"
                />
              </div>
              
              <div className="form-group">
                <label>分类 *</label>
                <input
                  type="text"
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  required
                  placeholder="如：树与二叉树"
                />
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>重要度</label>
                  <select
                    name="importance"
                    value={formData.importance}
                    onChange={handleInputChange}
                  >
                    {importanceOptions.map(opt => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                </div>
                
                <div className="form-group">
                  <label>难度</label>
                  <select
                    name="difficulty"
                    value={formData.difficulty}
                    onChange={handleInputChange}
                  >
                    {difficultyOptions.map(opt => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="form-group">
                <label>考点</label>
                <input
                  type="text"
                  name="exam_points"
                  value={formData.exam_points}
                  onChange={handleInputChange}
                  placeholder="如：选择题、计算题、论述题"
                />
              </div>
              
              <div className="form-group">
                <label>详细内容</label>
                <textarea
                  name="content"
                  value={formData.content}
                  onChange={handleInputChange}
                  rows="6"
                  placeholder="输入知识点的详细内容..."
                />
              </div>
              
              <div className="form-actions">
                <button type="button" className="cancel-button" onClick={() => setShowModal(false)}>
                  取消
                </button>
                <button type="submit" className="submit-button">
                  {editingPoint ? '更新' : '创建'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeManagement;

