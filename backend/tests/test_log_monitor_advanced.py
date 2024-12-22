import sys
import time
import threading
import random
from pathlib import Path
import psutil
from concurrent.futures import ThreadPoolExecutor
from backend.app.utils.log_monitor import log_monitor
from backend.app.utils.logger import setup_logger

def test_long_term_stability():
    """长期稳定性测试 (运行1小时)"""
    print("\n=== 长期稳定性测试 ===")
    logger = setup_logger("test.stability")
    
    start_time = time.time()
    test_duration = 3600  # 1小时
    
    try:
        while time.time() - start_time < test_duration:
            # 随机生成不同类型的日志
            log_type = random.choice(['info', 'warning', 'error'])
            if log_type == 'info':
                logger.info(f"定期信息日志: {time.time()}")
            elif log_type == 'warning':
                logger.warning(f"定期警告日志: {time.time()}")
            else:
                try:
                    raise ValueError("模拟错误")
                except:
                    logger.error("定期错误日志", exc_info=True)
            
            # 随机等待
            time.sleep(random.uniform(0.1, 1.0))
            
            # 每10分钟输出一次状态
            elapsed = time.time() - start_time
            if elapsed % 600 < 1:  # 每10分钟
                print(f"稳定性测试运行中: {elapsed/3600:.1f}小时")
                
    except KeyboardInterrupt:
        print("\n稳定性测试被手动中断")
    finally:
        print(f"稳定性测试完成，运行时间: {(time.time()-start_time)/3600:.1f}小时")

def test_high_concurrency():
    """高并发测试"""
    print("\n=== 高并发测试 ===")
    logger = setup_logger("test.concurrency")
    
    def worker(worker_id):
        for i in range(100):
            try:
                if random.random() < 0.1:  # 10%概率产生错误
                    raise ValueError(f"并发错误 #{i}")
                logger.info(f"并发消息 from worker {worker_id}: {i}")
                time.sleep(random.uniform(0.01, 0.05))
            except Exception as e:
                logger.error(f"并发错误 from worker {worker_id}", exc_info=True)
    
    # 使用线程池模拟高并发
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(worker, i) for i in range(20)]
        for future in futures:
            future.result()

def test_network_failure():
    """网络异常测试"""
    print("\n=== 网络异常测试 ===")
    logger = setup_logger("test.network")
    
    def simulate_network_issue():
        """模拟网络问题"""
        time.sleep(random.uniform(1, 3))
        raise ConnectionError("模拟网络连接失败")
    
    for i in range(10):
        try:
            simulate_network_issue()
        except ConnectionError:
            logger.error("网络连接失败", exc_info=True)
            time.sleep(random.uniform(0.5, 2))

def test_disk_space():
    """磁盘空间测试"""
    print("\n=== 磁盘空间测试 ===")
    logger = setup_logger("test.disk")
    
    def check_disk_space():
        """检查磁盘空间"""
        disk = psutil.disk_usage('/')
        return disk.percent
    
    # 模拟磁盘空间不足
    while True:
        usage = check_disk_space()
        logger.warning(f"磁盘使用率: {usage}%")
        if usage > 90:
            logger.error("磁盘空间严重不足!")
            break
        
        # 写入大量数据
        large_data = "x" * (1024 * 1024)  # 1MB
        logger.info(f"写入大量数据: {len(large_data)} bytes")
        time.sleep(1)

def test_resource_limits():
    """资源限制测试"""
    print("\n=== 资源限制测试 ===")
    logger = setup_logger("test.resources")
    
    # 测试内存限制
    def consume_memory():
        data = []
        try:
            while True:
                data.append("x" * (1024 * 1024))  # 追加1MB
                if len(data) % 100 == 0:
                    logger.warning(f"当前内存使用: {len(data)}MB")
        except MemoryError:
            logger.error("内存不足!", exc_info=True)
    
    # 测试CPU限制
    def consume_cpu():
        start = time.time()
        while time.time() - start < 60:  # 运行1分钟
            _ = [i**2 for i in range(10000)]
            logger.info(f"CPU使用率: {psutil.cpu_percent()}%")
            time.sleep(0.1)

def main():
    """运行所有高级测试"""
    print("开始高级测试...")
    
    try:
        # 启动监控
        log_monitor.start()
        
        # 运行测试
        test_high_concurrency()
        test_network_failure()
        test_disk_space()
        test_resource_limits()
        
        # 如果需要长期测试，取消下面的注释
        # test_long_term_stability()
        
    except KeyboardInterrupt:
        print("\n测试被手动中断")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
    finally:
        # 停止监控
        log_monitor.stop()
        
        # 显示最终统计
        print("\n=== 测试统计 ===")
        alerts = log_monitor.get_alerts()
        print(f"总告警数: {len(alerts)}")
        print(f"警告数: {sum(1 for a in alerts if a.level == 'WARNING')}")
        print(f"错误数: {sum(1 for a in alerts if a.level == 'ERROR')}")

if __name__ == "__main__":
    main() 