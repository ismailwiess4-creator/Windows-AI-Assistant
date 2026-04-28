"""
Unit tests for emergency_stop.py
Run with: pytest tests/test_emergency_stop.py -v
"""
import pytest
import time
from unittest.mock import Mock, patch
import sys
sys.path.insert(0, '..')
from src.windows_ai.emergency_stop import brake, EmergencyBrake

class TestEmergencyBrake:
    def test_initialization(self):
        brake_instance = EmergencyBrake()
        assert brake_instance.engaged == False
        assert brake_instance.last_tap == 0
        assert brake_instance.thread == None

    def test_toggle_engaged(self):
        brake_instance = EmergencyBrake()
        # Simulate double-tap
        brake_instance.last_tap = time.time() - 0.5
        brake_instance._on_combo()
        assert brake_instance.engaged == True
        
        # Toggle again
        brake_instance.last_tap = time.time() - 0.5
        brake_instance._on_combo()
        assert brake_instance.engaged == False

    def test_single_tap_does_not_toggle(self):
        brake_instance = EmergencyBrake()
        # Single tap (too long ago)
        brake_instance.last_tap = time.time() - 2.0
        brake_instance._on_combo()
        assert brake_instance.engaged == False

    def test_double_tap_within_one_second(self):
        brake_instance = EmergencyBrake()
        # First tap
        brake_instance._on_combo()
        first_tap_time = brake_instance.last_tap
        
        # Second tap within 1 second
        time.sleep(0.1)
        brake_instance._on_combo()
        
        assert brake_instance.engaged == True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
