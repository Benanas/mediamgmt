#-------------------------------------------------------------------------------
# Name:        MediaManager
# Purpose:
#
# Author:      Benanas
# Created:     17-10-2024
#-------------------------------------------------------------------------------

# # SQL and JSON cache libraries
import sqlite3
import json
from PIL import Image
from PIL.ExifTags import TAGS
import os

# # Duplicate Finder Libraries
import os
import hashlib
from collections import defaultdict

class MediaManager:

    def __init__(self, library_path, cache_db=None):

        # # Initializes the MediaManager with the media library path and optional cache database.
        self.library_path = library_path
        self.cache_db = cache_db  # Optional: Could integrate with SQLiteCache
        self.library = []  # List to hold MediaFile objects

    def scan_files(self):

        # # Scans the media library directory and loads all media files (photos, videos) into memory.
        supported_extensions = ['.jpg', '.jpeg', '.png', '.mp4', '.mov', '.gif']  # Extend as needed

        for root, dirs, files in os.walk(self.library_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in supported_extensions):
                    file_path = os.path.join(root, file)
                    media_file = MediaFile(file_path)
                    self.library.append(media_file)

        print(f"Loaded {len(self.library)} media files from {self.library_path}")

    def get_library_summary(self):

        # # Returns a summary of the media library, including number of files by type.
        summary = {
            'total_files': len(self.library),
            'image_files': sum(1 for file in self.library if file.is_image()),
            'video_files': sum(1 for file in self.library if file.is_video()),
        }
        return summary

    def clean_duplicates(self):

        # # Detects and marks duplicate media files for review (placeholder, duplicate logic to be added).
        # You would integrate DuplicateFinder or other methods here
        pass

    def organize_files(self, destination_folder):

        # # Organizes media files based on metadata (e.g., by date or type) and moves them to new folders.
        # Placeholder for calling FileOrganizer logic
        pass


class MediaFile:

    def __init__(self, file_path):

        # # Initializes a MediaFile object and extracts its metadata.
        self.file_path = file_path
        self.metadata = self.extract_metadata()

    def extract_metadata(self):

        # # Extracts metadata from the media file, such as date taken, dimensions, etc.
        metadata = {}
        if self.is_image():
            metadata = self.extract_image_metadata()
        elif self.is_video():
            metadata = self.extract_video_metadata()
        return metadata

    def extract_image_metadata(self):

        # # Extracts metadata from image files (e.g., EXIF data for JPG).
        metadata = {}
        try:
            image = Image.open(self.file_path)
            exif_data = image._getexif()

            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    metadata[tag_name] = value
        except Exception as e:
            print(f"Error extracting metadata from {self.file_path}: {e}")
        return metadata

    def extract_video_metadata(self):

        # # Extracts metadata from video files (e.g., duration, resolution) (Placeholder).
        # You would use libraries like ffmpeg, moviepy, etc. for video metadata extraction
        metadata = {
            "duration": "Unknown",
            "resolution": "Unknown"
        }
        return metadata

    def is_image(self):
        # # Checks if the file is an image.
        return os.path.splitext(self.file_path)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif']

    def is_video(self):

        # # Checks if the file is a video.
        return os.path.splitext(self.file_path)[1].lower() in ['.mp4', '.mov', '.avi', '.mkv']

    def tag_file(self, tags):

        # # Adds or updates tags for the media file.
        self.metadata['tags'] = tags

    def is_modified(self):

        # # Checks if the file has been modified since its metadata was last cached.
        cached_last_modified = self.cache.get_last_modified(self.file_path)
        current_last_modified = os.path.getmtime(self.file_path)

        return current_last_modified > cached_last_modified

    def __repr__(self):

        # # Returns a string representation of the MediaFile object.
        return f"<MediaFile: {os.path.basename(self.file_path)} | Metadata: {self.metadata}>"


class FileOrganizer:

    def __init__(self, destination_folder):
        self.destination_folder = destination_folder

    def move_files(self, media_files):
        """Moves media files to organized folders based on their metadata."""
        pass


