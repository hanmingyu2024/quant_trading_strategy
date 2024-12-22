# config/config.py

import os
from pathlib import Path
from dotenv import load_dotenv
import MetaTrader5 as mt5

# 加载.env文件
load_dotenv()

# 项目路径配置
PROJECT_ROOT = Path(os.getenv('PROJECT_ROOT'))
LOG_DIR = Path(os.getenv('LOG_DIR'))
MODEL_CHECKPOINT_DIR = Path(os.getenv('MODEL_CHECKPOINT_DIR'))

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'pool_size': int(os.getenv('DB_POOL_SIZE', 5)),
    'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 10)),
    'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', 60)),
    'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 1800))
}

# MT5配置
MT5_CONFIG = {
    'account': int(os.getenv('MT5_ACCOUNT')),
    'password': os.getenv('MT5_PASSWORD'),
    'server': os.getenv('MT5_SERVER'),
    'timeout': int(os.getenv('MT5_TIMEOUT', 60000)),
    'retry_count': int(os.getenv('MT5_RETRY_COUNT', 3)),
    'retry_delay': int(os.getenv('MT5_RETRY_DELAY', 5))
}

# 邮件配置
EMAIL_CONFIG = {
    'server': os.getenv('SMTP_SERVER'),
    'port': int(os.getenv('SMTP_PORT')),
    'username': os.getenv('SMTP_USERNAME'),
    'password': os.getenv('SMTP_PASSWORD'),
    'from_email': os.getenv('SMTP_FROM_EMAIL'),
    'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true',
    'timeout': int(os.getenv('SMTP_TIMEOUT', 30))
}

# Redis配置
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST'),
    'port': int(os.getenv('REDIS_PORT')),
    'password': os.getenv('REDIS_PASSWORD'),
    'ssl': os.getenv('REDIS_SSL', 'false').lower() == 'true',
    'timeout': int(os.getenv('REDIS_TIMEOUT', 5)),
    'max_connections': int(os.getenv('REDIS_MAX_CONNECTIONS', 100)),
    'db': int(os.getenv('REDIS_DB', 0))
}

# 安全配置
SECURITY_CONFIG = {
    'encryption_key': os.getenv('ENCRYPTION_KEY'),
    'jwt_secret': os.getenv('JWT_SECRET_KEY'),
    'api_key_salt': os.getenv('API_KEY_SALT'),
    'password_salt': os.getenv('PASSWORD_SALT')
}

# AI模型配置
AI_CONFIG = {
    'wandb_api_key': os.getenv('WANDB_API_KEY'),
    'wandb_project': os.getenv('WANDB_PROJECT'),
    'wandb_entity': os.getenv('WANDB_ENTITY')
}

# 阿里云OSS配置
OSS_CONFIG = {
    'access_key_id': os.getenv('OSS_ACCESS_KEY_ID'),
    'access_key_secret': os.getenv('OSS_ACCESS_KEY_SECRET')
}

# 交易品种配置
SYMBOLS_CONFIG = {
    # 主要货币对
    'majors': [
        'EURUSD',    # 欧元美元
        'GBPUSD',    # 英镑美元
        'USDJPY',    # 美元日元
        'USDCHF',    # 美元瑞郎
        'USDCAD',    # 美元加元
        'AUDUSD',    # 澳元美元
        'NZDUSD',    # 纽元美元
    ],
    
    # 指数
    'indices': [
        'SPT_DXY',   # 美元指数
        'US30',      # 道琼斯工业指数
        'US500',     # 标普500
        'USTEC',     # 纳斯达克指数
    ],
    
    # 交叉盘
    'crosses': [
        'EURJPY',    # 欧元日元
        'GBPJPY',    # 英镑日元
        'EURGBP',    # 欧元英镑
        'AUDJPY',    # 澳元日元
        'CADJPY',    # 加元日元
        'EURAUD',    # 欧元澳元
        'GBPAUD',    # 英镑澳元
    ],
    
    # 商品
    'commodities': [
        'XAUUSD',    # 黄金
        'XAGUSD',    # 白银
        'WTIUSD',    # 原油
    ]
}

