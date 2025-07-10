import subprocess
import logging
import os

def execute_workflow(containers):
    for container in containers:
        cmd = container["command"]

        # Add volume mount if missing (so containers can access /data)
        if "/data" not in cmd:
            cwd = os.getcwd()
            volume_flag = f"-v {cwd}/../data:/data"
            cmd = cmd.replace("docker run", f"docker run {volume_flag}")

        logging.info(f"Starting container: {container['id']}")
        logging.info(f"Command: {cmd}")
        print(f"Running: {cmd}")

        try:
            result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
            logging.info(f"{container['id']} STDOUT:\n{result.stdout}")
            if result.stderr:
                logging.warning(f"{container['id']} STDERR:\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            logging.error(f"{container['id']} FAILED with error:\n{e.stderr}")
            print(f"Error: Command failed: {cmd}")
            break

    logging.info("All containers executed.")
    print("All containers executed successfully.")
