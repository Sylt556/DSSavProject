from hashlib import blake2b
import os




def hash_blake2b(fname):
    if not os.path.isfile(fname):
        raise Exception('DB does not exist')
    
    hash_blake2b = blake2b(key=b'chiaveSegreta', digest_size=64)
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_blake2b.update(chunk)
    return hash_blake2b.hexdigest()





