import time
import psutil
import json
from contextlib import contextmanager
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self):
        self.timings = {}
        self.timing_counts = {}
        self.process = psutil.Process()
        self.start_time = time.time()

    @contextmanager
    def measure_performance(self, operation: str):
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            if operation not in self.timings:
                self.timings[operation] = 0
                self.timing_counts[operation] = 0
            self.timings[operation] += duration
            self.timing_counts[operation] += 1

    def get_average_time(self, operation: str) -> float:
        if operation in self.timings:
            return self.timings[operation] / self.timing_counts[operation]
        return 0.0

    def get_all_timings(self) -> Dict[str, float]:
        return {op: self.get_average_time(op) for op in self.timings}

    def get_cpu_usage(self) -> float:
        return self.process.cpu_percent()

    def get_memory_usage(self) -> Dict[str, float]:
        mem_info = self.process.memory_info()
        return {
            "rss": mem_info.rss / 1024 / 1024,  # MB
            "vms": mem_info.vms / 1024 / 1024   # MB
        }

    def save_statistics(self):
        stats = {
            "total_runtime": time.time() - self.start_time,
            "average_timings": self.get_all_timings(),
            "cpu_usage": self.get_cpu_usage(),
            "memory_usage": self.get_memory_usage()
        }
        
        try:
            with open("performance_stats.json", "w") as f:
                json.dump(stats, f, indent=2)
            logger.info("Performance statistics saved")
        except Exception as e:
            logger.error(f"Failed to save performance statistics: {e}")
