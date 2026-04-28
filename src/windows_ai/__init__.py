"""
Windows AI Assistant — Local, Private, Aware

A production-grade AI assistant with real-time desktop awareness,
audio monitoring, and MCP integration. 100% offline, no cloud, no telemetry.
"""

__version__ = "1.0.0"
__author__ = "Ismail Wiess"
__license__ = "MIT"

from .desktop_awareness import DesktopAwareness, DesktopEvent
from .audio_awareness import AudioAwareness, AudioEvent
from .emergency_stop import brake

__all__ = [
    "DesktopAwareness",
    "DesktopEvent",
    "AudioAwareness",
    "AudioEvent",
    "brake",
]
