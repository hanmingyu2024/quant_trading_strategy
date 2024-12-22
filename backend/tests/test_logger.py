import sys
import os
from pathlib import Path
import threading
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from backend.app.utils.logger import setup_logger, get_logger_manager

def test_basic_logging():
    """测试基本日志功能"""
    logger = setup_logger("test.basic")
    
    print("\n=== 测试基本日志功能 ===")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    
    # 检查统计信息
    stats = get_logger_manager().get_stats()
    print("\n日志统计信息:")
    print(f"- 运行时间: {stats['运行时间']:.2f}秒")
    print(f"- 日志器数量: {stats['日志器数量']}")
    print(f"- 系统信息: {stats['系统信息']}")

def test_concurrent_logging():
    """测试并发日志"""
    def worker(thread_id):
        logger = setup_logger(f"test.thread.{thread_id}")
        for i in range(3):
            logger.info(f"线程{thread_id}的第{i+1}条日志")
            time.sleep(0.1)
    
    print("\n=== 测试并发日志 ===")
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

def test_error_logging():
    """测试错误日志"""
    logger = setup_logger("test.error")
    
    print("\n=== 测试错误日志 ===")
    try:
        1/0
    except Exception as e:
        logger.error(f"发生错误: {str(e)}", exc_info=True)

def check_log_file():
    """检查日志文件"""
    log_dir = project_root / "logs"
    print("\n=== 检查日志文件 ===")
    print(f"日志目录: {log_dir}")
    
    if log_dir.exists():
        for log_file in log_dir.glob("*.log"):
            size = log_file.stat().st_size / 1024  # KB
            print(f"- {log_file.name}: {size:.2f}KB")
    else:
        print("日志目录不存在!")

def test_performance_logging():
    """性能压力测试"""
    logger = setup_logger("test.performance")
    
    print("\n=== 性能压力测试 ===")
    start_time = time.time()
    
    # 快速写入1000条日志
    for i in range(1000):
        logger.info(f"性能测试日志 #{i}")
    
    duration = time.time() - start_time
    print(f"写入1000条日志耗时: {duration:.2f}秒")
    print(f"平均每条日志耗时: {(duration/1000)*1000:.2f}毫秒")

def test_large_data_logging():
    """大数据量日志测试"""
    logger = setup_logger("test.large_data")
    
    print("\n=== 大数据量测试 ===")
    # 生成1MB的测试数据
    large_data = "x" * (1024 * 1024)  # 1MB字符串
    
    start_time = time.time()
    logger.info(f"大数据日志测试: {large_data[:100]}... (总长度:{len(large_data)}字节)")
    print(f"写入1MB数据耗时: {time.time() - start_time:.2f}秒")

def test_log_rotation():
    """日志轮转测试"""
    logger = setup_logger("test.rotation")
    
    print("\n=== 日志轮转测试 ===")
    # 写入足够多的数据触发轮转
    for i in range(100):
        large_data = "x" * 1024 * 100  # 100KB
        logger.info(f"轮转测试 #{i}: {large_data[:50]}...")
    
    # 检查日志文件
    log_dir = project_root / "logs"
    print("\n轮转后的日志文件:")
    for log_file in sorted(log_dir.glob("*.log*")):
        size = log_file.stat().st_size / (1024 * 1024)  # MB
        print(f"- {log_file.name}: {size:.2f}MB")

def test_error_recovery():
    """错误恢复测试"""
    logger = setup_logger("test.recovery")
    
    print("\n=== 错误恢复测试 ===")
    
    # 模拟各种异常情况
    test_cases = [
        ("除零错误", lambda: 1/0),
        ("类型错误", lambda: len(None)),
        ("索引错误", lambda: [][0]),
        ("键错误", lambda: {}["不存在的键"]),
        ("属性错误", lambda: object().不存在的属性)
    ]
    
    for case_name, error_func in test_cases:
        try:
            error_func()
        except Exception as e:
            logger.error(f"{case_name}: {str(e)}", exc_info=True)
            print(f"成功捕获并记录 {case_name}")

def main():
    """运行所有测试"""
    print("开始日志系统测试...")
    
    # 基础测试
    test_basic_logging()
    test_concurrent_logging()
    test_error_logging()
    
    # 补充测试
    test_performance_logging()
    test_large_data_logging()
    test_log_rotation()
    test_error_recovery()
    
    # 等待所有日志写入
    time.sleep(1)
    
    # 检查日志文件
    check_log_file()
    
    # 输出最终统计
    stats = get_logger_manager().get_stats()
    print("\n=== 最终统计信息 ===")
    print(f"总运行时间: {stats['运行时间']:.2f}秒")
    print(f"总日志器数量: {stats['日志器数量']}")
    print("系统资源使用:")
    for key, value in stats['系统信息'].items():
        print(f"- {key}: {value}")
    
    print("\n所有测试完成!")

if __name__ == "__main__":
    main() 