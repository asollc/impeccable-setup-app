#!/usr/bin/env python3
"""
Pack and Send - Zip your website changes and prepare them to send to Gigi.

Usage:
  python send.py /path/to/project

What it does:
1. Zips the project (excluding node_modules, .git, build output, etc.)
2. Names it clearly with timestamp
3. Saves to Desktop
4. Tells you exactly what to do next
"""

import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path


# Directories and files to exclude from the zip
EXCLUDE_DIRS = {
    "node_modules", ".git", ".next", "dist", "build", "out",
    ".impeccable", "__pycache__", ".venv", "venv", ".turbo",
    "coverage", ".nyc_output", ".cache", "tmp", "temp"
}

EXCLUDE_FILES = {
    ".DS_Store", "Thumbs.db", ".env", ".env.local", ".env.production",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml"
}

EXCLUDE_EXTENSIONS = {".log", ".tmp", ".cache"}


def should_exclude(path, project_root):
    """Check if a path should be excluded from the zip."""
    rel = path.relative_to(project_root)
    parts = rel.parts
    
    # Check directory exclusions
    for part in parts[:-1] if path.is_file() else parts:
        if part in EXCLUDE_DIRS:
            return True
    
    # Check file exclusions
    if path.is_file():
        if path.name in EXCLUDE_FILES:
            return True
        if path.suffix.lower() in EXCLUDE_EXTENSIONS:
            return True
    
    return False


def get_desktop():
    """Get the Desktop path cross-platform."""
    if os.name == "nt":  # Windows
        return Path(os.path.expanduser("~/Desktop"))
    elif sys.platform == "darwin":  # macOS
        return Path(os.path.expanduser("~/Desktop"))
    else:  # Linux
        return Path(os.path.expanduser("~/Desktop"))


def pack_project(project_path):
    """Zip the project and save to Desktop."""
    project_root = Path(project_path).resolve()
    
    if not project_root.exists():
        print(f"Error: {project_root} does not exist")
        return None
    
    project_name = project_root.name
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    zip_name = f"{project_name}-changes-{timestamp}.zip"
    
    desktop = get_desktop()
    desktop.mkdir(parents=True, exist_ok=True)
    zip_path = desktop / zip_name
    
    print(f"Packing {project_name}...")
    print(f"Excluding: node_modules, .git, build output, etc.")
    print()
    
    file_count = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for item in project_root.rglob("*"):
            if should_exclude(item, project_root):
                continue
            if item.is_file():
                arcname = item.relative_to(project_root)
                z.write(item, arcname)
                file_count += 1
    
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"Packed {file_count} files ({size_mb:.1f} MB)")
    print(f"Saved to: {zip_path}")
    
    return zip_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python send.py /path/to/project")
        sys.exit(1)
    
    project_path = sys.argv[1]
    zip_path = pack_project(project_path)
    
    if zip_path:
        print()
        print("=" * 50)
        print("Ready to send!")
        print()
        print("1. Open your chat with Gigi")
        print(f"2. Drag this file into the chat:")
        print(f"   {zip_path}")
        print("3. Gigi will push the changes live")
        print("=" * 50)


if __name__ == "__main__":
    main()
