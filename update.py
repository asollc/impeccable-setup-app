#!/usr/bin/env python3
"""
Auto-updater for Impeccable Setup App.
Checks GitHub for a new version and updates if available.
"""

import json
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path


REPO = "asollc/impeccable-setup-app"
VERSION_FILE = Path(__file__).parent / "VERSION"


def get_local_version():
    try:
        return VERSION_FILE.read_text().strip()
    except:
        return "0.0.0"


def get_remote_version():
    """Get the latest version from GitHub."""
    url = f"https://api.github.com/repos/{REPO}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "impeccable-setup-app"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            tag = data.get("tag_name", "v0.0.0")
            return tag.lstrip("v"), data
    except Exception as e:
        print(f"Update check failed: {e}")
        return None, None


def version_tuple(v):
    return tuple(int(x) for x in v.split(".") if x.isdigit())


def check_and_update():
    local = get_local_version()
    print(f"Current version: {local}")
    
    remote, release_data = get_remote_version()
    if not remote:
        print("Could not check for updates. Continuing...")
        return False
    
    print(f"Latest version: {remote}")
    
    if version_tuple(remote) <= version_tuple(local):
        print("Already up to date.")
        return False
    
    print(f"\nUpdate available: {local} -> {remote}")
    print("Downloading...")
    
    # Download the release archive (works for public repos without auth)
    zip_url = f"https://github.com/{REPO}/archive/refs/tags/v{remote}.zip"
    
    # Download to temp
    app_dir = Path(__file__).parent
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "update.zip"
        urllib.request.urlretrieve(zip_url, zip_path)
        
        print("Installing update...")
        # Extract over the current directory
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(tmpdir + "/extracted")
        
        # Copy new files over (preserve the update script itself during copy)
        extracted = Path(tmpdir) / "extracted"
        # GitHub archive has a top-level dir like impeccable-setup-app-1.0.0/
        subdirs = [d for d in extracted.iterdir() if d.is_dir()]
        if len(subdirs) == 1:
            extracted = subdirs[0]
        
        for item in extracted.rglob("*"):
            if item.is_file():
                rel = item.relative_to(extracted)
                dest = app_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
        
        # Update version file
        VERSION_FILE.write_text(remote)
    
    print(f"Updated to version {remote}!")
    return True


if __name__ == "__main__":
    check_and_update()
