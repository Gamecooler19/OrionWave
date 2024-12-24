import numpy as np
from typing import Dict, Any, Callable
import threading
import time
import logging

logger = logging.getLogger(__name__)

class ParameterAutomation:
    def __init__(self):
        self.automations: Dict[str, Dict[str, Any]] = {}
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    def add_automation(self, param_name: str, 
                      start_value: float,
                      end_value: float,
                      duration: float,
                      curve: str = 'linear',
                      callback: Callable = None):
        """Add parameter automation"""
        with self._lock:
            self.automations[param_name] = {
                'start_value': start_value,
                'end_value': end_value,
                'duration': duration,
                'start_time': time.time(),
                'curve': curve,
                'callback': callback
            }
        
        if not self._running:
            self._start_automation_thread()

    def _start_automation_thread(self):
        self._running = True
        self._thread = threading.Thread(target=self._automation_loop)
        self._thread.daemon = True
        self._thread.start()

    def _automation_loop(self):
        while self._running:
            current_time = time.time()
            
            with self._lock:
                completed = []
                for param_name, auto in self.automations.items():
                    progress = (current_time - auto['start_time']) / auto['duration']
                    
                    if progress >= 1.0:
                        if auto['callback']:
                            auto['callback'](param_name, auto['end_value'])
                        completed.append(param_name)
                        continue

                    # Calculate current value based on curve
                    if auto['curve'] == 'exponential':
                        value = self._exponential_interpolate(
                            auto['start_value'],
                            auto['end_value'],
                            progress
                        )
                    else:  # linear
                        value = self._linear_interpolate(
                            auto['start_value'],
                            auto['end_value'],
                            progress
                        )

                    if auto['callback']:
                        auto['callback'](param_name, value)

                # Remove completed automations
                for param_name in completed:
                    del self.automations[param_name]

                if not self.automations:
                    self._running = False
                    break

            time.sleep(0.016)  # ~60 fps

    @staticmethod
    def _linear_interpolate(start: float, end: float, progress: float) -> float:
        return start + (end - start) * progress

    @staticmethod
    def _exponential_interpolate(start: float, end: float, progress: float) -> float:
        return start + (end - start) * (1 - np.exp(-5 * progress))
