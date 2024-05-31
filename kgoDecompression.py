import sys
import math

def GetDecompressedByte(quotient):
  global dbb1
  global dbb3

  magic = 3
  dbb3_curr_idx = quotient >> magic
  dbb3_curr = dbb3[dbb3_curr_idx]
  dbb3_next = dbb3[dbb3_curr_idx+1]
  dbb3_next += 1
  eax = dbb3_curr + 1
  if eax < dbb3_next:
    dbb1_curr_idx = (dbb3_next + dbb3_curr) >> 1
    dbb1_curr = dbb1[dbb1_curr_idx]
    if quotient >= dbb1_curr:
      dbb3_curr = dbb1_curr_idx
    else:
      dbb3_next = dbb1_curr_idx
    curr_idx = dbb3_curr + 1
    while curr_idx < dbb3_next:
      dbb1_curr_idx = (dbb3_next + dbb3_curr) >> 1
      dbb1_curr = dbb1[dbb1_curr_idx]
      if quotient >= dbb1_curr:
        dbb3_curr = dbb1_curr_idx
      else:
        dbb3_next = dbb1_curr_idx
      curr_idx = dbb3_curr + 1
  
  return dbb3_next

def CalculateDBBs():
  global dbb1
  global dbb2
  global dbb3
  global chunk_magic_1
  global chunk_magic_2
  global curr_chunk_size
  global next_chunk_size
  global global_quotient

  if chunk_magic_1 < chunk_magic_2:
    chunk_magic = 2 * chunk_magic_1
    chunk_magic_1 = chunk_magic_2 if chunk_magic > chunk_magic_2 else chunk_magic
  curr_idx = 0x101
  curr_dbb1_idx = curr_idx
  curr_dbb2_idx = curr_idx - 1
  dbb1_curr = dbb1[curr_dbb1_idx]
  curr_dbb1_idx -= 1
  curr_idx -= 1
  next_dbb1_curr = dbb1_curr
  while curr_idx > 0:
    dbb2_curr = dbb2[curr_dbb2_idx]
    curr_dbb2_idx -= 1
    next_dbb1_curr -= dbb2_curr
    curr_dbb1_idx -= 1
    dbb2_curr |= 2
    dbb1[curr_dbb1_idx+1] = (next_dbb1_curr & 0xffff)
    dbb2_curr >>= 1
    curr_idx -= 1
    dbb1_curr -= dbb2_curr
    dbb2[curr_dbb2_idx+1] = (dbb2_curr & 0xffff)
  dbb2_curr = dbb2[0]
  if next_dbb1_curr == dbb2_curr:
    dbb2_curr = (dbb2_curr | 2) >> 1
    dbb2[0] = dbb2_curr
    dbb1_curr -= dbb2_curr
    global_quotient = math.floor(dbb1_curr / chunk_magic_1)
    remainder = dbb1_curr % chunk_magic_1
    next_chunk_size = remainder
    curr_chunk_size = chunk_magic_1 - remainder
    curr_dbb1_idx = 0x101
    while curr_dbb1_idx != 0:
      dbb1_curr = (dbb1[curr_dbb1_idx] - 1) >> 3
      curr_dbb1_idx -= 1
      dbb1_next = dbb1[curr_dbb1_idx] >> 3
      dbb3_curr = dbb3[dbb1_next]
      if dbb1_next <= dbb1_curr:
        dbb1_curr = dbb1_curr - dbb1_next + 1
        while dbb1_curr != 0:
          dbb3[dbb1_next] = curr_dbb1_idx
          dbb1_next += 1
          dbb1_curr -= 1

if len(sys.argv) < 3:
  print("Usage: kgoDecompression.py [file] [output]")
  exit()

# open file to decompress
f = open(sys.argv[1], "rb")
compressed_data = f.read()
f.close()

# calculate the compression size, decompressed size and start indexes of each compressed chunk
compressed_size = int.from_bytes(compressed_data[0:2], "little")
decompressed_size = int.from_bytes(compressed_data[2:4], "little") + 2
size_list = [(compressed_size,decompressed_size,0)]
next = compressed_data[compressed_size:]
while len(next) != 0:
  next_compressed_size = int.from_bytes(next[0:2], "little")
  next_decompressed_size = int.from_bytes(next[2:4], "little") + 2
  prev_size = size_list[len(size_list) - 1]
  next_start = prev_size[0] + prev_size[2]
  size_list.append((next_compressed_size, next_decompressed_size, next_start))
  next = next[next_compressed_size:]

