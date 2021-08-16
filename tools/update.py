import subprocess


def update():
    update_status = subprocess.run(['bash', 'update.sh'], capture_output=True)
    if update_status.returncode == 0:
        return True
    return False
