"""
策略测试脚本
测试均线交叉策略的基本功能
"""
import asyncio
from backend.app.services.strategy_service import strategy_service

async def test_ma_cross_strategy():
    """测试均线交叉策略"""
    print("=== 均线交叉策略测试 ===\n")
    
    try:
        # 1. 创建策略
        print("1. 创建策略...")
        strategy = await strategy_service.create_strategy(
            strategy_type="MA_CROSS",
            symbol="BTC/USDT",
            params={
                "short_window": 5,
                "long_window": 10
            }
        )
        print(f"策略创建成功: {strategy.name}\n")
        
        # 2. 运行策略
        print("2. 运行策略...")
        success = await strategy_service.run_strategy("MA_CROSS_BTC/USDT")
        print(f"策略运行{'成功' if success else '失败'}\n")
        
        # 3. 检查策略状态
        print("3. 策略状态:")
        state = strategy_service.get_strategy_state("MA_CROSS_BTC/USDT")
        for key, value in state.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"\n错误: {str(e)}")
        raise
    
    print("\n测试完成!")

if __name__ == "__main__":
    asyncio.run(test_ma_cross_strategy()) 