#!/usr/bin/env python3

import os
import logging
import fnmatch
from pathlib import Path

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

def get_system_file_patterns():
    """Returns a list of file patterns that should be removed."""
    return [
        # macOS system files
        '._*',           # AppleDouble files (resource forks)
        '.DS_Store',     # Directory Services Store
        '.AppleDouble',  # AppleDouble directory
        '.__MACOSX',     # macOS archive artifacts
        '.fseventsd',    # File system events daemon
        '.Spotlight-V100', # Spotlight index
        '.TemporaryItems', # Temporary items
        '.Trashes',      # Trash folder
        '.VolumeIcon.icns', # Volume icons
        '.com.apple.*',  # Apple system files
        
        # Windows system files
        'Thumbs.db',     # Windows thumbnail cache
        'Desktop.ini',   # Windows desktop configuration
        'ehthumbs.db',   # Windows thumbnail cache
        '$RECYCLE.BIN',  # Windows recycle bin
        'System Volume Information', # Windows system folder
        
        # Other common system/hidden files
        '.dropbox',      # Dropbox sync files
        '.dropbox.attr', # Dropbox attributes
        '@eaDir',        # Synology NAS thumbnails
        '.@__thumb',     # QNAP NAS thumbnails
        '.bzvol',        # BackBlaze volume marker
        
        # Audio software temp files
        '*.tmp',         # Temporary files
        '*.temp',        # Temporary files
        '.apdisk',       # Apple Partition Map
    ]

def should_remove_file(file_path, patterns):
    """Check if a file matches any of the removal patterns."""
    file_name = os.path.basename(file_path)
    
    for pattern in patterns:
        if fnmatch.fnmatch(file_name, pattern):
            return True
    return False

def find_system_files(directory, patterns):
    """Recursively find all system files matching the patterns."""
    system_files = []
    
    for root, dirs, files in os.walk(directory):
        # Check files
        for file in files:
            file_path = os.path.join(root, file)
            if should_remove_file(file_path, patterns):
                system_files.append(file_path)
        
        # Check directories (for removing entire system directories)
        for dir_name in dirs[:]:  # Use slice copy to allow modification during iteration
            dir_path = os.path.join(root, dir_name)
            if should_remove_file(dir_path, patterns):
                system_files.append(dir_path)
                dirs.remove(dir_name)  # Don't traverse into directories we're going to delete
    
    return system_files

def remove_file_or_directory(path):
    """Safely remove a file or directory."""
    try:
        if os.path.isfile(path):
            os.remove(path)
            return True, "file"
        elif os.path.isdir(path):
            import shutil
            shutil.rmtree(path)
            return True, "directory"
        else:
            return False, "not found"
    except Exception as e:
        logging.error(f"Error removing {path}: {e}")
        return False, "error"

def main():
    logger = setup_logging()
    
    current_directory = os.getcwd()
    logger.info(f"Starting system file cleanup in: {current_directory}")
    
    patterns = get_system_file_patterns()
    logger.info(f"Looking for {len(patterns)} types of system files")
    
    # Find all system files
    system_files = find_system_files(current_directory, patterns)
    
    if not system_files:
        logger.info("No system files found to remove")
        return
    
    logger.info(f"Found {len(system_files)} system files/directories to remove")
    
    # Ask for confirmation before deletion
    print(f"\nFound {len(system_files)} system files/directories:")
    for file_path in system_files[:10]:  # Show first 10
        relative_path = os.path.relpath(file_path, current_directory)
        print(f"  {relative_path}")
    
    if len(system_files) > 10:
        print(f"  ... and {len(system_files) - 10} more")
    
    response = input(f"\nRemove all {len(system_files)} system files? (y/N): ").strip().lower()
    
    if response not in ['y', 'yes']:
        logger.info("Operation cancelled by user")
        return
    
    # Remove the files
    removed_files = 0
    removed_dirs = 0
    errors = 0
    
    for file_path in system_files:
        relative_path = os.path.relpath(file_path, current_directory)
        success, file_type = remove_file_or_directory(file_path)
        
        if success:
            if file_type == "file":
                removed_files += 1
                logger.info(f"Removed file: {relative_path}")
            elif file_type == "directory":
                removed_dirs += 1
                logger.info(f"Removed directory: {relative_path}")
        else:
            errors += 1
    
    logger.info(f"Cleanup complete:")
    logger.info(f"  Files removed: {removed_files}")
    logger.info(f"  Directories removed: {removed_dirs}")
    logger.info(f"  Errors: {errors}")

if __name__ == "__main__":
    main()