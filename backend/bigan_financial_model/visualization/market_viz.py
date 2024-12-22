"""市场可视化模块"""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from typing import Optional
import matplotlib as mpl
from matplotlib.font_manager import FontProperties

class MarketVisualizer:
    """市场可视化器"""
    
    def __init__(self):
        """初始化可视化器"""
        # 检查系统字体
        self._setup_chinese_font()
        
        # 设置绘图风格
        plt.style.use('default')
        sns.set_theme(style="whitegrid")
        
    def _setup_chinese_font(self):
        """设置中文字体"""
        try:
            # Windows 常见中文字体
            fonts = ['Microsoft YaHei', 'SimSun', 'KaiTi', 'FangSong', 'SimHei']
            
            # 打印当前系统可用的字体
            from matplotlib.font_manager import FontManager
            fm = FontManager()
            system_fonts = set([f.name for f in fm.ttflist])
            print("系统可用的中文字体:")
            available_chinese_fonts = []
            for font in fonts:
                if font in system_fonts:
                    available_chinese_fonts.append(font)
                    print(f"- {font}")
                    
            if available_chinese_fonts:
                # 使用找到的第一个中文字体
                plt.rcParams['font.sans-serif'] = [available_chinese_fonts[0]] + plt.rcParams['font.sans-serif']
                print(f"使用字体: {available_chinese_fonts[0]}")
            else:
                print("警告: 未找到中文字体，图表可能无法正确显示中文")
                
            plt.rcParams['axes.unicode_minus'] = False
            
        except Exception as e:
            print(f"字体设置错误: {str(e)}")
            
    def plot_market_overview(
        self,
        df: pd.DataFrame,
        title: Optional[str] = None,
        save_path: Optional[str] = None,
        use_english: bool = True
    ) -> None:
        """绘制市场概览"""
        # 创建子图
        fig, axes = plt.subplots(4, 1, figsize=(15, 20), 
                                gridspec_kw={'height_ratios': [3, 1, 1, 1]})
        
        # 设置标签语言
        labels = {
            'price': 'Price' if use_english else '价格',
            'ma20': '20 Day MA' if use_english else '20日均线',
            'ma50': '50 Day MA' if use_english else '50日均线',
            'bb_upper': 'Bollinger Upper' if use_english else '布林上轨',
            'bb_lower': 'Bollinger Lower' if use_english else '布林下轨',
            'volume': 'Volume' if use_english else '成交量',
            'date': 'Date' if use_english else '日期',
            'signal': 'Signal' if use_english else '信号线',
            'histogram': 'Histogram' if use_english else '柱状图',
            'volume_ma': 'Volume MA' if use_english else '成交量均线'
        }
        
        # 1. 价格和指标
        axes[0].plot(df.index, df['close'], label=labels['price'], linewidth=2)
        axes[0].plot(df.index, df['sma_20'], '--', label=labels['ma20'], alpha=0.8)
        axes[0].plot(df.index, df['sma_50'], '--', label=labels['ma50'], alpha=0.8)
        axes[0].plot(df.index, df['bb_upper'], ':', label=labels['bb_upper'], alpha=0.6)
        axes[0].plot(df.index, df['bb_lower'], ':', label=labels['bb_lower'], alpha=0.6)
        axes[0].fill_between(df.index, df['bb_upper'], df['bb_lower'], alpha=0.1)
        axes[0].set_title('BTC-USD Market Overview')
        axes[0].legend(loc='upper left')
        axes[0].grid(True)
        
        # 2. MACD
        axes[1].plot(df.index, df['macd'], label='MACD')
        axes[1].plot(df.index, df['macd_signal'], label='Signal')
        axes[1].bar(df.index, df['macd'] - df['macd_signal'], alpha=0.3, label='Histogram')
        axes[1].set_title('MACD Indicator')
        axes[1].legend(loc='upper left')
        axes[1].grid(True)
        
        # 3. RSI
        axes[2].plot(df.index, df['rsi'], label='RSI')
        axes[2].axhline(y=70, color='r', linestyle='--', alpha=0.5)
        axes[2].axhline(y=30, color='g', linestyle='--', alpha=0.5)
        axes[2].set_title('RSI Indicator')
        axes[2].legend(loc='upper left')
        axes[2].grid(True)
        
        # 4. 成交量
        volume_colors = ['g' if r >= 0 else 'r' for r in df['returns']]
        axes[3].bar(df.index, df['volume'], color=volume_colors, alpha=0.6)
        axes[3].plot(df.index, df['volume_ma'], 'r', label='Volume MA', linewidth=2)
        axes[3].set_title('Volume')
        axes[3].legend(loc='upper left')
        axes[3].grid(True)
        
        # 设置标签
        axes[0].set_ylabel(labels['price'])
        axes[1].set_ylabel('MACD Value')
        axes[2].set_ylabel('RSI Value')
        axes[3].set_ylabel(labels['volume'])
        
        for ax in axes:
            ax.set_xlabel(labels['date'])
            
        # 调整布局
        plt.tight_layout(pad=2.0)
        
        # 保存或显示
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
            
    def plot_returns_distribution(
        self,
        df: pd.DataFrame,
        save_path: Optional[str] = None
    ) -> None:
        """绘制收益率分布"""
        plt.figure(figsize=(12, 6))
        
        # 绘制直方图和核密度估计
        sns.histplot(data=df['returns'], bins=50, stat='density', alpha=0.5)
        sns.kdeplot(data=df['returns'], color='r')
        
        # 添加均值和标准差线
        plt.axvline(df['returns'].mean(), color='g', linestyle='--', label='Mean')
        plt.axvline(df['returns'].mean() + df['returns'].std(), 
                   color='r', linestyle=':', label='+1 Standard Deviation')
        plt.axvline(df['returns'].mean() - df['returns'].std(), 
                   color='r', linestyle=':', label='-1 Standard Deviation')
        
        plt.title('Returns Distribution')
        plt.xlabel('Returns')
        plt.ylabel('Density')
        plt.legend()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
