import os
import json
import hashlib

def compute_hash(units):
    units_str = json.dumps(units, sort_keys=True)
    return hashlib.sha256(units_str.encode()).hexdigest()

def read_last_hash(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.read().strip()
    return None

def write_hash(file_path, hash_value):
    with open(file_path, 'w') as file:
        file.write(hash_value)