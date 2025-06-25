import subprocess

def execute_workflow(containers):
    for container in containers:
        cmd = container["command"]
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            print(f"Error: Command failed: {cmd}")
            return False
    print("All containers executed successfully.")
    return True
