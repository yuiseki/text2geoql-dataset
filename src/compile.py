import datasets
import os
import sys

# Collect input-*.txt files and output-*.overpassql files in ./data/**/* directory recursively
# input-trident.txt files must be one
# input-en-001.txt files may be multiple
# output-001.overpassql files may be multiple

# list of dict of files
# dict keys
# - input
# - input_type (en or trident)
# - output
# - output_type (overpassql)
# input and output are must be paired by directory
# input and output are must be content of files, not path of files
text2geoql_dict_list = []


def collect_text2geoql_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "input-trident.txt":
                input_txt = open(os.path.join(root, file), "r").read().strip()
                # search all output-*.overpassql files
                output_files = [
                    f for f in files if f.startswith("output-") and f.endswith(".overpassql")
                ]
                for output_file in output_files:
                    output_txt = open(os.path.join(
                        root, output_file), "r").read().strip()
                    text2geoql_dict = {
                        "input": input_txt,
                        "input_type": "trident",
                        "output": output_txt,
                        "output_type": "overpassql"
                    }
                    text2geoql_dict_list.append(text2geoql_dict)


dir_path = "./data"

collect_text2geoql_files(dir_path)


my_dataset = datasets.Dataset.from_list(text2geoql_dict_list)

print(my_dataset)