decompressed_data = b''

# Setup Decompression Byte Buffers (dbb)
dbb1 = [0] * 0x101
dbb1.append(0x1000)
# Dbb2 is initialized through data in engine
dbb2 = [
  0x578, 0x280, 0x140, 0xF0, 0xA0, 0x78, 0x50, 0x40, 0x30, 0x28, 0x20, 0x18, 0x14, 0x14, 0x14, 0x14,
  0x10, 0x10, 0x10, 0x10, 0xC, 0xC, 0xC, 0xC, 0xC, 0xC, 0x8, 0x8, 0x8, 0x8, 0x8, 0x8, 0x6, 0x6, 0x6, 0x6,
  0x6, 0x6, 0x6, 0x6, 0x6, 0x6, 0x6, 0x6, 0x6, 0x6, 0x6, 0x6, 0x5, 0x5, 0x5, 0x5, 0x5, 0x5, 0x5, 0x5,
  0x5, 0x5, 0x5, 0x5, 0x5, 0x5, 0x5, 0x5, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4,
  0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4, 0x4,
	0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3,
	0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x3, 0x2, 0x2,
	0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2,
  0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2,
	0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2,
	0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2,
	0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2,
	0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2, 0x2,
	0x2 
]
dbb3 = [0] * 0x200
dbb3.append(0x100)

# Setup Chunk Data
chunk_magic_1 = 0x12
chunk_magic_2 = 0x7D0
curr_chunk_size = 0
next_chunk_size = 0
global_quotient = 0

# Initialise DBB, curr_chunk_size, next_chunk_size and global_quotient
CalculateDBBs()

for size in size_list:
  decompressed_chunk = []
  compressed_size = size[0]
  decompressed_size = size[1]
  compressed_start = size[2]
  compressed_curr_idx = 1

  curr_compressed_data = compressed_data[compressed_start+4:compressed_start+compressed_size]
  curr = curr_compressed_data[compressed_curr_idx]
  compressed_curr_idx += 1

  # initialise a byte buffer made with compressed bytes and counter which determines whether to take the 
  # next compressed byte or not
  processed_byte_buffer = curr >> 1
  process_counter = 0x80

  while True:
    if len(decompressed_chunk) >= decompressed_size:
      break
    if process_counter == 0:
      raise
    
    # determines whether to take the next compressed byte
    while process_counter <= 0x800000:
      val = processed_byte_buffer * 2
      curr = ((curr & 1) | val) << 7
      processed_byte_buffer = curr
      if compressed_curr_idx < compressed_size:
        curr = curr_compressed_data[compressed_curr_idx]
        compressed_curr_idx += 1
      else:
        curr = 0x00
      processed_byte_buffer |= curr >> 1
      process_counter <<= 8

    # uses processed byte buffer and process counter to get the next decompressed byte
    divisor = process_counter >> 0x0C
    quotient = math.floor(processed_byte_buffer/divisor)
    decompressed_byte = GetDecompressedByte(quotient) - 1
    decompressed_chunk.append(decompressed_byte)

    # uses dbb1 to calculate the process counter and processed byte buffer to use in the next iteration
    dbb1_idx = decompressed_byte
    target_dbb2_idx = dbb1_idx
    dbb1_curr = dbb1[dbb1_idx]
    dbb1_next = dbb1[dbb1_idx + 1] - dbb1_curr
    orig_dbb1_next = dbb1_next
    ebx = (divisor * dbb1_curr) & 0xffffffff
    dbb1_next += dbb1_curr
    processed_byte_buffer -= ebx
    if dbb1_next < 0x1000:
      dbb1_idx = (divisor * orig_dbb1_next) & 0xffffffff
    process_counter = dbb1_idx if dbb1_next < 0x1000 else process_counter - ebx

    # Chunk Management - if next chunk size is 0, we reconfigure the DBBs and chunk sizes
    if curr_chunk_size == 0:
      if next_chunk_size == 0:
        CalculateDBBs()
      else:
        curr_chunk_size = next_chunk_size
        global_quotient += 1
        next_chunk_size = 0
    curr_chunk_size -= 1
    # modify dbb2 based on global quotient
    dbb2[target_dbb2_idx] += (global_quotient & 0xffff)
  # add to overall decompressed data
  decompressed_data += bytearray(decompressed_chunk)

f = open(sys.argv[2], "wb")
f.write(decompressed_data)
f.close()
exit()
