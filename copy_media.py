#!/usr/bin/env python3
"""
Copy media files to the production media directory
"""
import os
import shutil
import sys
from pathlib import Path

def copy_media_files():
    """Copy media files from local to production directory"""
    source_dir = Path('media/products')
    dest_dir = Path('/opt/render/project/src/media/products')
    
    # Create destination directory
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    if source_dir.exists() and any(source_dir.iterdir()):
        print(f"Copying media files from {source_dir} to {dest_dir}")
        
        # Copy each file individually to handle any issues
        copied_count = 0
        for file_path in source_dir.glob('*'):
            if file_path.is_file():
                try:
                    dest_file = dest_dir / file_path.name
                    shutil.copy2(file_path, dest_file)
                    copied_count += 1
                    print(f"  Copied: {file_path.name}")
                except Exception as e:
                    print(f"  Error copying {file_path.name}: {e}")
        
        print(f"Successfully copied {copied_count} media files")
        return True
    else:
        print("No media files found to copy")
        # Create a placeholder file
        placeholder = dest_dir / '.gitkeep'
        placeholder.touch()
        return False

if __name__ == '__main__':
    success = copy_media_files()
    sys.exit(0 if success else 1)
