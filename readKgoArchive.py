import sys
from pathlib import Path

if len(sys.argv) < 3:
  print("Usage: readKgoArchive.py [file] [directory]")
  exit()

# Create Directory to store files
directory = f'./{sys.argv[2]}/{sys.argv[1]}'
Path(directory).mkdir(parents=True, exist_ok=True)

f = open(sys.argv[1], "rb")
data = f.read()
f.close()

# Read location of file table and the amount of entries
file_table_idx = int.from_bytes(data[8:12], "little") + 0x10
entries = int.from_bytes(data[12:16], "little")

file_table = data[file_table_idx:]

# Process the files
curr_idx = 0
for i in range(entries):
  filename = file_table[curr_idx:curr_idx+0x15].decode("utf-8").rstrip('\x00')
  curr_idx += 0x15
  extension = file_table[curr_idx:curr_idx+0x3].decode("utf-8").rstrip('\x00')
  curr_idx += 0x3
  start_idx = int.from_bytes(file_table[curr_idx:curr_idx+0x4], "little") + 0x10
  curr_idx += 0x4
  decompressed_size = int.from_bytes(file_table[curr_idx:curr_idx+0x4], "little")
  curr_idx += 0x4
  compressed_size = int.from_bytes(file_table[curr_idx:curr_idx+0x4], "little")
  curr_idx += 0x10
  f = open(f'{directory}/{filename}.{extension}', "wb")
  f.write(data[start_idx:start_idx+compressed_size])
  f.close()

exit()