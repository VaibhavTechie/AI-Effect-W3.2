import argparse
import os
from pathlib import Path

from config_parser import load_workflow
from executor import Orchestrator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple container orchestrator")
    parser.add_argument('--workflow', required=True, help='Path to workflow JSON')
    parser.add_argument('--log-dir', default=os.environ.get('LOG_DIR', './logs'), help='Directory for logs')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workflow = load_workflow(args.workflow)
    orchestrator = Orchestrator(workflow, Path(args.log_dir))
    orchestrator.run()


if __name__ == '__main__':
    main()
