"""风险分析模块"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import FontProperties
from scipy import stats
import warnings
import platform
import matplotlib as mpl
from datetime import datetime
import os

class RiskAnalysis:
    """风险分析工具"""
    
    @staticmethod
    def configure_chinese_font() -> str:
        """
        配置中文字体
        Returns:
            str: 成功加载的字体名称
        """
        system = platform.system()
        
        if system == 'Windows':
            font_list = ['Microsoft YaHei', 'SimHei', 'SimSun']
            for font in font_list:
                try:
                    plt.rcParams['font.sans-serif'] = [font]
                    plt.rcParams['axes.unicode_minus'] = False
                    test_fig = plt.figure()
                    test_fig.text(0.5, 0.5, '测试中文')
                    plt.close(test_fig)
                    print(f"使用字体: {font}")
                    return font
                except Exception as e:
                    print(f"字体 {font} 加载失败: {str(e)}")
                    continue
        elif system == 'Linux':
            try:
                font = 'WenQuanYi Micro Hei'
                plt.rcParams['font.sans-serif'] = [font]
                return font
            except Exception as e:
                print(f"Linux字体加载失败: {str(e)}")
        
        warnings.warn("未找到合适的中文字体，将使用系统默认字体")
        return "default"
    
    @staticmethod
    def calculate_risk_metrics(returns: pd.Series) -> Dict[str, float]:
        """
        计算风险指标
        Args:
            returns: 收益率序列
        Returns:
            Dict[str, float]: 风险指标字典
        """
        metrics = {
            '年化收益率': returns.mean() * 252,
            '年化波动率': returns.std() * np.sqrt(252),
            '夏普比率': (returns.mean() * 252) / (returns.std() * np.sqrt(252)),
            'VaR(95%)': np.percentile(returns, 5),
            'CVaR(95%)': returns[returns <= np.percentile(returns, 5)].mean(),
            '最大回撤': (1 - (1 + returns).cumprod() / (1 + returns).cumprod().expanding().max()).max()
        }
        return metrics

    @staticmethod
    def set_plot_style() -> None:
        """设置绘图样式"""
        RiskAnalysis.configure_chinese_font()
        
        sns.set_style("whitegrid", {
            'font.sans-serif': plt.rcParams['font.sans-serif'],
            'axes.unicode_minus': False
        })
        
        plt.rcParams.update({
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'grid.color': '#666666',
            'grid.linestyle': ':',
            'grid.alpha': 0.3,
            'xtick.labelsize': 8,
            'ytick.labelsize': 8,
            'axes.titlesize': 10,
            'axes.labelsize': 9,
        })

    @staticmethod
    def save_plot(fig: plt.Figure, filename: Optional[str] = None) -> str:
        """
        保存图表
        Args:
            fig: matplotlib图形对象
            filename: 文件名（可选）
        Returns:
            str: 保存的文件路径
        """
        if filename is None:
            filename = f"risk_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        save_dir = "output/figures"
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, filename)
        
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"图表已保存至: {filepath}")
        return filepath

    @staticmethod
    def plot_risk_dashboard(
        returns: pd.Series,
        prices: pd.Series,
        volume: pd.Series,
        market_returns: Optional[pd.Series] = None,
        figsize: Tuple[int, int] = (15, 10),
        save_plot: bool = True
    ) -> Optional[str]:
        """
        绘制风险分析仪表盘
        Args:
            returns: 收益率序列
            prices: 价格序列
            volume: 成交量序列
            market_returns: 市场收益率序列（可选）
            figsize: 图表大小
            save_plot: 是否保存图表
        Returns:
            Optional[str]: 如果save_plot为True，返回保存的文件路径
        """
        print("开始生成风险分析图表...")
        
        # 计算风险指标
        metrics = RiskAnalysis.calculate_risk_metrics(returns)
        print("\n风险指标:")
        for key, value in metrics.items():
            print(f"{key}: {value:.2%}")
        
        # 设置绘图样式
        RiskAnalysis.set_plot_style()
        print("\n样式设置完成...")
        
        # 创建图形和子图布局
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
        print("布局初始化完成...")
        
        # 1. 收益分布
        ax1 = fig.add_subplot(gs[0, 0])
        sns.histplot(returns, ax=ax1, kde=True, color='skyblue')
        ax1.set_title('收益率分布')
        ax1.set_xlabel('收益率')
        ax1.set_ylabel('频数')
        
        # 2. Q-Q图
        ax2 = fig.add_subplot(gs[0, 1])
        RiskAnalysis.plot_qq(returns, ax2)
        
        # 3. 波动率走势
        ax3 = fig.add_subplot(gs[0, 2])
        rolling_vol = returns.rolling(30).std() * np.sqrt(252)
        rolling_vol.plot(ax=ax3, color='red', alpha=0.7)
        ax3.set_title('30日滚动波动率')
        ax3.set_xlabel('日期')
        ax3.set_ylabel('波动率')
        
        # 4. 价格和成交量
        ax4 = fig.add_subplot(gs[1, :])
        ax4.plot(prices.index, prices, label='价格', color='blue')
        ax4_twin = ax4.twinx()
        ax4_twin.fill_between(volume.index, volume, alpha=0.3, color='gray', label='成交量')
        ax4.set_title('价格和成交量走势')
        ax4.set_xlabel('日期')
        ax4.set_ylabel('价格')
        ax4_twin.set_ylabel('成交量')
        
        # 合并图例
        lines1, labels1 = ax4.get_legend_handles_labels()
        lines2, labels2 = ax4_twin.get_legend_handles_labels()
        ax4_twin.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        
        # 5. 回撤分析
        ax5 = fig.add_subplot(gs[2, 0])
        cum_returns = (1 + returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = (cum_returns - rolling_max) / rolling_max
        drawdowns.plot(ax=ax5, color='red')
        ax5.set_title('回撤走势')
        ax5.set_xlabel('日期')
        ax5.set_ylabel('回撤幅度')
        
        # 6. 相关性热图
        if market_returns is not None:
            ax6 = fig.add_subplot(gs[2, 1])
            corr_data = pd.DataFrame({
                '资产收益': returns,
                '市场收益': market_returns
            })
            sns.heatmap(corr_data.corr(), 
                       annot=True, 
                       cmap='RdYlBu', 
                       ax=ax6,
                       cbar_kws={'shrink': 0.8})
            ax6.set_title('相关性热图')
        
        # 7. 尾部风险
        ax7 = fig.add_subplot(gs[2, 2])
        RiskAnalysis.plot_tail_risk(returns, ax=ax7)
        
        # 调整布局
        fig.align_labels()
        print("图表生成完成！")
        
        # 保存图表
        filepath = None
        if save_plot:
            filepath = RiskAnalysis.save_plot(fig)
        
        # 显示图形
        plt.show()
        return filepath

    @staticmethod
    def plot_qq(returns: pd.Series, ax: plt.Axes) -> None:
        """
        绘制Q-Q图（Quantile-Quantile Plot）
        
        Args:
            returns: 收益率序列
            ax: matplotlib轴对象
        """
        try:
            # 使用scipy.stats进行正态性检验
            qq = stats.probplot(returns, dist="norm", plot=ax)
            ax.set_title('正态Q-Q图')
            ax.set_xlabel('理论分位数')
            ax.set_ylabel('观测值')
            print("Q-Q图绘制完成...")
        except Exception as e:
            warnings.warn(f"绘制Q-Q图时出错: {str(e)}")
            ax.text(0.5, 0.5, '无法生成Q-Q图', 
                   horizontalalignment='center',
                   verticalalignment='center')
            print(f"Q-Q图绘制失败: {str(e)}")

    @staticmethod
    def plot_tail_risk(
        returns: pd.Series, 
        ax: Optional[plt.Axes] = None
    ) -> None:
        """
        绘制尾部风险分析图
        
        Args:
            returns: 收益率序列
            ax: matplotlib轴对象（可选）
        """
        if ax is None:
            _, ax = plt.subplots(figsize=(8, 6))
            
        # 计算VaR和CVaR
        var_95 = np.percentile(returns, 5)
        cvar_95 = returns[returns <= var_95].mean()
        
        # 绘制分布
        sns.histplot(returns, ax=ax, kde=True)
        
        # 标记VaR和CVaR
        ax.axvline(var_95, color='r', linestyle='--', 
                  label=f'VaR(95%): {var_95:.2%}')
        ax.axvline(cvar_95, color='g', linestyle='--', 
                  label=f'CVaR(95%): {cvar_95:.2%}')
        
        ax.set_title('尾部风险分析')
        ax.legend()
        print("尾部风险分析图绘制完成...")

if __name__ == '__main__':
    try:
        print("正在准备数据...")
        # 创建测试数据
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=252, freq='D')
        
        # 生成模拟数据
        returns = pd.Series(np.random.normal(0.0001, 0.02, len(dates)), index=dates)
        prices = pd.Series(100 * (1 + returns).cumprod(), index=dates)
        volume = pd.Series(np.random.lognormal(10, 1, len(dates)), index=dates)
        market_returns = pd.Series(np.random.normal(0.0002, 0.015, len(dates)), index=dates)
        print("数据准备完成...")
        
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=UserWarning)
            filepath = RiskAnalysis.plot_risk_dashboard(
                returns=returns,
                prices=prices,
                volume=volume,
                market_returns=market_returns,
                save_plot=True
            )
            
    except Exception as e:
        print(f"\n程序执行出错: {str(e)}")
        print("详细错误信息:")
        import traceback
        traceback.print_exc()
    else:
        print("\n程序执行完成！")
        if filepath:
            print(f"图表已保存至: {filepath}")