# 交易参数配置
TRADING_CONFIG = {
    'default': {
        'timeframes': [
            mt5.TIMEFRAME_M1,    # 1分钟
            mt5.TIMEFRAME_M5,    # 5分钟
            mt5.TIMEFRAME_M15,   # 15分钟
            mt5.TIMEFRAME_M30,   # 30分钟
            mt5.TIMEFRAME_H1,    # 1小时
            mt5.TIMEFRAME_H4,    # 4小时
            mt5.TIMEFRAME_D1,    # 日线
            mt5.TIMEFRAME_W1,    # 周线
            mt5.TIMEFRAME_MN1    # 月线
        ],
        'short_window': 50,
        'long_window': 200,
        'lot_size': 0.1,
        'stop_loss_pips': 500,
        'take_profit_pips': 1000,
        'magic_number': 234000,
        'deviation': 20,
        'volume_min': 0.01,
        'volume_max': 10.0,
        'volume_step': 0.01
    },
    
    # 美元指数配置
    'SPT_DXY': {
        'timeframes': [
            mt5.TIMEFRAME_M1,    # 1分钟
            mt5.TIMEFRAME_M5,    # 5分钟
            mt5.TIMEFRAME_M15,   # 15分钟
            mt5.TIMEFRAME_M30,   # 30分钟
            mt5.TIMEFRAME_H1,    # 1小时
            mt5.TIMEFRAME_H4,    # 4小时
            mt5.TIMEFRAME_D1,    # 日线
            mt5.TIMEFRAME_W1,    # 周线
            mt5.TIMEFRAME_MN1    # 月线
        ],
        'short_window': 20,
        'long_window': 100,
        'lot_size': 0.05,
        'stop_loss_pips': 300,
        'take_profit_pips': 600,
        'magic_number': 234001,
        'deviation': 20,
        'volume_min': 0.01,
        'volume_max': 5.0,
        'volume_step': 0.01
    }
}

# 时间周期权重配置
TIMEFRAME_WEIGHTS = {
    mt5.TIMEFRAME_M1: 0.05,    # 1分钟权重
    mt5.TIMEFRAME_M5: 0.10,    # 5分钟权重
    mt5.TIMEFRAME_M15: 0.15,   # 15分钟权重
    mt5.TIMEFRAME_M30: 0.15,   # 30分钟权重
    mt5.TIMEFRAME_H1: 0.20,    # 1小时权重
    mt5.TIMEFRAME_H4: 0.15,    # 4小时权重
    mt5.TIMEFRAME_D1: 0.10,    # 日线权重
    mt5.TIMEFRAME_W1: 0.05,    # 周线权重
    mt5.TIMEFRAME_MN1: 0.05    # 月线权重
}

# 时间周期分析配置
TIMEFRAME_ANALYSIS = {
    'trend': {
        'primary': [mt5.TIMEFRAME_H4, mt5.TIMEFRAME_D1, mt5.TIMEFRAME_W1],     # 趋势判断
        'secondary': [mt5.TIMEFRAME_H1, mt5.TIMEFRAME_M30, mt5.TIMEFRAME_M15], # 趋势确认
        'signal': [mt5.TIMEFRAME_M5, mt5.TIMEFRAME_M1]                         # 入场信号
    },
    'momentum': {
        'long': [mt5.TIMEFRAME_W1, mt5.TIMEFRAME_D1],    # 长期动量
        'medium': [mt5.TIMEFRAME_H4, mt5.TIMEFRAME_H1],  # 中期动量
        'short': [mt5.TIMEFRAME_M30, mt5.TIMEFRAME_M15]  # 短期动量
    },
    'volatility': {
        'high': [mt5.TIMEFRAME_M1, mt5.TIMEFRAME_M5],    # 高波动时段
        'medium': [mt5.TIMEFRAME_M15, mt5.TIMEFRAME_M30], # 中波动时段
        'low': [mt5.TIMEFRAME_H1, mt5.TIMEFRAME_H4]      # 低波动时段
    }
}

