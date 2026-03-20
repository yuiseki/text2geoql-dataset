import os

import yaml

examples: list[dict[str, str]] = []


def add_examples_from_dir(directory: str) -> None:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "input-trident.txt":
                input_txt = open(os.path.join(root, file)).read().strip()
                if input_txt == "":
                    continue
                example: dict[str, str] = {
                    "input": input_txt,
                    "path": os.path.join(root, file),
                }
                examples.append(example)


dir_path = "./data"
add_examples_from_dir(dir_path)

# list of dict
# keys: concern, path
seed_concerns: list[dict[str, str]] = []

# read yaml file
# Key-value pairs of concern word and path to save
good_concerns_path = "good_concerns.yaml"
with open(good_concerns_path) as f:
    good_concerns: dict[str, str] = yaml.safe_load(f)
    for concern, path in good_concerns.items():
        seed_concerns.append({"concern": concern, "base_path": path})


seed_areas: list[str] = []
for example in examples:
    input_txt = example["input"]
    if input_txt.startswith("SubArea:"):
        continue
    if input_txt.startswith("AreaWithConcern:"):
        continue
    if input_txt.startswith("Area:"):
        if ";" in input_txt:
            continue
        if "Hong Kong" in input_txt or "Seoul" in input_txt:
            # ","が2つ未満の場合はスキップ
            if input_txt.count(",") < 2:
                continue
        else:
            # ","が3つ未満の場合はスキップ
            if input_txt.count(",") < 3:
                continue
        new_area = input_txt.replace("Area: ", "").strip()
        if new_area in seed_areas:
            continue
        seed_areas.append(new_area)


# Generate AreaWithConcernsAndPath from seeds
# list of dict
# keys: area_with_concern, path
area_with_concerns_and_path: list[dict[str, str]] = []

for area in seed_areas:
    for concern_item in seed_concerns:
        area_with_concern = f"AreaWithConcern: {area}; {concern_item['concern']}"
        # area_with_concernがexamplesのinputに含まれている場合はスキップ
        if area_with_concern in [example["input"] for example in examples]:
            continue
        item_base_path = concern_item["base_path"]
        area_with_concerns_and_path.append(
            {"area_with_concern": area_with_concern, "base_path": item_base_path}
        )


for item in area_with_concerns_and_path:
    print(item["area_with_concern"])
    # save input-trident.txt to item path
    # item path is base_path + area directory
    area_names = item["area_with_concern"].split(";")[0].replace("AreaWithConcern: ", "").split(", ")
    area_name_reversed = "/".join(reversed(area_names))
    item_path = os.path.join(item["base_path"], area_name_reversed)
    print(item_path)
    os.makedirs(item_path, exist_ok=True)
    with open(f"{item_path}/input-trident.txt", "w") as f:
        f.write(f"{item['area_with_concern']}\n")
