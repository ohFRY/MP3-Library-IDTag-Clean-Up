#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import urllib.parse
import os
import sys
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TBPM, TXXX, TKEY, ID3NoHeaderError
import logging
import argparse

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

def parse_rekordbox_location(location):
    # Remove common file URL prefixes
    if location.startswith('file://localhost'):
        location = location[len('file://localhost'):]
    elif location.startswith('file://'):
        location = location[len('file://'):]

    decoded_path = urllib.parse.unquote(location)

    # On Windows URLs Rekordbox sometimes produces paths like '/E:/path/to/file.mp3'
    # Strip a leading slash before a drive letter and normalize separators.
    if os.name == 'nt':
        if len(decoded_path) >= 3 and decoded_path[0] == '/' and decoded_path[2] == ':':
            decoded_path = decoded_path.lstrip('/')
        decoded_path = decoded_path.replace('/', os.sep)

    return decoded_path

def extract_track_data(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    tracks = []
    collection = root.find('COLLECTION')
    if collection is None:
        raise ValueError("No COLLECTION element found in XML")
    
    for track in collection.findall('TRACK'):
        track_data = {
            'name': track.get('Name', 'Unknown'),
            'artist': track.get('Artist', 'Unknown'),
            'bpm': track.get('AverageBpm'),
            'key': track.get('Tonality'),
            'location': track.get('Location')
        }
        
        if track_data['bpm'] and track_data['key'] and track_data['location']:
            tracks.append(track_data)
    
    return tracks

def update_mp3_tags(file_path, bpm, key):
    try:
        audio = MP3(file_path, ID3=ID3)
        
        if audio.tags is None:
            audio.add_tags()
        
        # Remove existing BPM and key tags if they exist
        if 'TBPM' in audio.tags:
            del audio.tags['TBPM']
        if 'TKEY' in audio.tags:
            del audio.tags['TKEY']
        if 'TXXX:BPM' in audio.tags:
            del audio.tags['TXXX:BPM']
        if 'TXXX:INITIALKEY' in audio.tags:
            del audio.tags['TXXX:INITIALKEY']
        
        # Add tags exactly like the reference file
        bpm_int = str(int(float(bpm)))
        audio.tags.add(TBPM(encoding=1, text=[bpm_int]))  # Standard BPM tag
        audio.tags.add(TKEY(encoding=1, text=[key]))      # Standard key tag  
        audio.tags.add(TXXX(encoding=1, desc='INITIALKEY', text=[key]))  # Backup custom key tag
        
        # Save with ID3v2.3 for better compatibility
        audio.save(v2_version=3)
        return True
    except Exception as e:
        logging.error(f"Error updating tags for {file_path}: {e}")
        return False

def log_missing_file(track_name, missing_files_log):
    with open(missing_files_log, 'a', encoding='utf-8') as f:
        f.write(f"{track_name}\n")

def main():
    parser = argparse.ArgumentParser(description='Import BPM and key data from Rekordbox XML to MP3 files')
    parser.add_argument('xml_file', nargs='?', default='rekordbox.xml', 
                        help='Path to Rekordbox XML file (default: rekordbox.xml)')
    parser.add_argument('--missing-log', default='missing_files.txt',
                        help='Path to log file for missing MP3 files (default: missing_files.txt)')
    
    args = parser.parse_args()
    logger = setup_logging()
    
    xml_file = args.xml_file
    missing_files_log = args.missing_log
    
    if not os.path.exists(xml_file):
        logger.error(f"XML file '{xml_file}' not found")
        return
    
    if os.path.exists(missing_files_log):
        os.remove(missing_files_log)
    
    try:
        tracks = extract_track_data(xml_file)
        logger.info(f"Found {len(tracks)} tracks in XML")
        
        processed = 0
        missing = 0
        
        for track in tracks:
            file_path = parse_rekordbox_location(track['location'])
            
            if os.path.exists(file_path):
                if update_mp3_tags(file_path, track['bpm'], track['key']):
                    logger.info(f"Updated: {track['name']} - {track['artist']}")
                    processed += 1
                else:
                    logger.warning(f"Failed to update: {track['name']} - {track['artist']}")
            else:
                logger.warning(f"File not found: {file_path}")
                log_missing_file(f"{track['artist']} - {track['name']}", missing_files_log)
                missing += 1
        
        logger.info(f"Processing complete: {processed} updated, {missing} missing files")
        
        if missing > 0:
            logger.info(f"Missing files logged to: {missing_files_log}")
    
    except Exception as e:
        logger.error(f"Error processing XML: {e}")

if __name__ == "__main__":
    main()