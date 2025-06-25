from config_parser import parse_config
from executor import execute_workflow

if __name__ == "__main__":
    config = parse_config("/config/energy-pipeline.json")
    execute_workflow(config["containers"])
