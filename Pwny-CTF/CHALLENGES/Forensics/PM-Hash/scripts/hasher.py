# Pete's Master Hash Algorithm (PM Hash Algo)
import hashlib
password = '???'
def hash_password(password):
  hash = ''
  for i in range(0, len(password), 2):
    chunk = password[i:i+2]
    # Don't ask me why I chose 4, it just felt right
    hash_bit = hashlib.md5(chunk.encode()).hexdigest()[:4]
    hash += hash_bit
  return hash

print(hash_password(password))
# 9272c1d1f611c71643a9d5a59109feb9c51c03c7