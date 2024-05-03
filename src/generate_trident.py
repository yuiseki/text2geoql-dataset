import hashlib
import os
import sys

examples = []


def add_examples_from_dir(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "input-trident.txt":
                input_txt = open(os.path.join(root, file), "r").read().strip()
                example = {
                    "input": input_txt,
                    "path": os.path.join(root, file),
                }
                examples.append(example)


dir_path = "./data"
add_examples_from_dir(dir_path)

for example in examples:
    print(example)
