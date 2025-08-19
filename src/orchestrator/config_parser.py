# src/orchestrator/config_parser.py
import json
import os
import sys
from typing import Dict, Any

def parse_config(path: str) -> Dict[str, Any]:
    """
    Load and validate the pipeline config JSON.
    - Accepts UTF-8 with or without BOM (Windows/Notepad friendly).
    - Prints absolute path in error messages.
    - Ensures a non-empty 'containers' list.
    """
    abs_path = os.path.abspath(path)

    if not os.path.exists(abs_path):
        print(f"Config file not found: {abs_path}")
        sys.exit(1)

    try:
        # 'utf-8-sig' skips a BOM if present
        with open(abs_path, "r", encoding="utf-8-sig") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in {abs_path}: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"Could not read config {abs_path}: {e}")
        sys.exit(1)

    containers = config.get("containers")
    if not isinstance(containers, list) or len(containers) == 0:
        print(f"Invalid config in {abs_path}: 'containers' list missing or empty.")
        sys.exit(1)

    return config
