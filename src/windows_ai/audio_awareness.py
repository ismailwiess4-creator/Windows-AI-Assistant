"""
Audio Awareness Module for Windows AI Assistant
Detects loud noises, silence, and audio patterns
"""

import pyaudio
import numpy as np
import threading
import queue
import time
from collections import deque
from dataclasses import dataclass

@dataclass
class AudioEvent:
    event_type: str  # 'loud_noise', 'sustained_speech', 'silence', 'pattern_match'
    amplitude: float
    frequency_peak: float
    timestamp: float

class AudioAwareness:
    def __init__(self, 
                 threshold_db: float = 60.0,  # Trigger above 60dB
                 silence_timeout: float = 300,  # Alert after 5 min silence
                 sample_rate: int = 16000,
                 device_index: int = None):  # None = default device
        
        self.threshold = threshold_db
        self.silence_timeout = silence_timeout
        self.sample_rate = sample_rate
        self.device_index = device_index
        
        self.running = False
        self.event_queue = queue.Queue()
        self.audio_history = deque(maxlen=100)
        
        # Silence detection
        self.last_sound_time = time.time()
        self.silence_alerted = False
    
    @staticmethod
    def list_devices():
        """List available audio input devices"""
        p = pyaudio.PyAudio()
        print("\nAvailable audio input devices:")
        print("-" * 60)
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"[{i}] {info['name']}")
        p.terminate()
    
    def start(self):
        try:
            self.running = True
            self.thread = threading.Thread(target=self._listen, daemon=True)
            self.thread.start()
            print("[Audio] Microphone awareness active")
        except Exception as e:
            print(f"[Audio] Failed to start: {e}")
            print("[Audio] Try running audio_awareness.py to list devices")
            self.running = False
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        print("[Audio] Microphone awareness stopped")
        
    def _listen(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                       channels=1,
                       rate=self.sample_rate,
                       input=True,
                       input_device_index=self.device_index,
                       frames_per_buffer=1024)
        
        while self.running:
            data = np.frombuffer(stream.read(1024), dtype=np.int16)
            amplitude = np.abs(data).mean()
            db = 20 * np.log10(amplitude / 32768 + 1e-10) + 96  # Convert to dB
            
            self.audio_history.append(db)
            
            # Detect events
            if db > self.threshold:
                self.last_sound_time = time.time()
                self.silence_alerted = False
                
                event = AudioEvent(
                    event_type='loud_noise',
                    amplitude=db,
                    frequency_peak=self._get_dominant_freq(data),
                    timestamp=time.time()
                )
                self.event_queue.put(event)
            
            # Silence detection
            elif time.time() - self.last_sound_time > self.silence_timeout:
                if not self.silence_alerted:
                    self.event_queue.put(AudioEvent(
                        event_type='silence',
                        amplitude=db,
                        frequency_peak=0,
                        timestamp=time.time()
                    ))
                    self.silence_alerted = True
        
        stream.stop_stream()
        stream.close()
        p.terminate()
    
    def _get_dominant_freq(self, data):
        fft = np.fft.fft(data)
        freqs = np.fft.fftfreq(len(data), 1/self.sample_rate)
        return abs(freqs[np.argmax(np.abs(fft))])
    
    def get_next_event(self, timeout=1.0):
        try:
            return self.event_queue.get(timeout=timeout)
        except queue.Empty:
            return None


# ============================================================================
# TEST USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AUDIO AWARENESS TEST")
    print("=" * 60)
    
    # List available devices
    AudioAwareness.list_devices()
    
    print("\nEnter device index to use (or press Enter for default):")
    device_input = input().strip()
    device_index = int(device_input) if device_input else None
    
    audio = AudioAwareness(threshold_db=60.0, silence_timeout=30, device_index=device_index)  # 30 sec for testing
    audio.start()
    
    if not audio.running:
        print("\nAudio awareness failed to start. Check device index.")
    else:
        print("Monitoring audio for 60 seconds...")
        print("Make loud noises or stay silent to test detection.")
        print("Press Ctrl+C to stop.\n")
        
        start_time = time.time()
        
        try:
            while time.time() - start_time < 60:
                event = audio.get_next_event(timeout=1.0)
                if event:
                    print(f"[{event.event_type.upper()}] Amplitude: {event.amplitude:.1f}dB, Freq: {event.frequency_peak:.1f}Hz")
        except KeyboardInterrupt:
            pass
        finally:
            audio.stop()
            print("\nAudio awareness stopped.")
