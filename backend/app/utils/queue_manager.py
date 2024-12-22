from typing import Any, List
import asyncio
import threading
from queue import Queue
import time

class QueueManager:
    def __init__(self, batch_size: int = 10, delay: float = 1.0):
        self.queue = Queue()
        self.batch_size = batch_size
        self.delay = delay
        self.is_processing = False
        self._lock = threading.Lock()
        
    def add_task(self, task: Any):
        """添加任务到队列"""
        self.queue.put(task)
        
    def get_queue_size(self) -> int:
        """获取当前队列大小"""
        return self.queue.qsize()
        
    async def process_queue(self):
        """处理队列中的任务"""
        if self.is_processing:
            return
            
        with self._lock:
            self.is_processing = True
            
        try:
            while not self.queue.empty():
                # 批量处理任务
                batch = []
                for _ in range(min(self.batch_size, self.queue.qsize())):
                    if not self.queue.empty():
                        batch.append(self.queue.get())
                        
                if batch:
                    await self._process_batch(batch)
                    await asyncio.sleep(self.delay)
        finally:
            with self._lock:
                self.is_processing = False
                
    async def _process_batch(self, batch: List[Any]):
        """处理一批任务"""
        # 实现具体的批处理逻辑
        pass

# 创建全局实例
queue_manager = QueueManager() 