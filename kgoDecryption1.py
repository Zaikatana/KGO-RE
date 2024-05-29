import sys

if len(sys.argv) < 3:
  print("Usage: kgoDecryption1.py [file] [output]")
  exit()

# read decompressed data
f = open(sys.argv[1], "rb")
decompressed_data = f.read()
f.close()

# Perform 1st pass decryption
# create buffer from 0x00 - 0xFF
buff = list(range(0x00, 0x100))

# Perform decryption algorithm
decrypted_data = []
for x in decompressed_data:
  curr = buff.pop(x)
  decrypted_data.append(curr)
  buff.insert(0, curr)

# write decrypted data to file
f = open(sys.argv[2], "wb")
f.write(bytearray(decrypted_data))
f.close()
exit()
