import hashlib
import httpx
import os
import sys

import ollama
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

print("")
print("")

base_path: str = sys.argv[1]
print("base_path:", base_path)

# if already saved, skip validation and save
save_path: str = os.path.join(base_path, "output-001.overpassql")
print("save_path:", save_path)
if os.path.exists(save_path):
    print("OverpassQL already saved!")
    sys.exit(0)

not_found_path: str = os.path.join(base_path, "not-found.txt")
if os.path.exists(not_found_path):
    print("not-found.txt exists!")
    sys.exit(0)

instruct_file_path: str = os.path.join(base_path, "input-trident.txt")
instruct: str = open(instruct_file_path).read().strip()
print("instruct:", instruct)

filter_type: str = instruct.split(":")[0].strip()
print("filter_type:", filter_type)

filter_concern: str = instruct.split("; ")[-1].strip()
print("filter_concern:", filter_concern)

# from "AreaWithConcern: Taito, Tokyo, Japan; Cafes" to extract Taito
filter_area: str = instruct.split("; ")[0].split(": ")[-1].split(", ")[0].strip()
print("filter_area:", filter_area)

embeddings = OllamaEmbeddings(
    model="nomic-embed-text:v1.5",
)
vectorstore = Chroma("langchain_store", embeddings)

example_selector = SemanticSimilarityExampleSelector(
    vectorstore=vectorstore,
    k=4,
)


def add_examples_from_dir(directory: str) -> None:
    filtered_area_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "input-trident.txt":
                input_txt = open(os.path.join(root, file)).read().strip()
                if not input_txt.startswith(filter_type):
                    continue
                # filter_areaは2個まで
                if filter_area in input_txt:
                    filtered_area_count += 1
                    if filtered_area_count > 2:
                        continue
                if filter_concern not in input_txt:
                    continue
                # search all output-*.overpassql files
                output_files = [f for f in files if f.startswith("output-") and f.endswith(".overpassql")]
                for output_file in output_files:
                    output_txt = open(os.path.join(root, output_file)).read().strip()
                    example: dict[str, str] = {
                        "input": input_txt,
                        "output": output_txt,
                    }
                    example_selector.add_example(example)


dir_path = "./data"
add_examples_from_dir(dir_path)


prompt_prefix = """\
You are an expert of OpenStreetMap and Overpass API. You output the best Overpass API query based on input text.

You will always reply according to the following rules:
- Output valid Overpass API query.
- The query timeout MUST be 30000.
- The query will utilize a area specifier as needed.
- The query will search nwr as needed.
- The query MUST be out geom.
- The query MUST be enclosed by three backticks on new lines, denoting that it is a code block.
- Respect examples with the utmost precision.
- Take utmost care with the Important note.

===
Examples:\
"""


example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="Input:\n{input}\n\nOutput:\n```\n{output}\n```",
)

prompt_template = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix=prompt_prefix,
    suffix="Input:\n{question}\n\nOutput:",
    input_variables=["question"],
)

question = f"{instruct}"
prompt: str = prompt_template.format(question=question)

response = ollama.generate(
    prompt=prompt,
    model="qwen2.5-coder:14b",
    options={
        "temperature": 0.01,
        "num_predict": 256,
    },
)

# extract the OverpassQL from the response
overpassql: str = response["response"].split("```")[1].strip()

print("Generated OverpassQL:")
print("===")
print(overpassql)
print("===")

# overpassql must be greater than 0 lines and less than 20 lines
if len(overpassql.split("\n")) == 0 or len(overpassql.split("\n")) > 20:
    print("OverpassQL is not valid!")
    sys.exit(1)

query_hash: str = hashlib.md5(overpassql.encode("utf-8")).hexdigest()
tmp_path: str = os.path.join("./tmp", query_hash)

# check OverpassQL already exists
if os.path.exists(os.path.join(tmp_path, "output-001.overpassql")):
    print("OverpassQL already exists!")
    sys.exit(0)


OVERPASS_API_ENDPOINT = "https://overpass.yuiseki.net/api/interpreter"


def get_number_of_elements(query: str) -> int:
    params = {"data": query}
    try:
        resp = httpx.get(OVERPASS_API_ENDPOINT, params=params, timeout=None)
        response_json = resp.json()
        return int(len(response_json["elements"]))
    except Exception as e:
        print("Error:", e)
        return 0


number_of_elements: int = get_number_of_elements(overpassql)

print("number of elements:", number_of_elements)

if 0 < number_of_elements:
    os.makedirs(tmp_path, exist_ok=True)
    with open(os.path.join(tmp_path, "output-001.overpassql"), "w") as f:
        f.write(overpassql + "\n")
    os.makedirs(base_path, exist_ok=True)
    # output the OverpassQL to a file to ./tmp
    with open(save_path, "w") as f:
        f.write(overpassql + "\n")
    print(save_path)
else:
    # save not_found.txt
    with open(not_found_path, "w") as f:
        f.write("")
    print(not_found_path)


print("")
print("")