class DuplicateFinder:
    def __init__(self, media_manager):

        # # Initializes the DuplicateFinder with access to the MediaManager's library.
        self.media_manager = media_manager
        self.duplicates = defaultdict(list)  # A dictionary to store duplicates

    def hash_file(self, file_path, block_size=65536):

        # # Generates a hash for a given file. Defaults to SHA-256, which is more secure, but MD5 can be used for speed if preferred.
        hasher = hashlib.sha256()  # Alternatively, use hashlib.md5() for faster but less secure hashing
        with open(file_path, 'rb') as f:
            while chunk := f.read(block_size):
                hasher.update(chunk)
        return hasher.hexdigest()

    def find_duplicates_by_hash(self):

        # # Finds duplicate files based on file hashes. If two files have the same hash, they are considered duplicates.
        file_hashes = {}

        for media_file in self.media_manager.library:
            file_path = media_file.file_path
            file_hash = self.hash_file(file_path)

            if file_hash in file_hashes:
                self.duplicates[file_hash].append(media_file)
            else:
                file_hashes[file_hash] = media_file

        # Store only hash keys with more than one associated file (duplicates)
        self.duplicates = {hash_key: files for hash_key, files in self.duplicates.items() if len(files) > 1}
        print(f"Found {len(self.duplicates)} sets of duplicate files by hash.")

    def find_duplicates_by_metadata(self):

        # # Finds duplicate files by comparing metadata (e.g., creation date, size, and dimensions).
        metadata_map = defaultdict(list)

        for media_file in self.media_manager.library:
            metadata_key = self.generate_metadata_key(media_file)
            metadata_map[metadata_key].append(media_file)

        # Store duplicates based on metadata key
        self.duplicates = {key: files for key, files in metadata_map.items() if len(files) > 1}
        print(f"Found {len(self.duplicates)} sets of duplicate files by metadata.")

    def generate_metadata_key(self, media_file):

        # # Generates a key based on important metadata fields (e.g., creation date, size, and dimensions)
        to find duplicates.
        return (
            media_file.metadata.get("DateTimeOriginal", None),
            media_file.metadata.get("FileSize", None),
            media_file.metadata.get("ImageWidth", None),
            media_file.metadata.get("ImageHeight", None),
            os.path.splitext(media_file.file_path)[1]  # File extension
        )

    def resolve_duplicates(self):

        # # Presents duplicate files and suggests which to keep/delete, potentially interacting with the user.
        for hash_key, duplicate_files in self.duplicates.items():
            print(f"Found duplicates: {[f.file_path for f in duplicate_files]}")
            # You can implement more logic here, such as automatically keeping the largest file,
            # or the one with the best quality or the earliest modification date.
            # For now, we'll just print them and let the user decide.
            self.suggest_removal(duplicate_files)

    def suggest_removal(self, duplicate_files):

        # # Suggests which file to delete, based on user-defined preferences or heuristics.
        print("Duplicates detected:")
        for i, file in enumerate(duplicate_files):
            print(f"{i + 1}: {file.file_path} (Size: {os.path.getsize(file.file_path)} bytes)")

        # Example logic: keep the first one, delete the rest (could be changed to a user input).
        keep_index = 0
        for i, file in enumerate(duplicate_files):
            if i != keep_index:
                print(f"Suggest deleting {file.file_path}")
                # Optionally: os.remove(file.file_path)  # Be careful here!


class MediaCache:

    def __init__(self, db_path="media_metadata.db"):

        # # Initializes the SQLite database for storing media file metadata.
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):

        # # Creates tables to store media file metadata if they don't exist.
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS media_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE,
                    file_type TEXT,
                    metadata TEXT,
                    tags TEXT,
                    last_modified TIMESTAMP
                )
            ''')

    def update_metadata(self, file_path, file_type, metadata, tags):

        # # Inserts or updates metadata for a media file.
        with self.conn:
            self.conn.execute('''
                INSERT INTO media_metadata (file_path, file_type, metadata, tags, last_modified)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(file_path) DO UPDATE SET
                    metadata = excluded.metadata,
                    tags = excluded.tags,
                    last_modified = excluded.last_modified
            ''', (file_path, file_type, metadata, tags))

    def get_metadata(self, file_path):

        # # Retrieves metadata for a given file path from the database.
        cursor = self.conn.execute('SELECT file_type, metadata, tags FROM media_metadata WHERE file_path = ?', (file_path,))
        return cursor.fetchone()

    def close(self):

        # # Closes the database connection.
        self.conn.close()

class Classifier:
    def __init__(self, model):
        self.model = model

    def classify_images(self, media_files):
        """Classifies media files and returns tags."""
        pass