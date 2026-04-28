"""
Configuration loader with validation for Windows AI Assistant
"""
import yaml
from pathlib import Path
from typing import Dict, Any
from .logger import setup_logger

logger = setup_logger("config")

DEFAULT_CONFIG = {
    "desktop_awareness": {
        "capture_fps": 10,
        "motion_threshold": 0.03,
        "window_check_interval": 2,
        "llm_cooldown": 5,
    },
    "audio_awareness": {
        "threshold_db": 60.0,
        "silence_timeout": 300,
        "sample_rate": 16000,
        "device_index": None,
    },
    "ollama": {
        "model": "gemma3:4b",
        "timeout": 30,
        "temperature": 0.1,
        "endpoint": "http://localhost:11434/api/chat",
    },
    "fast_path": {
        "deterministic_actions": ["start_menu", "alt_tab", "taskbar_click"],
        "response_time_ms": 100,
    },
}

def load_config(config_path: str = "src/windows_ai/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file with validation."""
    config = DEFAULT_CONFIG.copy()
    
    config_file = Path(config_path)
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    _merge_config(config, user_config)
                    logger.info(f"Loaded config from {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load config file: {e}, using defaults")
    else:
        logger.info(f"Config file not found at {config_path}, using defaults")
    
    _validate_config(config)
    return config

def _merge_config(base: Dict[str, Any], override: Dict[str, Any]) -> None:
    """Recursively merge override config into base config."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge_config(base[key], value)
        else:
            base[key] = value

def _validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration values."""
    # Validate desktop_awareness
    da = config.get("desktop_awareness", {})
    if da.get("capture_fps", 0) <= 0:
        logger.warning("capture_fps must be > 0, using default 10")
        da["capture_fps"] = 10
    if da.get("motion_threshold", 0) <= 0 or da.get("motion_threshold", 0) > 1:
        logger.warning("motion_threshold must be between 0 and 1, using default 0.03")
        da["motion_threshold"] = 0.03
    
    # Validate audio_awareness
    aa = config.get("audio_awareness", {})
    if aa.get("threshold_db", 0) < 0:
        logger.warning("threshold_db must be >= 0, using default 60")
        aa["threshold_db"] = 60.0
    if aa.get("silence_timeout", 0) <= 0:
        logger.warning("silence_timeout must be > 0, using default 300")
        aa["silence_timeout"] = 300
    
    # Validate ollama
    ollama = config.get("ollama", {})
    if not ollama.get("model"):
        logger.warning("ollama model not specified, using default gemma3:4b")
        ollama["model"] = "gemma3:4b"
