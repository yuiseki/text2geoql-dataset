"""Generate and validate Overpass QL queries from TRIDENT input files using LLM."""

import hashlib
import os
import sys

import ollama
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

from trident import parse_filter_type, parse_filter_concern, parse_filter_area
from overpass import count_elements

OLLAMA_MODEL = "qwen2.5-coder:14b"
EMBED_MODEL = "nomic-embed-text:v1.5"
MAX_QUERY_LINES = 20

PROMPT_PREFIX = """\
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


def load_examples_for_instruct(
    data_dir: str,
    filter_type: str,
    filter_concern: str,
    filter_area: str,
    example_selector: SemanticSimilarityExampleSelector,
    max_area_examples: int = 2,
) -> None:
    """Walk data_dir and add matching examples to the example_selector."""
    filtered_area_count = 0
    for root, dirs, files in os.walk(data_dir):
        if "input-trident.txt" not in files:
            continue
        input_txt = open(os.path.join(root, "input-trident.txt")).read().strip()
        if not input_txt.startswith(filter_type):
            continue
        if filter_area in input_txt:
            filtered_area_count += 1
            if filtered_area_count > max_area_examples:
                continue
        if filter_concern not in input_txt:
            continue
        output_files = [f for f in files if f.startswith("output-") and f.endswith(".overpassql")]
        for output_file in output_files:
            output_txt = open(os.path.join(root, output_file)).read().strip()
            example: dict[str, str] = {"input": input_txt, "output": output_txt}
            example_selector.add_example(example)


def build_prompt(instruct: str, data_dir: str) -> str:
    """Build a few-shot prompt for the given TRIDENT instruction."""
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    vectorstore = Chroma("langchain_store", embeddings)
    example_selector = SemanticSimilarityExampleSelector(vectorstore=vectorstore, k=4)

    load_examples_for_instruct(
        data_dir=data_dir,
        filter_type=parse_filter_type(instruct),
        filter_concern=parse_filter_concern(instruct),
        filter_area=parse_filter_area(instruct),
        example_selector=example_selector,
    )

    example_prompt = PromptTemplate(
        input_variables=["input", "output"],
        template="Input:\n{input}\n\nOutput:\n```\n{output}\n```",
    )
    prompt_template = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix=PROMPT_PREFIX,
        suffix="Input:\n{question}\n\nOutput:",
        input_variables=["question"],
    )
    return prompt_template.format(question=instruct)


def generate_overpassql(prompt: str, model: str = OLLAMA_MODEL) -> str | None:
    """Call LLM and extract the OverpassQL code block from the response.

    Returns None if no valid code block is found or line count exceeds limit.
    """
    response = ollama.generate(
        prompt=prompt,
        model=model,
        options={"temperature": 0.01, "num_predict": 256},
    )
    parts = response["response"].split("```")
    if len(parts) < 2:
        return None
    overpassql = parts[1].strip()
    lines = overpassql.split("\n")
    if len(lines) == 0 or len(lines) > MAX_QUERY_LINES:
        return None
    return overpassql


def save_overpassql(overpassql: str, base_path: str, tmp_root: str = "./tmp") -> None:
    """Save validated OverpassQL to base_path and tmp dedup store."""
    query_hash = hashlib.md5(overpassql.encode("utf-8")).hexdigest()
    tmp_path = os.path.join(tmp_root, query_hash)
    os.makedirs(tmp_path, exist_ok=True)
    with open(os.path.join(tmp_path, "output-001.overpassql"), "w") as f:
        f.write(overpassql + "\n")
    os.makedirs(base_path, exist_ok=True)
    save_path = os.path.join(base_path, "output-001.overpassql")
    with open(save_path, "w") as f:
        f.write(overpassql + "\n")


def run(base_path: str, data_dir: str = "./data", tmp_root: str = "./tmp", model: str = OLLAMA_MODEL) -> None:
    """Main generation pipeline for a single TRIDENT directory."""
    print("")
    print("base_path:", base_path)

    save_path = os.path.join(base_path, "output-001.overpassql")
    if os.path.exists(save_path):
        print("OverpassQL already saved!")
        return

    not_found_path = os.path.join(base_path, "not-found.txt")
    if os.path.exists(not_found_path):
        print("not-found.txt exists!")
        return

    instruct_file_path = os.path.join(base_path, "input-trident.txt")
    instruct = open(instruct_file_path).read().strip()
    print("instruct:", instruct)

    query_hash_tmp = hashlib.md5(b"").hexdigest()  # placeholder until we have the query
    prompt = build_prompt(instruct, data_dir)
    overpassql = generate_overpassql(prompt, model=model)

    if overpassql is None:
        print("OverpassQL is not valid!")
        with open(not_found_path, "w") as f:
            f.write("")
        return

    print("Generated OverpassQL:\n===")
    print(overpassql)
    print("===")

    query_hash_tmp = hashlib.md5(overpassql.encode("utf-8")).hexdigest()
    tmp_path = os.path.join(tmp_root, query_hash_tmp)
    if os.path.exists(os.path.join(tmp_path, "output-001.overpassql")):
        print("OverpassQL already exists!")
        return

    n = count_elements(overpassql)
    print("number of elements:", n)

    if n > 0:
        save_overpassql(overpassql, base_path, tmp_root)
        print(save_path)
    else:
        with open(not_found_path, "w") as f:
            f.write("")
        print(not_found_path)


if __name__ == "__main__":
    run(base_path=sys.argv[1])
