# Corrupted File Checker

It can be check for the files even if it is not in the same directory or folder as the file.

## How to Run

```bash
python3 corrupted_file_checker.py
```

If no path is given, it will prompt for one.

## Supported Formats

`.zip` `.tar` `.gz` `.tgz` `.json` `.ipynb` `.csv` `.pkl` `.pickle` `.db` `.py` `.pdf` `.doc` `.xpt` `.c` `.cpp` `.sql` `.r` `.html` `.css` `.java` `.js` `.javascript` `.md`

## Validation Logic

- `.zip`, `.tar`, `.gz`, `.tgz`: For gzip-based files (`.gz`, `.tgz`), the full compressed stream is decompressed to verify the trailing CRC32 and length fields. For tar-based files (`.tar`, `.tgz`), each entry's header checksum and declared data are read to confirm the archive table is intact. For `.zip`, each entry's CRC is checked via `testzip()`.
- `.json`, `.ipynb`: It parses the object syntax. For Jupyter notebooks, it additionally enforces the presence of required structural fields (`cells` and `metadata`).
- `.csv`: It decodes and scans the full stream row by row, tracking array delimiters from start to end.
- `.pkl`, `.pickle`: It runs an unpickling read step to check for data serialization stream breaks.
- `.db`: It maps onto the file as a database connection and uses database engine commands (`PRAGMA integrity_check`) to parse cell pages.
- `.py`: It uses Python's compiler subsystem to confirm the source file contains syntactically correct code blocks.
- `.pdf`: It targets byte arrays at the head and tail (clamped to file size) searching for the specific signature hex boundaries (`%PDF` and `%%EOF`).
- `.doc`: It reads the signature block for structural Microsoft Compound File compliance.
- `.xpt`: It evaluates the high-level header sequence against SAS transport layouts.
- `.c`, `.cpp`, `.sql`, `.r`, `.html`, `.css`, `.java`, `.js`, `.javascript`, `.md`: It parses the full file into buffer memory and checks for embedded null bytes (illegal binary injection), then decodes it via standard string decoders to ensure it contains uncorrupted, human-readable text.
