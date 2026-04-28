"""
EMERGENCY BRAKE - Double-tap Ctrl+Alt+Shift+E to freeze all automation
Place in: D:\AI Assistant\emergency_stop.py
"""

import keyboard
import threading
import time

class EmergencyBrake:
    def __init__(self):
        self.engaged = False
        self.last_tap = 0
        self.thread = None
        
    def start(self):
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()
        print("[BRAKE] Emergency stop active. Ctrl+Alt+Shift+E twice to freeze.")
        
    def _listen(self):
        # Hotkey combo that's impossible to hit accidentally
        keyboard.add_hotkey('ctrl+alt+shift+e', self._on_combo)
        keyboard.wait()
        
    def _on_combo(self):
        now = time.time()
        if now - self.last_tap < 1.0:  # Double-tap within 1 second
            self.engaged = not self.engaged
            status = "ENGAGED (Automation FROZEN)" if self.engaged else "RELEASED"
            print(f"\n[BRAKE] Emergency Stop {status}")
            if self.engaged:
                # Kill any active automation
                import pyautogui
                pyautogui.FAILSAFE = True
        self.last_tap = now

# Singleton
brake = EmergencyBrake()
