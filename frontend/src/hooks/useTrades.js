import { useState, useEffect } from 'react';
import { tradesAPI } from '../services/api';

export const useTrades = () => {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTrades = async () => {
    try {
      setLoading(true);
      const response = await tradesAPI.getTrades();
      setTrades(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || '获取交易记录失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrades();
  }, []);

  const createTrade = async (tradeData) => {
    try {
      const response = await tradesAPI.createTrade(tradeData);
      setTrades([...trades, response.data]);
      return response.data;
    } catch (err) {
      throw err;
    }
  };

  const closeTrade = async (tradeId) => {
    try {
      await tradesAPI.closeTrade(tradeId);
      setTrades(trades.map(trade => 
        trade.id === tradeId 
          ? { ...trade, status: 'CLOSED' } 
          : trade
      ));
    } catch (err) {
      throw err;
    }
  };

  return {
    trades,
    loading,
    error,
    fetchTrades,
    createTrade,
    closeTrade
  };
};