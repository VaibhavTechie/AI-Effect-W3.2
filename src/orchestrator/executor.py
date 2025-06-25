import subprocess
from pathlib import Path
from typing import Set

from .config_parser import WorkflowConfig, ContainerConfig


class Orchestrator:
    """Very simple orchestrator to run containers sequentially."""

    def __init__(self, workflow: WorkflowConfig, log_dir: Path):
        self.workflow = workflow
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _run_container(self, container: ContainerConfig) -> None:
        log_file = self.log_dir / f"{container.id}.log"
        print(f"Running {container.name} (id={container.id})")
        with log_file.open('w', encoding='utf-8') as lf:
            process = subprocess.run(container.command.split(), stdout=lf, stderr=lf)
        if process.returncode != 0:
            raise RuntimeError(f"Container {container.id} failed")

    def run(self) -> None:
        executed: Set[str] = set()
        for container in self.workflow.containers:
            if any(dep not in executed for dep in container.depends_on):
                missing = [d for d in container.depends_on if d not in executed]
                raise RuntimeError(f"Dependencies not met for {container.id}: {missing}")
            self._run_container(container)
            executed.add(container.id)
        print("Workflow completed")
