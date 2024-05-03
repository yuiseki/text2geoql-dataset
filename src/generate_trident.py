import random
import hashlib
import os
import sys

examples = []


def add_examples_from_dir(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "input-trident.txt":
                input_txt = open(os.path.join(root, file), "r").read().strip()
                if input_txt == "":
                    continue
                example = {
                    "input": input_txt,
                    "path": os.path.join(root, file),
                }
                examples.append(example)


dir_path = "./data"
add_examples_from_dir(dir_path)

seed_areas = []
seed_concerns = []

for example in examples:
    input_txt = example["input"]
    if input_txt.startswith("SubArea:"):
        continue
    if input_txt.startswith("Area:"):
        if ";" in input_txt:
            continue
        # ","が2つ未満の場合はスキップ
        if input_txt.count(",") < 2:
            continue
        new_area = input_txt.replace("Area: ", "").strip()
        if new_area in seed_areas:
            continue
        seed_areas.append(new_area)
    else:
        # ;以降のみを取得
        new_concern = input_txt.split(";")[1].strip()
        if new_concern in seed_concerns:
            continue
        seed_concerns.append(new_concern)


# Generate AreaWithConcern from seeds
area_with_concerns = []

for area in seed_areas:
    for concern in seed_concerns:
        area_with_concern = f"AreaWithConcern: {area}; {concern}"
        # examplesのinputに含まれている場合はスキップ
        if area_with_concern in [example["input"] for example in examples]:
            continue
        area_with_concerns.append(area_with_concern)

# Shuffle area_with_concerns

random.seed(42)
random.shuffle(area_with_concerns)

for area_with_concern in area_with_concerns:
    print(area_with_concern)
