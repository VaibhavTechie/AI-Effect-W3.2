import json
from dataclasses import dataclass
from typing import List


@dataclass
class ContainerConfig:
    id: str
    name: str
    command: str
    input_file: str
    output_file: str
    depends_on: List[str]


@dataclass
class WorkflowConfig:
    workflow_name: str
    containers: List[ContainerConfig]


def load_workflow(path: str) -> WorkflowConfig:
    """Load workflow configuration from a JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    containers = [
        ContainerConfig(
            id=c.get('id'),
            name=c.get('name'),
            command=c.get('command'),
            input_file=c.get('input_file'),
            output_file=c.get('output_file'),
            depends_on=c.get('depends_on', []),
        )
        for c in data.get('containers', [])
    ]

    return WorkflowConfig(workflow_name=data.get('workflow_name', ''), containers=containers)
