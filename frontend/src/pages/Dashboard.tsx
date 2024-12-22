import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import TradeForm from '../components/TradeForm';
import TradeList from '../components/TradeList';
import api from '../services/api';

const Dashboard = () => {
    const { user } = useSelector((state) => state.auth);
    const [stats, setStats] = useState({
        totalTrades: 0,
        profitLoss: 0,
        winRate: 0
    });

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const response = await api.get('/trades/stats');
            setStats(response.data);
        } catch (error) {
            console.error('获取统计数据失败:', error);
        }
    };

    const handleTradeSubmit = () => {
        fetchStats(); // 刷新统计数据
    };

    return (
        <div className="dashboard">
            <div className="dashboard-header">
                <h1>交易仪表盘</h1>
                <div className="stats-container">
                    <div className="stat-box">
                        <h3>总交易次数</h3>
                        <p>{stats.totalTrades}</p>
                    </div>
                    <div className="stat-box">
                        <h3>盈亏</h3>
                        <p className={stats.profitLoss >= 0 ? 'profit' : 'loss'}>
                            {stats.profitLoss > 0 ? '+' : ''}{stats.profitLoss}
                        </p>
                    </div>
                    <div className="stat-box">
                        <h3>胜率</h3>
                        <p>{stats.winRate}%</p>
                    </div>
                </div>
            </div>

            <div className="dashboard-content">
                <div className="trade-section">
                    <h2>创建交易</h2>
                    <TradeForm onTradeSubmit={handleTradeSubmit} />
                </div>

                <div className="history-section">
                    <TradeList />
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
