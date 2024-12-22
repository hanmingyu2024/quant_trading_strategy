import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { logoutUser } from '../store/actions/authActions';

const Header = () => {
    const navigate = useNavigate();
    const dispatch = useDispatch();
    const { user, isAuthenticated } = useSelector((state) => state.auth);

    const handleLogout = () => {
        dispatch(logoutUser());
        navigate('/login');
    };

    return (
        <header className="header">
            <div className="logo">
                <img src="/assets/logo.png" alt="量化交易" />
            </div>
            <nav>
                {isAuthenticated ? (
                    <>
                        <span>欢迎, {user?.username}</span>
                        <button onClick={() => navigate('/dashboard')}>仪表盘</button>
                        <button onClick={handleLogout}>退出</button>
                    </>
                ) : (
                    <>
                        <button onClick={() => navigate('/login')}>登录</button>
                        <button onClick={() => navigate('/register')}>注册</button>
                    </>
                )}
            </nav>
        </header>
    );
};

export default Header; 