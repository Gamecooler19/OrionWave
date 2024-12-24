import os
import sys
import unittest
import numpy as np

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orionwave import VoiceProcessor, AudioConfig  # Updated import path

class TestVoiceProcessor(unittest.TestCase):
    def setUp(self):
        self.config = AudioConfig()
        try:
            # Initialize without server to avoid port conflicts
            self.processor = VoiceProcessor(self.config, start_server=False)
        except Exception as e:
            self.skipTest(f"Audio initialization failed: {e}")

    def test_pitch_shift(self):
        # Generate test audio data with fixed length
        sample_rate = self.config.RATE
        duration = 0.1  # 100ms
        samples = int(sample_rate * duration)
        
        t = np.linspace(0, duration, samples)
        test_data = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
        test_bytes = test_data.tobytes()
        
        # Apply pitch shift
        shifted = self.processor.pitch_shift(test_bytes, shift=100)
        shifted_data = np.frombuffer(shifted, dtype=np.int16)
        
        # Verify output
        self.assertEqual(len(shifted_data), len(test_data), 
                        "Output length should match input length")
        self.assertNotEqual(np.mean(np.abs(shifted_data - test_data)), 0,
                          "Output should be different from input")

    def test_robot_effect(self):
        # Similar test for robot effect
        duration = 0.1
        t = np.linspace(0, duration, int(self.config.RATE * duration))
        test_data = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
        test_bytes = test_data.tobytes()
        
        robot = self.processor.robot_effect(test_bytes)
        robot_data = np.frombuffer(robot, dtype=np.int16)
        
        self.assertEqual(len(robot_data), len(test_data))
        difference = np.abs(robot_data - test_data).mean()
        self.assertGreater(difference, 100)

    def test_effects_chain(self):
        self.processor.clear_effects()
        self.assertEqual(len(self.processor.effects_chain), 0)
        
        self.processor.add_effect('pitch_shift', {'shift': 100})
        self.assertEqual(len(self.processor.effects_chain), 1)
        
    def tearDown(self):
        self.processor.cleanup()

if __name__ == '__main__':
    unittest.main()
