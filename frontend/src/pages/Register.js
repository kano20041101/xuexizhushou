import React, { useState } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import './Register.css';

const Register = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('两次密码输入不一致');
      return;
    }
    try {
      const response = await axios.post('http://localhost:8000/register', {
        username,
        password
      });
      if (response.data.status === 'success') {
        setSuccess('注册成功，请登录');
        setTimeout(() => navigate('/login'), 1500);
      } else {
        setError(response.data.message || '注册失败，请重试');
      }
    } catch (err) {
      setError('注册失败，请检查网络或服务器');
      console.error('Register error:', err);
    }
  };

  return (
    <div className="register-container">
      <div className="register-card">
        <h2>用户注册</h2>
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">用户名</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">密码</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="confirmPassword">确认密码</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="register-button">注册</button>
        </form>
        <div className="login-link">
          已有账号? <Link to="/login">立即登录</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;