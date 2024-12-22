import React, { useEffect, useState } from 'react';
import api from '../services/api';

const TradeList = () => {
    const [trades, setTrades] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchTrades();
    }, []);

    const fetchTrades = async () => {
        try {
            const response = await api.get('/trades');
            setTrades(response.data);
        } catch (error) {
            console.error('获取交易记录失败:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div>加载中...</div>;
    }

    return (
        <div className="trade-list">
            <h2>交易记录</h2>
            <table>
                <thead>
                    <tr>
                        <th>时间</th>
                        <th>交易对</th>
                        <th>类型</th>
                        <th>数量</th>
                        <th>价格</th>
                        <th>策略</th>
                        <th>状态</th>
                    </tr>
                </thead>
                <tbody>
                    {trades.map((trade) => (
                        <tr key={trade.id}>
                            <td>{new Date(trade.created_at).toLocaleString()}</td>
                            <td>{trade.symbol}</td>
                            <td className={trade.type === 'BUY' ? 'buy' : 'sell'}>
                                {trade.type === 'BUY' ? '买入' : '卖出'}
                            </td>
                            <td>{trade.amount}</td>
                            <td>{trade.price}</td>
                            <td>{trade.strategy}</td>
                            <td>{trade.status}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default TradeList;
