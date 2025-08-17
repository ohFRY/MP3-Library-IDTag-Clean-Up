#!/usr/bin/env python3

import os
import logging
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

def get_tags_to_keep():
    """Returns a set of ID3 tag names that should be preserved."""
    return {
        # Standard ID3v2 tags
        'TALB',  # ALBUM
        'TPE2',  # ALBUMARTIST
        'TPE1',  # ARTIST
        'TCMP',  # COMPILATION
        'APIC',  # COVER (Attached Picture)
        'TRCK',  # TRACK
        'TIT2',  # TITLE
        'TDRC', 'TYER',  # YEAR (TDRC is v2.4, TYER is v2.3)
        'COMM',  # COMMENT
        'TCON',  # GENRE
        'TIT1',  # GROUPING
        'TCOM',  # COMPOSER
        'TMOO',  # MOOD
        'TPOS',  # DISCNUMBER
        'TBPM',  # BPM
        'TKEY',  # INITIALKEY
        # Custom tags for compatibility
        'TXXX:BPM',        # Custom BPM
        'TXXX:INITIALKEY', # Custom key
        'TXXX:MOOD',       # Custom mood
        'TXXX:GROUPING',   # Custom grouping
        'TXXX:ALBUMARTIST', # Custom album artist
        'TXXX:COMPILATION', # Custom compilation
    }

def find_mp3_files(directory):
    """Recursively find all MP3 files in directory and subdirectories."""
    mp3_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.mp3'):
                mp3_files.append(os.path.join(root, file))
    return mp3_files

def clean_mp3_metadata(file_path, tags_to_keep):
    """Remove all metadata except specified tags from an MP3 file."""
    try:
        audio = MP3(file_path, ID3=ID3)
        
        if audio.tags is None:
            return True
        
        # Get all current tags
        current_tags = list(audio.tags.keys())
        tags_removed = 0
        
        # Remove tags that are not in the keep list
        for tag in current_tags:
            # Handle TXXX tags specially (they have descriptors)
            if tag.startswith('TXXX:'):
                if tag not in tags_to_keep:
                    del audio.tags[tag]
                    tags_removed += 1
            # Always preserve APIC (cover art) tags
            elif tag.startswith('APIC:'):
                continue
            elif tag not in tags_to_keep:
                del audio.tags[tag]
                tags_removed += 1
        
        # Save the file if any tags were removed
        if tags_removed > 0:
            audio.save(v2_version=4)
            return tags_removed
        
        return 0
        
    except Exception as e:
        logging.error(f"Error cleaning metadata for {file_path}: {e}")
        return False

def main():
    logger = setup_logging()
    
    current_directory = os.getcwd()
    logger.info(f"Starting metadata cleanup in: {current_directory}")
    
    tags_to_keep = get_tags_to_keep()
    logger.info(f"Preserving {len(tags_to_keep)} tag types")
    
    # Find all MP3 files recursively
    mp3_files = find_mp3_files(current_directory)
    logger.info(f"Found {len(mp3_files)} MP3 files")
    
    if not mp3_files:
        logger.info("No MP3 files found")
        return
    
    processed = 0
    total_tags_removed = 0
    errors = 0
    
    for file_path in mp3_files:
        relative_path = os.path.relpath(file_path, current_directory)
        result = clean_mp3_metadata(file_path, tags_to_keep)
        
        if result is False:
            errors += 1
            logger.error(f"Failed to process: {relative_path}")
        elif result > 0:
            total_tags_removed += result
            logger.info(f"Cleaned {result} tags from: {relative_path}")
            processed += 1
        else:
            logger.debug(f"No tags to remove from: {relative_path}")
            processed += 1
    
    logger.info(f"Processing complete:")
    logger.info(f"  Files processed: {processed}")
    logger.info(f"  Total tags removed: {total_tags_removed}")
    logger.info(f"  Errors: {errors}")

if __name__ == "__main__":
    main()