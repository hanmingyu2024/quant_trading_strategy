import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Header from './components/Header';
import PasswordReset from './components/PasswordReset';
import { useAuth } from './hooks/useAuth';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';

function App() {
    const { isAuthenticated } = useAuth();

    return (
        <Router>
            <Header />
            <main>
                <Routes>
                    <Route path="/" element={isAuthenticated ? <Dashboard /> : <Login />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/reset-password" element={<PasswordReset />} />
                </Routes>
            </main>
        </Router>
    );
}

export default App;