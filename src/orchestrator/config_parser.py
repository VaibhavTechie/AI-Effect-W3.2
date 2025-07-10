import json
import os
import sys

def parse_config(path):
    if not os.path.exists(path):
        print(f"Config file not found: {path}")
        sys.exit(1)

    with open(path) as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
            sys.exit(1)

    if "containers" not in config or not isinstance(config["containers"], list):
        print("Invalid config: 'containers' list missing or malformed.")
        sys.exit(1)

    return config