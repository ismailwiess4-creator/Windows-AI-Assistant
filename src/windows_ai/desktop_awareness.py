"""
Desktop Awareness Middleware for Windows LSTC
Bridges live screen capture to Ollama with intelligent change detection
"""

import cv2
import numpy as np
import mss
import time
import json
import requests
from PIL import Image
from collections import deque
from dataclasses import dataclass
from typing import Optional, Tuple, List
import threading
import queue
import pygetwindow as gw
import base64
from io import BytesIO

@dataclass
class DesktopEvent:
    """Significant change detected on screen"""
    event_type: str  # 'motion', 'window_change', 'ui_popup', 'user_idle'
    region: Tuple[int, int, int, int]  # x, y, w, h
    confidence: float
    screenshot_base64: str
    timestamp: float

class DesktopAwareness:
    def __init__(self, 
                 capture_fps: int = 10,  # Process 10 frames/sec (balance CPU/awareness)
                 motion_threshold: float = 0.02,  # 2% of pixels changed = motion
                 window_check_interval: float = 0.5,  # Check window changes twice/sec
                 llm_cooldown: float = 2.0,  # Don't spam LLM more than once per 2 sec
                 ollama_model: str = "gemma3:4b"):
        
        self.capture_fps = capture_fps
        self.motion_threshold = motion_threshold
        self.window_check_interval = window_check_interval
        self.llm_cooldown = llm_cooldown
        self.ollama_model = ollama_model
        
        # Screen capture setup
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]  # Primary monitor
        
        # State tracking
        self.prev_frame = None
        self.prev_window_title = None
        self.last_llm_call = 0
        self.event_queue = queue.Queue()
        
        # Motion history for pattern detection
        self.motion_history = deque(maxlen=30)
        
        # Event correlation window for pattern matching
        self.event_window = deque(maxlen=10)
        
        # Define dead zones (taskbar, static widgets)
        self.ignore_regions = [
            (0, self.monitor['height'] - 80, self.monitor['width'], 80),  # Taskbar
            (self.monitor['width'] - 400, 0, 400, 30)  # Top-right window controls
        ]
        
        # Background thread control
        self.running = False
        self.thread = None
        
        print(f"[DesktopAwareness] Initialized - {self.monitor['width']}x{self.monitor['height']}")
        
    def start(self):
        """Start background monitoring thread"""
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("[DesktopAwareness] Monitoring started")
        
    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        print("[DesktopAwareness] Monitoring stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop - runs in background thread"""
        # Initialize mss handles in this thread (mss stores handles in thread-local storage)
        self.sct = mss.mss()
        
        frame_interval = 1.0 / self.capture_fps
        last_window_check = 0
        
        while self.running:
            loop_start = time.time()
            
            # Capture current frame
            frame = self._capture_frame()
            
            # Detect motion
            motion_event = self._detect_motion(frame)
            if motion_event:
                self.event_queue.put(motion_event)
                self.motion_history.append(1)
                pattern = self._correlate_events(motion_event)
                if pattern:
                    print(f"[Pattern] {pattern}")
            else:
                self.motion_history.append(0)
            
            # Check for window changes (less frequent)
            if time.time() - last_window_check > self.window_check_interval:
                window_event = self._detect_window_change()
                if window_event:
                    self.event_queue.put(window_event)
                    pattern = self._correlate_events(window_event)
                    if pattern:
                        print(f"[Pattern] {pattern}")
                last_window_check = time.time()
            
            # Detect UI popups/notifications (pattern recognition)
            popup_event = self._detect_popup(frame)
            if popup_event:
                self.event_queue.put(popup_event)
                pattern = self._correlate_events(popup_event)
                if pattern:
                    print(f"[Pattern] {pattern}")
            
            # Update previous frame
            self.prev_frame = frame
            
            # Maintain target FPS
            elapsed = time.time() - loop_start
            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)
                
    def _capture_frame(self) -> np.ndarray:
        """Capture screen as numpy array (BGR format for OpenCV)"""
        screenshot = self.sct.grab(self.monitor)
        frame = np.array(screenshot)[:, :, :3]  # Drop alpha channel
        
        # FOR 4K: Downscale to 1080p BEFORE any processing
        # This cuts memory by 75% with zero perceptual loss for detection
        if frame.shape[1] > 1920:
            scale = 1920 / frame.shape[1]
            new_width = 1920
            new_height = int(frame.shape[0] * scale)
            frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return frame
    
    def _is_in_ignore_region(self, x: int, y: int) -> bool:
        """Check if coordinates fall in any ignore zone"""
        for ix, iy, iw, ih in self.ignore_regions:
            if ix <= x <= ix + iw and iy <= y <= iy + ih:
                return True
        return False
    
    def _correlate_events(self, current_event: DesktopEvent) -> Optional[str]:
        """Detect compound patterns like 'user opened start menu'"""
        self.event_window.append(current_event)
        
        # Pattern 1: Window change immediately after motion in bottom-left
        # = Start menu opened
        if len(self.event_window) >= 2:
            prev = self.event_window[-2]
            if (prev.event_type == 'motion' and 
                prev.region[0] < 200 and prev.region[1] > self.monitor['height'] - 200 and
                current_event.event_type == 'window_change'):
                return "start_menu_opened"
        
        # Pattern 2: Sustained motion then UI popup
        # = User triggered a dialog
        if current_event.event_type == 'ui_popup':
            recent_motion = sum(1 for e in self.event_window if e.event_type == 'motion')
            if recent_motion >= 3:
                return "user_triggered_dialog"
        
        return None
    
    def _detect_motion(self, current_frame: np.ndarray) -> Optional[DesktopEvent]:
        """Detect significant motion between frames"""
        if self.prev_frame is None:
            return None
            
        # Downscale for performance (4x reduction)
        h, w = current_frame.shape[:2]
        small_h, small_w = h // 4, w // 4
        
        prev_small = cv2.resize(self.prev_frame, (small_w, small_h))
        curr_small = cv2.resize(current_frame, (small_w, small_h))
        
        # Compute absolute difference
        diff = cv2.absdiff(prev_small, curr_small)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Threshold to find significant changes
        _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
        
        # Calculate percentage of changed pixels
        changed_pixels = np.sum(thresh > 0)
        total_pixels = small_h * small_w
        change_ratio = changed_pixels / total_pixels
        
        if change_ratio > self.motion_threshold:
            # Find the region with most motion
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Get bounding box of largest motion area
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w_box, h_box = cv2.boundingRect(largest_contour)
                
                # Scale back to original coordinates
                x = x * 4
                y = y * 4
                w_box = w_box * 4
                h_box = h_box * 4
                
                # Ignore taskbar junk
                if self._is_in_ignore_region(x + w_box//2, y + h_box//2):
                    return None
                
                return DesktopEvent(
                    event_type='motion',
                    region=(x, y, w_box, h_box),
                    confidence=change_ratio,
                    screenshot_base64=self._frame_to_base64(current_frame),
                    timestamp=time.time()
                )
        
        return None
    
    def _detect_window_change(self) -> Optional[DesktopEvent]:
        """Detect if active window has changed"""
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                current_title = active_window.title
                
                if self.prev_window_title != current_title:
                    self.prev_window_title = current_title
                    
                    # Capture frame for context
                    frame = self._capture_frame()
                    
                    return DesktopEvent(
                        event_type='window_change',
                        region=(0, 0, self.monitor['width'], self.monitor['height']),
                        confidence=1.0,
                        screenshot_base64=self._frame_to_base64(frame),
                        timestamp=time.time()
                    )
        except Exception as e:
            print(f"[DesktopAwareness] Window check error: {e}")
            
        return None
    
    def _detect_popup(self, frame: np.ndarray) -> Optional[DesktopEvent]:
        """Detect sudden appearance of dialog boxes/popups"""
        if self.prev_frame is None:
            return None
            
        # Simple heuristic: Sudden bright rectangle near screen center
        # (Most dialogs appear in center with distinct borders)
        h, w = frame.shape[:2]
        center_region = frame[h//4:3*h//4, w//4:3*w//4]
        prev_center = self.prev_frame[h//4:3*h//4, w//4:3*w//4]
        
        # Check for new high-contrast rectangle
        diff = cv2.absdiff(prev_center, center_region)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Look for rectangular contours
        edges = cv2.Canny(gray_diff, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 5000:  # Significant new UI element
                x, y, w_box, h_box = cv2.boundingRect(contour)
                
                # Check if roughly rectangular (dialog box shape)
                aspect_ratio = w_box / h_box if h_box > 0 else 0
                if 0.5 < aspect_ratio < 2.0:
                    return DesktopEvent(
                        event_type='ui_popup',
                        region=(x + w//4, y + h//4, w_box, h_box),
                        confidence=0.8,
                        screenshot_base64=self._frame_to_base64(frame),
                        timestamp=time.time()
                    )
        
        return None
    
    def _frame_to_base64(self, frame: np.ndarray) -> str:
        """Convert numpy frame to base64 string for Ollama"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_frame)
        
        # Save to bytes buffer
        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")
        
        # Encode to base64
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    def should_query_llm(self, event: DesktopEvent) -> bool:
        """Determine if this event warrants LLM attention"""
        # Cooldown check
        if time.time() - self.last_llm_call < self.llm_cooldown:
            return False
        
        # Motion patterns: Check if sustained activity or single burst
        if event.event_type == 'motion':
            recent_motion = sum(self.motion_history) / len(self.motion_history) if self.motion_history else 0
            # Query LLM if sustained motion (>30% of recent frames have motion)
            if recent_motion < 0.3:
                return False
        
        # Window changes almost always worth checking
        if event.event_type == 'window_change':
            return True
        
        # UI popups definitely worth checking
        if event.event_type == 'ui_popup':
            return True
        
        return False
    
    def query_llm_about_event(self, event: DesktopEvent) -> dict:
        """Send event screenshot to Ollama for analysis"""
        self.last_llm_call = time.time()
        
        prompt = self._build_prompt_for_event(event)
        
        try:
            response = requests.post(
                'http://localhost:11434/api/chat',
                json={
                    'model': self.ollama_model,
                    'messages': [{
                        'role': 'user',
                        'content': prompt,
                        'images': [event.screenshot_base64]
                    }],
                    'stream': False,
                    'options': {
                        'temperature': 0.1,  # Low temp for accurate analysis
                    }
                },
                timeout=30  # Increased timeout
            )
            
            if response.status_code == 200:
                content = response.json()['message']['content'].strip()
                # Try to parse JSON from response
                try:
                    return json.loads(content)
                except:
                    return {"analysis": content, "action_needed": False}
            else:
                return {"error": f"Ollama error: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _build_prompt_for_event(self, event: DesktopEvent) -> str:
        """Build context-aware prompt based on event type"""
        base_prompt = "You are analyzing a user's desktop screen. "
        
        if event.event_type == 'motion':
            base_prompt += f"The user is actively moving something in region {event.region}. "
            base_prompt += "Is this a meaningful UI interaction or just casual movement? "
        
        elif event.event_type == 'window_change':
            base_prompt += f"The active window just changed. "
            base_prompt += "What application appears to be open? What might the user want to do next? "
        
        elif event.event_type == 'ui_popup':
            base_prompt += f"A dialog or popup just appeared in region {event.region}. "
            base_prompt += "What does this popup say? Is it an error, confirmation, or notification? "
        
        base_prompt += """
        Respond in JSON format:
        {
            "action_needed": true/false,
            "analysis": "brief description",
            "suggested_tool": "winscript tool name or null",
            "suggested_params": {}
        }
        Only include JSON, no other text.
        """
        
        return base_prompt
    
    def get_next_event(self, timeout: float = 1.0) -> Optional[DesktopEvent]:
        """Get next significant event from queue (non-blocking)"""
        try:
            return self.event_queue.get(timeout=timeout)
        except queue.Empty:
            return None

# ============================================================================
# INTEGRATION WITH EXISTING QWE-QWE ASSISTANT
# ============================================================================

class AssistantWithAwareness:
    """Wrapper that adds desktop awareness to existing qwe-qwe assistant"""
    
    def __init__(self, mcp_client, ollama_model="gemma3:4b"):
        self.mcp_client = mcp_client
        self.awareness = DesktopAwareness(ollama_model=ollama_model)
        self.running = False
        
    def start(self):
        """Start awareness monitoring"""
        self.awareness.start()
        self.running = True
        print("[Assistant] Desktop awareness active - monitoring screen changes")
        
    def stop(self):
        """Stop monitoring"""
        self.awareness.stop()
        self.running = False
        
    def process_events_loop(self):
        """Main loop - process desktop events and take action"""
        print("[Assistant] Entering event processing loop. Press Ctrl+C to stop.")
        
        try:
            while self.running:
                event = self.awareness.get_next_event(timeout=0.5)
                
                if event and self.awareness.should_query_llm(event):
                    print(f"\n[Event] {event.event_type} detected (confidence: {event.confidence:.2f})")
                    
                    # Ask LLM what this event means
                    llm_response = self.awareness.query_llm_about_event(event)
                    
                    if "error" not in llm_response:
                        print(f"[Analysis] {llm_response.get('analysis', 'No analysis')}")
                        
                        # Take action if LLM suggests
                        if llm_response.get('action_needed'):
                            tool = llm_response.get('suggested_tool')
                            params = llm_response.get('suggested_params', {})
                            
                            if tool:
                                print(f"[Action] Calling {tool} with {params}")
                                # Call WinScript MCP tool
                                result = self.mcp_client.call_tool('winscript', tool, params)
                                print(f"[Result] {result}")
                    else:
                        print(f"[Error] LLM query failed: {llm_response['error']}")
                
                time.sleep(0.1)  # Small sleep to prevent CPU spin
                
        except KeyboardInterrupt:
            print("\n[Assistant] Stopping event loop...")
            self.stop()

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("DESKTOP AWARENESS MIDDLEWARE TEST")
    print("=" * 60)
    
    # Test the awareness system standalone
    awareness = DesktopAwareness(capture_fps=5)
    awareness.start()
    
    print("\nMonitoring desktop for 30 seconds...")
    print("Move windows, click around, open popups to test detection.")
    print("Press Ctrl+C to stop.\n")
    
    start_time = time.time()
    event_count = 0
    
    try:
        while time.time() - start_time < 30:
            event = awareness.get_next_event(timeout=0.5)
            
            if event:
                event_count += 1
                print(f"[{event_count}] {event.event_type.upper()} - Region: {event.region}")
                
                # Optional: Test LLM query (comment out if Ollama not ready)
                # if awareness.should_query_llm(event):
                #     response = awareness.query_llm_about_event(event)
                #     print(f"  → LLM: {response.get('analysis', 'No analysis')}")
            
    except KeyboardInterrupt:
        pass
    finally:
        awareness.stop()
        print(f"\nDetected {event_count} significant events in 30 seconds.")
