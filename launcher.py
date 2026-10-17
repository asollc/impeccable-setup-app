#!/usr/bin/env python3
"""
Bimyah Live Launcher - One-click dev server + live mode.
Auto-updates via the impeccable-setup-app repo.
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path


def check_node():
    try:
        if os.name == "nt":
            result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5, shell=True)
        else:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False


def check_npm():
    try:
        # On Windows, npm is npm.cmd and needs shell=True
        if os.name == "nt":
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True, timeout=5, shell=True)
        else:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False


def get_dev_command(project_root):
    """Get the dev command from package.json."""
    pkg_path = project_root / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text())
            scripts = pkg.get("scripts", {})
            if "dev" in scripts:
                return ["npm", "run", "dev"]
        except:
            pass
    return ["npm", "run", "dev"]


def main():
    if len(sys.argv) < 2:
        print("Usage: python launcher.py /path/to/project [--target src/routes/index.tsx]")
        sys.exit(1)
    
    project_root = Path(sys.argv[1]).resolve()
    target = None
    for i, arg in enumerate(sys.argv):
        if arg == "--target" and i + 1 < len(sys.argv):
            target = sys.argv[i + 1]
    
    if not project_root.exists():
        print(f"Error: {project_root} does not exist")
        sys.exit(1)
    
    print(f"Project: {project_root}")
    print("=" * 50)
    
    # Check Node and npm
    if not check_node():
        print("ERROR: Node.js not found. Install from https://nodejs.org")
        sys.exit(1)
    if not check_npm():
        print("ERROR: npm not found.")
        sys.exit(1)
    
    # npm install if needed
    node_modules = project_root / "node_modules"
    if not node_modules.exists():
        print("\nInstalling dependencies (first run, this takes a few minutes)...")
        result = subprocess.run(["npm", "install"], cwd=project_root)
        if result.returncode != 0:
            print("ERROR: npm install failed")
            sys.exit(1)
        print("Dependencies installed.")
    else:
        print("\nDependencies already installed, skipping npm install.")
    
    # Find impeccable scripts
    script_dir = Path(__file__).parent
    impeccable_cmd = script_dir / "scripts" / "impeccable.cmd"
    impeccable_sh = script_dir / "scripts" / "impeccable"
    
    if os.name == "nt" and impeccable_cmd.exists():
        impeccable = str(impeccable_cmd)
    elif impeccable_sh.exists():
        impeccable = str(impeccable_sh)
    else:
        print("ERROR: impeccable scripts not found")
        sys.exit(1)
    
    # Start dev server
    print("\nStarting dev server...")
    dev_cmd = get_dev_command(project_root)
    
    if os.name == "nt":
        # Windows: start in new terminal
        dev_process = subprocess.Popen(
            ["start", "cmd", "/k"] + dev_cmd,
            cwd=project_root,
            shell=True
        )
    else:
        dev_process = subprocess.Popen(dev_cmd, cwd=project_root)
    
    print("Dev server starting in new terminal...")
    print("Waiting 10 seconds for it to come up...")
    time.sleep(10)
    
    # Start live mode
    print("\nStarting live mode...")
    live_cmd = [impeccable, "live"]
    if target:
        live_cmd.extend(["--target", target])
    
    if os.name == "nt":
        subprocess.Popen(
            ["start", "cmd", "/k"] + live_cmd,
            cwd=project_root,
            shell=True
        )
    else:
        subprocess.Popen(live_cmd, cwd=project_root)
    
    print("\n" + "=" * 50)
    print("Both running!")
    print("- Dev server: check the terminal for the URL (usually http://localhost:5173)")
    print("- Live mode: check the other terminal")
    print("- Open the dev server URL in your browser and click elements to edit")
    print("=" * 50)


if __name__ == "__main__":
    main()
