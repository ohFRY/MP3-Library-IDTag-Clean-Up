#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import urllib.parse
import os
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TBPM, TXXX, TKEY, ID3NoHeaderError
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

def parse_rekordbox_location(location):
    if location.startswith('file://localhost'):
        location = location[16:]
    
    decoded_path = urllib.parse.unquote(location)
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
    logger = setup_logging()
    
    xml_file = 'test.xml'  # Use test.xml for validation
    missing_files_log = 'missing_files.txt'
    
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