# 时间周期映射（完整定义）
TIMEFRAMES = {
    'M1': mt5.TIMEFRAME_M1,    # 1分钟
    'M5': mt5.TIMEFRAME_M5,    # 5分钟
    'M15': mt5.TIMEFRAME_M15,  # 15分钟
    'M30': mt5.TIMEFRAME_M30,  # 30分钟
    'H1': mt5.TIMEFRAME_H1,    # 1小时
    'H4': mt5.TIMEFRAME_H4,    # 4小时
    'D1': mt5.TIMEFRAME_D1,    # 日线
    'W1': mt5.TIMEFRAME_W1,    # 周线
    'MN1': mt5.TIMEFRAME_MN1   # 月线
}

# 多时间周期组合策略
TIMEFRAME_STRATEGIES = {
    'trend_following': {
        'trend_timeframe': mt5.TIMEFRAME_D1,     # 判断趋势方向
        'entry_timeframe': mt5.TIMEFRAME_H4,     # 入场时机
        'exit_timeframe': mt5.TIMEFRAME_H1       # 出场时机
    },
    'scalping': {
        'trend_timeframe': mt5.TIMEFRAME_H1,     # 判断短期趋势
        'entry_timeframe': mt5.TIMEFRAME_M5,     # 快速入场
        'exit_timeframe': mt5.TIMEFRAME_M1       # 快速出场
    },
    'swing_trading': {
        'trend_timeframe': mt5.TIMEFRAME_W1,     # 判断大趋势
        'entry_timeframe': mt5.TIMEFRAME_D1,     # 择机入场
        'exit_timeframe': mt5.TIMEFRAME_H4       # 择机出场
    }
}

# 订单类型映射
ORDER_TYPES = {
    'BUY': mt5.ORDER_TYPE_BUY,                    # 市价买入
    'SELL': mt5.ORDER_TYPE_SELL,                  # 市价卖出
    'BUY_LIMIT': mt5.ORDER_TYPE_BUY_LIMIT,        # 限价买入
    'SELL_LIMIT': mt5.ORDER_TYPE_SELL_LIMIT,      # 限价卖出
    'BUY_STOP': mt5.ORDER_TYPE_BUY_STOP,          # 停损买入
    'SELL_STOP': mt5.ORDER_TYPE_SELL_STOP         # 停损卖出
}

# 交易会话时间（服务器时间）
TRADING_SESSIONS = {
    'asian': {
        'start': '01:00',
        'end': '08:00',
    },
    'london': {
        'start': '08:00',
        'end': '16:00',
    },
    'new_york': {
        'start': '13:00',
        'end': '22:00',
    }
}

# 相关性配置
CORRELATION_CONFIG = {
    'lookback_period': 30,  # 相关性计算周期（天）
    'min_correlation': 0.7, # 最小相关系数
    'update_interval': 24,  # 相关性更新间隔（小时）
    'pairs': [
        ('EURUSD', 'SPT_DXY'),  # 欧元美元与美元指数
        ('GBPUSD', 'SPT_DXY'),  # 英镑美元与美元指数
        ('XAUUSD', 'SPT_DXY'),  # 黄金与美元指数
        ('USDJPY', 'SPT_DXY'),  # 美元日元与美元指数
    ]
}

# 风险管理配置
RISK_CONFIG = {
    'max_positions_per_symbol': 3,      # 每个品种最大持仓数
    'max_daily_trades': 10,             # 每日最大交易次数
    'max_risk_per_trade': 0.02,         # 每笔交易最大风险（账户余额的2%）
    'max_daily_drawdown': 0.05,         # 每日最大回撤（账户余额的5%）
    'correlation_threshold': 0.75,       # 相关性阈值
    'max_correlated_positions': 2,       # 高相关品种最大同向持仓数
    'margin_call_level': 100,           # 保证金预警水平（百分比）
    'stop_out_level': 50               # 强制平仓水平（百分比）
}

if __name__ == "__main__":
    print("配置文件加载成功！")
    print("\n=== MT5配置 ===")
    print(f"MT5账号: {MT5_CONFIG['account']}")
    print(f"MT5服务器: {MT5_CONFIG['server']}")
    
    print("\n=== 交易品种 ===")
    print("主要货币对:", SYMBOLS_CONFIG['majors'])
    print("指数:", SYMBOLS_CONFIG['indices'])
    
    print("\n=== 时间周期 ===")
    for name, tf in TIMEFRAMES.items():
        print(f"{name}: {tf}")
