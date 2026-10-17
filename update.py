#!/usr/bin/env python3
"""
Auto-updater for Impeccable Setup App.
Checks GitHub for a new version and updates if available.
Safe for Windows: stages update and applies via separate batch.
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
    
    # On Windows, we can't overwrite running files, so stage the update
    # and create a batch file to apply it
    if os.name == "nt":
        print("Downloading update...")
        zip_url = f"https://github.com/{REPO}/archive/refs/tags/v{remote}.zip"
        
        app_dir = Path(__file__).parent
        
        # Aggressively clean up ALL staging dirs (including nested ones)
        # Do this before defining stage_dir to catch everything
        for _ in range(3):  # Multiple passes for nested structures
            found = list(app_dir.rglob(".update_staged"))
            if not found:
                break
            for p in found:
                # Remove deepest first to avoid issues
                try:
                    shutil.rmtree(p, ignore_errors=False)
                except:
                    pass
        
        stage_dir = app_dir / ".update_staged"
        # Final check
        if stage_dir.exists():
            shutil.rmtree(stage_dir, ignore_errors=True)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "update.zip"
            try:
                urllib.request.urlretrieve(zip_url, zip_path)
            except Exception as e:
                print(f"Download failed: {e}")
                return False
            
            print("Staging update...")
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(tmpdir + "/extracted")
            
            extracted = Path(tmpdir) / "extracted"
            subdirs = [d for d in extracted.iterdir() if d.is_dir()]
            if len(subdirs) == 1:
                extracted = subdirs[0]
            
            # Copy to staging
            if stage_dir.exists():
                shutil.rmtree(stage_dir)
            shutil.copytree(extracted, stage_dir)
            
            # Create apply script
            apply_bat = app_dir / "apply_update.bat"
            apply_content = f"""@echo off
echo Applying update to {remote}...
xcopy /E /Y "{stage_dir}" "{app_dir}\\" >nul
rmdir /S /Q "{stage_dir}"
del "%~f0"
echo Update complete! Version {remote} installed.
pause
"""
            apply_bat.write_text(apply_content)
        
        print(f"\nUpdate downloaded. Run apply_update.bat to install version {remote}.")
        print("The current operation will continue with the old version.")
        return False  # Don't block current operation
    else:
        # Unix: can overwrite in place
        print("Downloading...")
        zip_url = f"https://github.com/{REPO}/archive/refs/tags/v{remote}.zip"
        app_dir = Path(__file__).parent
        
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "update.zip"
            urllib.request.urlretrieve(zip_url, zip_path)
            
            print("Installing update...")
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(tmpdir + "/extracted")
            
            extracted = Path(tmpdir) / "extracted"
            subdirs = [d for d in extracted.iterdir() if d.is_dir()]
            if len(subdirs) == 1:
                extracted = subdirs[0]
            
            for item in extracted.rglob("*"):
                if item.is_file():
                    rel = item.relative_to(extracted)
                    dest = app_dir / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest)
            
            VERSION_FILE.write_text(remote)
        
        print(f"Updated to version {remote}!")
        return True


if __name__ == "__main__":
    check_and_update()
