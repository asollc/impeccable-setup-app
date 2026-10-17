#!/usr/bin/env python3
"""
Download a project zip from a URL, extract it, and run setup.
Usage: python download.py <url> [project-name]
"""

import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from setup import main as setup_main


def download_project(url, project_name=None):
    print(f"Downloading from: {url}")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "project.zip"
        
        # Download with progress
        def progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                pct = min(100, downloaded * 100 // total_size)
                print(f"\r  {pct}% ({downloaded//1024//1024}MB)", end="", flush=True)
        
        urllib.request.urlretrieve(url, zip_path, reporthook=progress)
        print("\nExtracting...")
        
        # Extract to Desktop or specified location
        if project_name:
            dest = Path.home() / "Desktop" / project_name
        else:
            dest = Path.home() / "Desktop" / "downloaded-project"
        
        dest.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(dest)
        
        # Handle single top-level directory
        subdirs = [d for d in dest.iterdir() if d.is_dir()]
        if len(subdirs) == 1 and len(list(dest.iterdir())) == 1:
            # Move contents up one level
            inner = subdirs[0]
            tmp_move = dest.parent / (dest.name + "_tmp")
            inner.rename(tmp_move)
            dest.rmdir()
            tmp_move.rename(dest)
        
        print(f"Extracted to: {dest}")
        return dest


def main():
    if len(sys.argv) < 2:
        print("Usage: python download.py <url> [project-name]")
        print("Example: python download.py https://example.com/bimyah.zip bimyah")
        sys.exit(1)
    
    url = sys.argv[1]
    project_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    dest = download_project(url, project_name)
    
    print("\nRunning setup...")
    print("=" * 50)
    sys.argv = ["setup.py", str(dest)]
    setup_main()


if __name__ == "__main__":
    main()
