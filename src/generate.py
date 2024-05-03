import os
import sys
import ollama
from langchain_chroma import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.example_selectors.ngram_overlap import (
    ngram_overlap_score,
    NGramOverlapExampleSelector,
)

embeddings = OllamaEmbeddings(
    model="all-minilm:l6-v2",
)
vectorstore = Chroma("langchain_store", embeddings)

example_selector = SemanticSimilarityExampleSelector(
    vectorstore=vectorstore,
    k=4,
)


def add_examples_from_dir(directory):
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
                    example = {
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

===
Examples:
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

arg = sys.argv[1]
question = f"AreaWithConcern: {arg}"
prompt = prompt_template.format(question=question)

response = ollama.generate(model='phi3:3.8b',
                           prompt=prompt,
                           options={
                               'temperature': 0.01,
                               'num_predict': 256,
                           })

print(response['response'])
