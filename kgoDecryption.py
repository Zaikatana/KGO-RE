import sys
import math

def decryption_pass_1():
  global decompressed_data
  # Perform 1st pass decryption
  # create buffer from 0x00 - 0xFF
  buff = list(range(0x00, 0x100))

  # Perform decryption algorithm
  decrypted_data = []
  for x in decompressed_data:
    curr = buff.pop(x)
    decrypted_data.append(curr)
    buff.insert(0, curr)

  return decrypted_data

def decryption_pass_2():
  global decompressed_data
  entries = []
  decrypted_data = b''

  # Generate start and end indexes for decompressed chunks (normally size 0x2002)
  full_chunk_size = math.floor(len(decompressed_data)/0x2002)
  if full_chunk_size > 0:
    remainder = len(decompressed_data) - (full_chunk_size * 0x2002)
    for i in range(full_chunk_size):
      entries.append((i * 0x2002, 0x2002))
    entries.append((full_chunk_size * 0x2002, remainder))
  else:
    entries.append((0, len(decompressed_data)))
  for entry in entries:
    entry_start = entry[0]
    entry_size = entry[1]
    data = decompressed_data[entry_start:entry_start+entry_size]
	  # Perform 2nd pass decryption
	  # Generate Frequency map
    freq_map = [0] * 0x100
    for i in range(2, entry_size):
      freq_map[data[i]] += 1

	  # From frequency map, generate indexes
    freq_map_idx = [freq_map[0]]
    for i in range(1, len(freq_map)):
      freq_map_idx.append(freq_map[i] + freq_map_idx[i - 1])

	  # Generate Magic Numbers
    magic_numbers = [0] * (entry_size + 1)
    curr_idx = entry_size - 1
    magic_data = entry_size - 3
    while magic_data >= 0:
      curr = data[curr_idx]
      freq_map_idx[curr] -= 1
      hash2_idx = freq_map_idx[curr]
      magic_numbers[hash2_idx] = magic_data
      curr_idx -= 1
      magic_data -= 1

	  # Decrypt Data
    decrypted_chunk = []
    curr_idx = 2
    magic = (data[1] << 8) | data[0]
    while curr_idx < entry_size:
      magic = magic_numbers[magic]
      decrypted_chunk.append(data[2 + magic])
      curr_idx += 1
    decrypted_data += bytearray(decrypted_chunk)

  return decrypted_data

if len(sys.argv) < 3:
  print("Usage: kgoDecryption.py [file] [output]")
  exit()

# open file to decrypt
f = open(sys.argv[1], "rb")
decompressed_data = f.read()
f.close()

# decryption pass 1
decompressed_data = decryption_pass_1()

# decryption pass 2
decrypted_data = decryption_pass_2()

# write decrypted file
f = open(sys.argv[2], "wb")
f.write(decrypted_data)
f.close()
exit()
