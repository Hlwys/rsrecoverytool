import os
import threading
import time

# Define the 6-byte sequences to search for (as hex strings)
hex_patterns = [
    "000a2f032489", #title",
    "000a62a3f043", #title",
    "0034909f70f6", #media",
    "0036909f70f6", #media",
    "0037909f70f6", #media",
    "003707811d70", #media",
    "004907811d70", #media",
    "004c07811d70", #media",
    "001516c8ae55", #models",
    "00330d66e56b", #texture",
    "00046245babb", #wordenc",
    "0004ddd362b7", #wordenc",
    "0004cde16282", #wordenc",
    "0004650456bc", #wordenc",
    "00010de00c5f", #sounds",
    "001034d1b7b8", #config",
    "001234d1b7b8", #config",
    "0012e14fb6af", #config",
    "00180ae38f79", #config",
    "00183d5965ac", #config",
    "001858c1fcdc", #config",
    "001893a36c54", #config",
    "001a58c1fcdc", #config",
    "314159265359",	#wholearchive
    "0632e32100", #"textures5to7",
    "0631f93600", #"textures8to15",
    "29df679e00", #"media48to58",
    "29edbf2901", #"entity20to24",
    "2dec5e1f00", #"entity10to19",
    "2ded480a01", #"entity4to8",
    "5e9c595300", #"maps14to27",
    "8138952900", #"media28to47",
    "816a8a8e01", #"entity12to19mem",
    "8384eb9200", #"textures15to17",
    "a38c6bba00", #"entity20to24mem",
    "d0fab5f400", #"entity7",
    "078d67ba", #"243 245 june2004",
    "1874c632", #"274 november2004",
    "2c3910d6", #"324 325 july2005",
    "3cd1cf37", #"270 november2004",
    "46c2823c", #"254 september2004",
    "9509ece5", #"365 377 2006",
    "de5b3345", #"289 347 2005",
    "e652d358", #"186 225 beta2004",
    "e8059684", #"350 363 2006", 
    "ec8aa7b6", #"349 december2005"
    "08fd540b0002", #"config failsafe"	
    "2000636c6f616465722e636c617373", #"loadercab"
    "006c6f616465722e636c617373", #"loaderjarRSC"
    "007369676e2f7369676e6c696e6b2e636c617373", #loaderjarRS2"
]

# Convert to byte patterns
patterns = [bytes.fromhex(p) for p in hex_patterns]

# Shared progress tracker
progress = {
    "bytes_scanned": 0,
    "start_time": time.time(),
    "done": False,
    "file_size": 1  # will be updated dynamically
}

def report_progress():
    if progress["done"]:
        return

    scanned = progress["bytes_scanned"]
    total = progress["file_size"]
    elapsed = time.time() - progress["start_time"]
    percent = (scanned / total) * 100 if total > 0 else 0
    remaining = (elapsed / scanned * (total - scanned)) if scanned else 0

    print(f"[{int(elapsed)}s] Scanned {scanned / (1024 * 1024):.2f} MB "
          f"({percent:.2f}%) - Est. time remaining: {int(remaining)}s")

    threading.Timer(30.0, report_progress).start()

def scan_image(file_path, patterns):
    offsets_found = {pattern.hex(): [] for pattern in patterns}
    chunk_size = 1024 * 1024
    max_pattern_len = max(len(p) for p in patterns)

    file_size = os.path.getsize(file_path)
    progress["file_size"] = file_size

    with open(file_path, 'rb') as f:
        overlap = max_pattern_len - 1
        position = 0
        prev_data = b''

        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            data = prev_data + chunk
            for pattern in patterns:
                start = 0
                while True:
                    index = data.find(pattern, start)
                    if index == -1:
                        break
                    absolute_offset = position - len(prev_data) + index
                    print(f"Found pattern {pattern.hex()} at offset 0x{absolute_offset:012x}")
                    offsets_found[pattern.hex()].append(absolute_offset)
                    start = index + 1

            prev_data = data[-overlap:]
            position += len(chunk)
            progress["bytes_scanned"] = position

    progress["done"] = True
    return offsets_found

def write_output(results, output_path="output.txt"):
    with open(output_path, 'w') as out:
        for pattern, offsets in results.items():
            if offsets:
                out.write(f"Pattern {pattern} found at offsets:\n")
                for offset in offsets:
                    out.write(f"  0x{offset:012x}\n")
                out.write("\n")

# === Entry point ===
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python scan_drive_image.py <image_file>")
        sys.exit(1)

    image_file = sys.argv[1]
    print("Starting scan...")

    report_progress()  # Start periodic progress reports
    results = scan_image(image_file, patterns)
    write_output(results)

    print("Scan complete. Results written to output.txt.")

