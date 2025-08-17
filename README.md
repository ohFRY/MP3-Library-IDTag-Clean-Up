# MP3 Tag Library Clean Up

A collection of Python scripts for comprehensive MP3 metadata management that goes beyond what traditional tag editors like Mp3Tag can accomplish. Perfect for DJs and music enthusiasts who need advanced metadata control.

## 📝 Why Did I Start This Project

I have my mp3 music library for 20+ years. I'm customising all ID3 tags from my mp3 to organise my music library.

I was struggling with:
- The BPM and the Key calculated in my Pionner RekordBox collection to not be saved in my MP3 files ID3v2.4 data. _This is solved with rekordbox_to_mp3.py script by parsing all the files in my rekordbox collection (rekordbox.xml), extracting these 2 values and writing them onto the files_.
- My home music server (Plex, Navidrome) creating duplicates of the same album name when the mp3 files inside would have different ID3 tag properties. _This is solved with clean_mp3_metadata.py script, by removing all tags, except the ones I care about_.
- My folders being full of system files junk (`._*`, `*.ini`). _This is solved with the remove_system_files.py script by parsing the folder and subfolders and removing them_

## 🎵 What This Project Does

This toolkit provides three powerful scripts to manage your MP3 collection:

1. **Import metadata from Rekordbox** - Sync BPM and key data from your DJ software
2. **Clean unwanted metadata** - Remove bloated tags while preserving only essential metadata
3. **Remove system junk files** - Clean up `.DS_Store`, `._` files, and other OS clutter

## 📋 Scripts Overview

### 1. `rekordbox_to_mp3.py`
Extracts BPM and key information from Rekordbox XML exports and writes them to your MP3 files.

**Features:**
- Parses Rekordbox XML collection exports
- Updates MP3 files with BPM and musical key data
- Handles file path conversion from Rekordbox URLs
- Logs missing files for easy troubleshooting
- Uses ID3v2.3 tags for maximum compatibility

### 2. `clean_mp3_metadata.py`
Removes unnecessary metadata tags while preserving only essential information.

**Preserved Tags:**
- ALBUM, ALBUMARTIST, ARTIST
- COMPILATION, COVER (artwork)
- TRACK, TITLE, YEAR
- COMMENT, GENRE, GROUPING
- COMPOSER, MOOD, DISCNUMBER
- BPM, INITIALKEY

**Features:**
- Recursively processes all MP3 files in subdirectories
- Preserves album artwork (APIC tags)
- Saves files with ID3v2.4 format
- Detailed logging of removed tags
- Safe processing with error handling

### 3. `remove_system_files.py`
Removes system-generated files that clutter your music directories.

**Removes:**
- macOS: `._*`, `.DS_Store`, `.AppleDouble`, etc.
- Windows: `Thumbs.db`, `Desktop.ini`, etc.
- Cloud sync artifacts: `.dropbox`, `.dropbox.attr`
- NAS thumbnails: `@eaDir`, `.@__thumb`
- Temporary files: `*.tmp`, `*.temp`

**Features:**
- Recursive directory scanning
- Safety confirmation before deletion
- Detailed removal logging
- Cross-platform compatibility

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup

#### macOS/Linux:
```bash
# Clone or download the repository
cd mp3-tag-library-clean-up

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install mutagen
```

#### Windows:
```cmd
# Clone or download the repository
cd mp3-tag-library-clean-up

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install mutagen
```

## 📖 Usage

### 1. Import Rekordbox Metadata

First, export your Rekordbox collection:
1. In Rekordbox: File → Export Collection in xml format
2. Save as `test.xml` in the script directory

```bash
python rekordbox_to_mp3.py
```

### 2. Clean MP3 Metadata

Navigate to your music directory and run:

```bash
# Activate virtual environment first
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Clean metadata
python clean_mp3_metadata.py
```

### 3. Remove System Files

```bash
python remove_system_files.py
```

The script will show you what it found and ask for confirmation before deletion.

## ⚠️ Important Safety Notes

- **Always backup your music collection** before running these scripts
- Test on a small subset of files first
- The metadata cleaning is **irreversible** - removed tags cannot be recovered
- System file removal will permanently delete files

## 🔧 Configuration

### Customizing Preserved Tags

Edit `clean_mp3_metadata.py` and modify the `get_tags_to_keep()` function to add or remove tag types:

```python
def get_tags_to_keep():
    return {
        'TALB',  # ALBUM
        'TPE1',  # ARTIST
        # Add your custom tags here
    }
```

### Customizing System File Patterns

Edit `remove_system_files.py` and modify the `get_system_file_patterns()` function:

```python
def get_system_file_patterns():
    return [
        '._*',           # AppleDouble files
        '.DS_Store',     # Directory Services Store
        # Add your custom patterns here
    ]
```

## 📊 Example Output

### Metadata Cleaning:
```
2025-08-17 23:11:34,941 - INFO - Starting metadata cleanup in: /Users/music/collection
2025-08-17 23:11:34,941 - INFO - Preserving 23 tag types
2025-08-17 23:11:34,958 - INFO - Found 1,247 MP3 files
2025-08-17 23:11:34,962 - INFO - Cleaned 9 tags from: Artist - Track.mp3
2025-08-17 23:11:34,966 - INFO - Processing complete:
2025-08-17 23:11:34,966 - INFO -   Files processed: 1,247
2025-08-17 23:11:34,966 - INFO -   Total tags removed: 15,832
2025-08-17 23:11:34,966 - INFO -   Errors: 0
```

### System File Removal:
```
Found 156 system files/directories:
  .DS_Store
  Artist Album/._Track.mp3
  Various/.AppleDouble
  ... and 153 more

Remove all 156 system files? (y/N): y
```

## 🛠️ Troubleshooting

### "Module not found" errors
Make sure you've activated the virtual environment and installed mutagen:
```bash
source .venv/bin/activate  # macOS/Linux
pip install mutagen
```

### "Can't sync to MPEG frame" errors
This usually means system files (like `._` files) are being processed as MP3s. Run the system file cleaner first:
```bash
python remove_system_files.py
```

### Permission errors
On Windows, you might need to run as Administrator for some system locations.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests. This project aims to solve metadata management problems that traditional tools can't handle.

## 📄 License

This project is open source. Use at your own risk and always backup your files.

## 🎧 Why This Project?

Traditional MP3 tag editors like Mp3Tag are powerful but have limitations:
- Can't easily bulk-remove unwanted metadata while preserving specific tags
- Don't integrate well with DJ software exports
- Can't handle system file cleanup in music directories
- Limited scripting capabilities for complex operations

This toolkit fills those gaps with purpose-built Python scripts that give you complete control over your music metadata.