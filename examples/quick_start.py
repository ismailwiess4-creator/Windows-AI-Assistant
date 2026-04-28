"""
Quick Start Example for Windows AI Assistant
Demonstrates basic usage of desktop and audio awareness
"""
import sys
sys.path.insert(0, '..')
from src.windows_ai import DesktopAwareness, AudioAwareness, brake
import time

def main():
    print("=" * 60)
    print("Windows AI Assistant - Quick Start Demo")
    print("=" * 60)
    
    # Start emergency brake
    brake.start()
    print("\n✅ Emergency brake active (Ctrl+Alt+Shift+E to freeze)")
    
    # Initialize desktop awareness
    desktop = DesktopAwareness(config={
        "capture_fps": 10,
        "motion_threshold": 0.03,
        "window_check_interval": 2,
        "llm_cooldown": 5
    })
    desktop.start()
    print("✅ Desktop awareness: 10 FPS, 1080p processing")
    
    # Initialize audio awareness
    audio = AudioAwareness(
        threshold_db=60.0,
        silence_timeout=300,
        sample_rate=16000
    )
    audio.start()
    print("✅ Audio awareness: listening on default device")
    
    print("\n" + "-" * 60)
    print("Monitoring for 30 seconds...")
    print("Try moving your mouse, changing windows, or making noise")
    print("Press Ctrl+C to stop early")
    print("-" * 60 + "\n")
    
    start_time = time.time()
    
    try:
        while time.time() - start_time < 30:
            if brake.engaged:
                print("\r[FROZEN] Automation paused. Double-tap Ctrl+Alt+Shift+E to resume.", end="")
                time.sleep(1)
                continue
            
            # Check desktop events
            desktop_event = desktop.get_next_event(timeout=0.5)
            if desktop_event:
                print(f"[Desktop] {desktop_event.event_type} detected (confidence: {desktop_event.confidence:.2f})")
            
            # Check audio events
            audio_event = audio.get_next_event(timeout=0.5)
            if audio_event:
                print(f"[Audio] {audio_event.event_type} detected (amplitude: {audio_event.amplitude:.1f}dB)")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    
    finally:
        print("\n" + "=" * 60)
        print("Shutting down...")
        desktop.stop()
        audio.stop()
        print("✅ All systems stopped")
        print("=" * 60)

if __name__ == "__main__":
    main()
