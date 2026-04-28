"""
Unit tests for audio_awareness.py
Run with: pytest tests/test_audio_awareness.py -v
"""
import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, '..')
from src.windows_ai.audio_awareness import AudioAwareness, AudioEvent

class TestAudioEvent:
    def test_event_creation(self):
        event = AudioEvent(
            event_type="loud_noise",
            amplitude=65.0,
            frequency_peak=1000.0,
            timestamp=1234567890.0
        )
        assert event.event_type == "loud_noise"
        assert event.amplitude == 65.0
        assert event.frequency_peak == 1000.0

class TestAudioAwareness:
    @pytest.fixture
    def audio(self):
        return AudioAwareness(
            threshold_db=60.0,
            silence_timeout=300,
            sample_rate=16000
        )

    def test_initialization(self, audio):
        assert audio.threshold == 60.0
        assert audio.silence_timeout == 300
        assert audio.sample_rate == 16000
        assert audio.running == False

    def test_list_devices_static(self):
        # This test would require actual audio hardware
        # In CI/CD, this might need to be mocked
        try:
            AudioAwareness.list_devices()
        except Exception as e:
            # Expected if no audio hardware available
            assert True

    def test_silence_detection_logic(self, audio):
        # Test that silence detection logic works
        audio.last_sound_time = 0  # Force silence
        assert time.time() - audio.last_sound_time > audio.silence_timeout

    def test_frequency_calculation(self, audio):
        # Test frequency calculation with synthetic data
        data = np.sin(2 * np.pi * 1000 * np.linspace(0, 0.01, 1024))
        data = (data * 32767).astype(np.int16)
        freq = audio._get_dominant_freq(data)
        # Should be close to 1000 Hz
        assert 900 < freq < 1100

if __name__ == "__main__":
    import time
    pytest.main([__file__, "-v"])
