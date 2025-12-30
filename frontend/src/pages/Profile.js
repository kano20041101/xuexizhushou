import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Profile.css';

const API_BASE_URL = 'http://localhost:8000';

const Profile = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    username: '',
    grade: '',
    postgraduate_session: '',
    school: '',
    major: '',
    target_school: '',
    target_major: '',
    target_score: ''
  });
  const [avatarPreview, setAvatarPreview] = useState('');
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  // 加载用户信息
  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const userId = localStorage.getItem('userId');
        if (!userId) {
          navigate('/login');
          return;
        }

        const response = await axios.get(`http://localhost:8000/profile/${userId}`);
        const userData = response.data;
        setUser(userData);
        setFormData({
          username: userData.username,
          grade: userData.grade || '',
          postgraduate_session: userData.postgraduate_session || '',
          school: userData.school || '',
          major: userData.major || '',
          target_school: userData.target_school || '',
          target_major: userData.target_major || '',
          target_score: userData.target_score || ''
        });
        setAvatarPreview(userData.avatar ? `${API_BASE_URL}${userData.avatar}` : '/default-avatar.png');
        setLoading(false);
      } catch (err) {
        setError('获取用户信息失败，请重试');
        setLoading(false);
        console.error('Profile error:', err);
      }
    };

    fetchUserProfile();
  }, [navigate]);

  // 处理表单输入变化
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // 处理头像上传预览
  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // 打开文件选择对话框
  const handleAvatarClick = () => {
    fileInputRef.current.click();
  };

  // 提交表单数据
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const userId = localStorage.getItem('userId');
      if (!userId) {
        navigate('/login');
        return;
      }

      // 创建FormData对象处理文件上传
      const submitData = new FormData();
      Object.entries(formData).forEach(([key, value]) => {
        submitData.append(key, value);
      });

      // 如果有新头像文件，添加到FormData
      if (fileInputRef.current.files.length > 0) {
        submitData.append('avatar', fileInputRef.current.files[0]);
      }

      await axios.put(`http://localhost:8000/profile/${userId}`, submitData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // 显示成功消息并刷新页面数据
      alert('个人信息更新成功！');
      window.location.reload();
    } catch (err) {
      setError('更新信息失败，请重试');
      console.error('Update profile error:', err);
    }
  };

  // 退出登录
  const handleLogout = () => {
    localStorage.removeItem('userId');
    navigate('/login');
  };

  const handleStudyAssistant = () => {
    navigate('/study-assistant');
  };

  if (loading) return <div className="loading">加载中...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!user) return null;

  return (
    <div className="profile-container">
      <div className="profile-card">
        <h2>个人信息</h2>
        <form onSubmit={handleSubmit} className="profile-form">
          {/* 头像上传区域 */}
          <div className="avatar-section">
            <div className="avatar-container" onClick={handleAvatarClick}>
              <img
                src={avatarPreview}
                alt="头像"
                className="avatar-img"
              />
              <div className="avatar-overlay">更换头像</div>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleAvatarChange}
                accept="image/*"
                className="avatar-input"
              />
            </div>
          </div>

          {/* 表单字段区域 */}
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="username">用户名</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                disabled
                className="disabled-input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="grade">年级</label>
              <select name="grade" value={formData.grade} onChange={handleInputChange} className="form-select">
                <option value="">请选择年级</option>
                <option value="大一">大一</option>
                <option value="大二">大二</option>
                <option value="大三">大三</option>
                <option value="大四">大四</option>
                <option value="已毕业">已毕业</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="postgraduate_session">考研届数</label>
              <input
                type="text"
                id="postgraduate_session"
                name="postgraduate_session"
                value={formData.postgraduate_session}
                onChange={handleInputChange}
                placeholder="如：2026届"
              />
            </div>

            <div className="form-group">
              <label htmlFor="school">学校</label>
              <input
                type="text"
                id="school"
                name="school"
                value={formData.school}
                onChange={handleInputChange}
                placeholder="请输入就读学校"
              />
            </div>

            <div className="form-group">
              <label htmlFor="major">专业</label>
              <input
                type="text"
                id="major"
                name="major"
                value={formData.major}
                onChange={handleInputChange}
                placeholder="请输入就读专业"
              />
            </div>

            <div className="form-group">
              <label htmlFor="target_school">预期学校</label>
              <input
                type="text"
                id="target_school"
                name="target_school"
                value={formData.target_school}
                onChange={handleInputChange}
                placeholder="请输入目标学校"
              />
            </div>

            <div className="form-group">
              <label htmlFor="target_major">预期专业</label>
              <input
                type="text"
                id="target_major"
                name="target_major"
                value={formData.target_major}
                onChange={handleInputChange}
                placeholder="请输入目标专业"
              />
            </div>

            <div className="form-group">
              <label htmlFor="target_score">预期分数</label>
              <input
                type="number"
                id="target_score"
                name="target_score"
                value={formData.target_score}
                onChange={handleInputChange}
                step="0.5"
                min="0"
                max="500"
                placeholder="请输入预期分数"
              />
            </div>
          </div>

          {/* 按钮区域 */}
          <div className="button-group">
            <button type="button" onClick={handleStudyAssistant} className="study-assistant-button">进入应用</button>
            <button type="submit" className="save-button">保存信息</button>
            <button type="button" onClick={handleLogout} className="logout-button">退出登录</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Profile;