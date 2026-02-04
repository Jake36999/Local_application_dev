import subprocess
from pathlib import Path

def check_system_binaries():
    result = {}
    for binary in ["git", "tesseract"]:
        try:
            subprocess.run([binary, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            result[binary] = True
        except Exception:
            result[binary] = False
    return result

def consolidate_pip(acp_root: Path):
    reqs = set()
    for req_file in acp_root.rglob("requirements.txt"):
        with open(req_file, "r") as f:
            for line in f:
                l = line.strip()
                if l and not l.startswith("#"):
                    reqs.add(l)
    master_path = acp_root / "requirements_master.txt"
    with open(master_path, "w") as f:
        for l in sorted(reqs):
            f.write(l + "\n")
    return str(master_path)
