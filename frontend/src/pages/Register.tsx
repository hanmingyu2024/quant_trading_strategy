import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/auth';

const Register = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (formData.password !== formData.confirmPassword) {
            setError('两次输入的密码不一致');
            return;
        }

        try {
            setLoading(true);
            setError(null);
            await authService.register({
                username: formData.username,
                email: formData.email,
                password: formData.password
            });
            navigate('/login', { state: { message: '注册成功，请登录' } });
        } catch (error) {
            setError(error.response?.data?.message || '注册失败');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="register-page">
            <div className="register-form">
                <h2>注册</h2>
                {error && <div className="error-message">{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>用户名</label>
                        <input
                            type="text"
                            value={formData.username}
                            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>邮箱</label>
                        <input
                            type="email"
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>密码</label>
                        <input
                            type="password"
                            value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>确认密码</label>
                        <input
                            type="password"
                            value={formData.confirmPassword}
                            onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                            required
                        />
                    </div>
                    <button type="submit" disabled={loading}>
                        {loading ? '注册中...' : '注册'}
                    </button>
                </form>
                <p>
                    已有账号？ <Link to="/login">立即登录</Link>
                </p>
            </div>
        </div>
    );
};

export default Register;
