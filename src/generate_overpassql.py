"""Generate and validate Overpass QL queries from TRIDENT input files using LLM."""

import hashlib
import os
import sys

import ollama
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

from meta import GenerationMeta, FailureMeta, model_to_slug
from overpass import fetch_elements
from trident import parse_filter_type, parse_filter_concern, parse_filter_area

OLLAMA_MODEL = "qwen2.5-coder:14b"
EMBED_MODEL = "nomic-embed-text:v1.5"
MAX_QUERY_LINES = 20
DEFAULT_TEMPERATURE = 0.01
DEFAULT_NUM_PREDICT = 256
DEFAULT_NUM_PREDICT_THINKING = 2048  # thinking consumes tokens before response

# Models that enable thinking by default when think=None
_REASONING_FAMILIES = ("qwen3", "qwen3.5")


def default_num_predict(model: str, think: bool | None = None) -> int:
    """Return a safe num_predict default for the given model and think setting.

    When think=True (or think=None for reasoning model families), thinking
    tokens are consumed before any response appears, requiring a larger budget.
    """
    is_reasoning_model = any(model.startswith(f) for f in _REASONING_FAMILIES)
    thinking_active = think is True or (think is None and is_reasoning_model)
    if thinking_active:
        return DEFAULT_NUM_PREDICT_THINKING
    return DEFAULT_NUM_PREDICT

PROMPT_PREFIX = """\
You are an expert of OpenStreetMap and Overpass API. You output the best Overpass API query based on input text.

You will always reply according to the following rules:
- Output valid Overpass API query.
- The query timeout MUST be 30.
- The query will utilize a area specifier as needed.
- The query will search nwr as needed.
- The query MUST be out geom.
- The query MUST be enclosed by three backticks on new lines, denoting that it is a code block.
- Respect examples with the utmost precision.
- Take utmost care with the Important note.

===
Examples:\
"""


def example_matches(
    input_txt: str,
    filter_type: str,
    filter_concern: str,
) -> bool:
    """Return True if input_txt is a valid Few-Shot example for the given filters.

    Concern matching is case-insensitive to handle capitalisation variants
    (e.g. 'Convenience Stores' vs 'Convenience stores').

    >>> example_matches("AreaWithConcern: Taito, Tokyo, Japan; Cafes", "AreaWithConcern", "Cafes")
    True
    >>> example_matches("AreaWithConcern: Taito, Tokyo, Japan; Convenience stores", "AreaWithConcern", "Convenience Stores")
    True
    >>> example_matches("AreaWithConcern: Taito, Tokyo, Japan; Cafes", "AreaWithConcern", "Hotels")
    False
    >>> example_matches("Area: Taito, Tokyo, Japan", "AreaWithConcern", "Cafes")
    False
    """
    if not input_txt.startswith(filter_type):
        return False
    if filter_concern.lower() not in input_txt.lower():
        return False
    return True


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
        if not example_matches(input_txt, filter_type, filter_concern):
            continue
        if filter_area in input_txt:
            filtered_area_count += 1
            if filtered_area_count > max_area_examples:
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


def generate_overpassql(
    prompt: str,
    model: str = OLLAMA_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    num_predict: int = DEFAULT_NUM_PREDICT,
    think: bool | None = None,
) -> tuple[str | None, str]:
    """Call LLM and extract the OverpassQL code block from the response.

    Returns (query, failure_reason) where query is None on failure.
    failure_reason is one of: "no_code_block", "too_many_lines", "" (success).

    think: pass False to disable chain-of-thought for models that support it
           (e.g. qwen3, qwen3.5). None means use the model default.
    """
    options: dict = {"temperature": temperature, "num_predict": num_predict}
    response = ollama.generate(
        prompt=prompt,
        model=model,
        think=think,
        options=options,
    )
    parts = response["response"].split("```")
    if len(parts) < 2:
        return None, "no_code_block"
    overpassql = parts[1].strip()
    lines = overpassql.split("\n")
    if len(lines) == 0 or len(lines) > MAX_QUERY_LINES:
        return None, "too_many_lines"
    return overpassql, ""


def save_overpassql(
    overpassql: str,
    base_path: str,
    meta: GenerationMeta,
    tmp_root: str = "./tmp",
) -> str:
    """Save validated OverpassQL and its provenance metadata. Returns save_path."""
    slug = meta.model_slug
    query_hash = hashlib.md5(overpassql.encode("utf-8")).hexdigest()
    tmp_path = os.path.join(tmp_root, query_hash)
    os.makedirs(tmp_path, exist_ok=True)
    with open(os.path.join(tmp_path, f"output-{slug}.overpassql"), "w") as f:
        f.write(overpassql + "\n")

    os.makedirs(base_path, exist_ok=True)
    save_path = os.path.join(base_path, f"output-{slug}.overpassql")
    with open(save_path, "w") as f:
        f.write(overpassql + "\n")

    meta_path = os.path.join(base_path, f"output-{slug}.meta.json")
    meta.save(meta_path)

    return save_path


def run(
    base_path: str,
    data_dir: str = "./data",
    tmp_root: str = "./tmp",
    model: str = OLLAMA_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    num_predict: int = DEFAULT_NUM_PREDICT,
) -> None:
    """Main generation pipeline for a single TRIDENT directory."""
    slug = model_to_slug(model)
    print("")
    print(f"base_path: {base_path}  model: {model}")

    save_path = os.path.join(base_path, f"output-{slug}.overpassql")
    if os.path.exists(save_path):
        print("OverpassQL already saved!")
        return

    not_found_path = os.path.join(base_path, f"not-found-{slug}.json")
    if os.path.exists(not_found_path):
        print("not-found already recorded!")
        return

    # Legacy compat: honour old not-found.txt
    if os.path.exists(os.path.join(base_path, "not-found.txt")):
        print("Legacy not-found.txt exists — skipping.")
        return

    instruct_file_path = os.path.join(base_path, "input-trident.txt")
    instruct = open(instruct_file_path).read().strip()
    print("instruct:", instruct)

    prompt = build_prompt(instruct, data_dir)
    overpassql, failure_reason = generate_overpassql(
        prompt, model=model, temperature=temperature, num_predict=num_predict
    )

    if overpassql is None:
        print(f"LLM generation failed: {failure_reason}")
        FailureMeta.create(model=model, reason=failure_reason, query=None).save(not_found_path)  # type: ignore[arg-type]
        return

    print("Generated OverpassQL:\n===")
    print(overpassql)
    print("===")

    query_hash = hashlib.md5(overpassql.encode("utf-8")).hexdigest()
    tmp_path = os.path.join(tmp_root, query_hash)
    if os.path.exists(os.path.join(tmp_path, f"output-{slug}.overpassql")):
        print("OverpassQL already exists in tmp!")
        return

    try:
        elements = fetch_elements(overpassql)
        n = len(elements)
    except Exception as e:
        print(f"Overpass API error: {e}")
        FailureMeta.create(model=model, reason="api_error", query=overpassql).save(not_found_path)
        return

    print("number of elements:", n)

    if n > 0:
        meta = GenerationMeta.create(
            model=model,
            temperature=temperature,
            num_predict=num_predict,
            element_count=n,
        )
        saved = save_overpassql(overpassql, base_path, meta, tmp_root)
        print(saved)
    else:
        FailureMeta.create(model=model, reason="zero_results", query=overpassql).save(not_found_path)
        print(not_found_path)


if __name__ == "__main__":
    run(base_path=sys.argv[1])
