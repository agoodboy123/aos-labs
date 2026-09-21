#!/usr/bin/env python3
import os
import random
import string

os.makedirs('data/input', exist_ok=True)

for i in range(20):
    path = f'data/input/file_{i}.txt'
    with open(path, 'w', encoding='utf-8') as f:
        for _ in range(200):
            line = ' '.join(random.choices(string.ascii_letters, k=10))
            f.write(line + '\n')
    print(f'created {path}')
