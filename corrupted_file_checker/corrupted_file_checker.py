import os
import sys
import zipfile
import tarfile
import gzip
import json
import csv
import py_compile
import sqlite3
import pickle

def check_file_health(filepath):
    # Convert to an absolute path so it runs from any directory
    absolute_path = os.path.abspath(filepath)
    
    print("Target File: " + absolute_path)
    
    # Baseline System Checks
    if not os.path.exists(absolute_path):
        print("RESULT: FAIL - File does not exist at the specified path.")
        return False

    if not os.access(absolute_path, os.R_OK):
        print("RESULT: FAIL - Read permission denied.")
        return False

    file_size = os.path.getsize(absolute_path)
    if file_size == 0:
        print("RESULT: FAIL - File is completely empty (0 bytes).")
        return False

    # Extract extension for explicit structural checks
    _, extension = os.path.splitext(absolute_path)
    ext = extension.lower()

    try:
        # 1. Archive Formats (.zip, .tar, .gz, .tgz)
        if ext == '.zip':
            with zipfile.ZipFile(absolute_path, 'r') as archive:
                bad_file = archive.testzip()
                if bad_file is not None:
                    print("RESULT: FAIL - Corrupted file found inside zip: " + bad_file)
                    return False

        elif ext in ['.tar', '.gz', '.tgz']:
            with open(absolute_path, 'rb') as f:
                magic = f.read(2)
            is_gzip = (magic == b'\x1f\x8b')
            is_tar = tarfile.is_tarfile(absolute_path)

            if not is_gzip and not is_tar:
                print("RESULT: FAIL - Not a valid tar or gzip archive framework.")
                return False

            if is_gzip:
                # Decompress the raw gzip stream all the way to its true
                # end, regardless of any tar member size fields, so
                # zlib verifies the CRC32 / length fields in the
                # gzip trailer (catches truncation tarfile misses).
                with gzip.open(absolute_path, 'rb') as gz:
                    while True:
                        chunk = gz.read(65536)
                        if not chunk:
                            break

            if is_tar:
                # Walk every member's header (checksum-validated by
                # tarfile) and read its declared data to catch
                # malformed size/offset entries.
                with tarfile.open(absolute_path, 'r') as archive:
                    for member in archive.getmembers():
                        if member.isfile():
                            extracted = archive.extractfile(member)
                            if extracted is not None:
                                while True:
                                    chunk = extracted.read(65536)
                                    if not chunk:
                                        break

        # 2. Data & Notation Structures (.json, .ipynb, .csv, .pkl)
        elif ext == '.json':
            with open(absolute_path, 'r', encoding='utf-8') as f:
                json.load(f)

        elif ext == '.ipynb':
            with open(absolute_path, 'r', encoding='utf-8') as f:
                notebook_data = json.load(f)
                if "cells" not in notebook_data or "metadata" not in notebook_data:
                    print("RESULT: FAIL - Corrupted Jupyter Notebook metadata structure.")
                    return False

        elif ext == '.csv':
            with open(absolute_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    pass

        elif ext in ['.pkl', '.pickle']:
            with open(absolute_path, 'rb') as f:
                pickle.load(f)

        # 3. Database Files (.db)
        elif ext == '.db':
            conn = sqlite3.connect(absolute_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            db_status = cursor.fetchone()
            conn.close()
            if db_status[0] != "ok":
                print("RESULT: FAIL - SQLite database internal corruption: " + str(db_status[0]))
                return False

        # 4. Compiled Python Scripts (.py)
        elif ext == '.py':
            py_compile.compile(absolute_path, doraise=True)

        # 5. Document Formats (.pdf, .doc)
        elif ext == '.pdf':
            with open(absolute_path, 'rb') as f:
                header = f.read(4)
                if header != b'%PDF':
                    print("RESULT: FAIL - Missing valid %PDF header.")
                    return False
                # Clamp the footer-scan window to the actual file size so
                # small PDFs don't trigger an invalid negative seek.
                seek_size = min(1024, file_size)
                f.seek(-seek_size, os.SEEK_END)
                footer = f.read()
                if b'%%EOF' not in footer:
                    print("RESULT: FAIL - Missing valid %%EOF footer token.")
                    return False

        elif ext == '.doc':
            with open(absolute_path, 'rb') as f:
                header = f.read(8)
                if header != b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
                    print("RESULT: FAIL - Invalid legacy OLE compound document structure.")
                    return False

        # 6. Statistical Formats (.xpt)
        elif ext == '.xpt':
            with open(absolute_path, 'rb') as f:
                header = f.read(40)
                if b'HEADER RECORD' not in header:
                    print("RESULT: FAIL - Invalid SAS XPT file header syntax.")
                    return False

        # 7. Plain-Text Code & Markups (.c, .cpp, .sql, .r, .html, .css, .java, .js, .javascript, .md)
        elif ext in ['.c', '.cpp', '.sql', '.r', '.html', '.css', '.java', '.js', '.javascript', '.md']:
            with open(absolute_path, 'rb') as f:
                raw_data = f.read()
            # Null bytes are valid UTF-8 but indicate binary data embedded
            # in what should be a plain-text source/markup file.
            if b'\x00' in raw_data:
                print("RESULT: FAIL - Illegal binary injection (null byte) detected in source text.")
                return False
            raw_data.decode('utf-8')

        # 8. Unmapped Extensions Fallback (Sector Verification)
        else:
            with open(absolute_path, 'rb') as f:
                f.read(1024)
                if file_size > 1024:
                    f.seek(-1024, os.SEEK_END)
                    f.read(1024)

        print("RESULT: PASS - File passed integrity checks.")
        return True

    except Exception as e:
        print("RESULT: FAIL - Structural verification error.")
        print("DETAILS: " + str(e))
        return False

# Command-line input processing
if len(sys.argv) > 1:
    target_file = sys.argv[1]
else:
    target_file = input("Enter file path to verify: ")

check_file_health(target_file)