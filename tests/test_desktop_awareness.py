"""
Unit tests for desktop_awareness.py
Run with: pytest tests/test_desktop_awareness.py -v
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, '..')
from src.windows_ai.desktop_awareness import DesktopEvent, DesktopAwareness

class TestDesktopEvent:
    def test_event_creation(self):
        event = DesktopEvent(
            event_type="motion",
            timestamp=1234567890.0,
            confidence=0.95,
            region=(0, 0, 1920, 1080),
            screenshot_base64="base64string"
        )
        assert event.event_type == "motion"
        assert event.confidence == 0.95
        assert event.region == (0, 0, 1920, 1080)

class TestDesktopAwareness:
    @pytest.fixture
    def awareness(self):
        return DesktopAwareness(config={
            "capture_fps": 10,
            "motion_threshold": 0.03,
            "window_check_interval": 2,
            "llm_cooldown": 5
        })

    def test_downscale_4k_to_1080p(self, awareness):
        # Simulate 4K frame (3840x2160x3)
        frame_4k = np.random.randint(0, 255, (2160, 3840, 3), dtype=np.uint8)
        downscaled = awareness._capture_frame()
        # Note: This test is simplified - actual capture uses mss
        # In real tests, you'd mock mss and test the downscaling logic separately

    def test_motion_detection_no_motion(self, awareness):
        # Two identical frames → no motion
        frame1 = np.zeros((1080, 1920, 3), dtype=np.uint8)
        awareness.prev_frame = frame1
        frame2 = np.zeros((1080, 1920, 3), dtype=np.uint8)
        event = awareness._detect_motion(frame2)
        assert event is None

    def test_motion_detection_with_motion(self, awareness):
        # Frames with >3% difference → motion detected
        frame1 = np.zeros((1080, 1920, 3), dtype=np.uint8)
        awareness.prev_frame = frame1
        frame2 = frame1.copy()
        # Change enough pixels to trigger motion
        frame2[0:324, 0:576, :] = 255  # ~30% × 30% = 9% area → should trigger
        event = awareness._detect_motion(frame2)
        assert event is not None
        assert event.event_type == "motion"

    def test_ignore_regions_prevent_false_positives(self, awareness):
        # Add taskbar region to ignore
        awareness.ignore_regions = [(0, 1000, 1920, 1080)]  # Bottom 80px
        frame1 = np.zeros((1080, 1920, 3), dtype=np.uint8)
        awareness.prev_frame = frame1
        frame2 = frame1.copy()
        # Change only in ignored region (taskbar)
        frame2[1000:1080, :, :] = 255
        event = awareness._detect_motion(frame2)
        assert event is None  # Should be ignored

    @patch('src.windows_ai.desktop_awareness.pygetwindow.get_active_window')
    def test_window_change_detection(self, mock_get_window, awareness):
        mock_get_window.return_value = "Notepad"
        awareness.prev_window_title = "Chrome"
        event = awareness._detect_window_change()
        assert event is not None
        assert event.event_type == "window_change"
        assert "Notepad" in event.metadata.get("window_title", "")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
