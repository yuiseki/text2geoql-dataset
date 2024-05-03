import hashlib
import os
import sys
import ollama
from langchain_chroma import Chroma
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.example_selectors import SemanticSimilarityExampleSelector

embeddings = OllamaEmbeddings(
    model="all-minilm:l6-v2",
)
vectorstore = Chroma("langchain_store", embeddings)

example_selector = SemanticSimilarityExampleSelector(
    vectorstore=vectorstore,
    k=10,
)


def add_examples_from_dir(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "input-trident.txt":
                input_txt = open(os.path.join(root, file), "r").read().strip()
                # get only "Area:"
                if input_txt.startswith("Area:"):
                    example = {
                        "input": "- "+input_txt,
                    }
                    example_selector.add_example(example)


dir_path = "./data"
add_examples_from_dir(dir_path)

example_prompt = PromptTemplate(
    input_variables=["input"],
    template="{input}",
)

prompt_prefix = """\
You output list of domain-specific language to retrieve information about a specific region.

You will always reply according to the following rules:
- Output MUST be start with Area:.
- Output MUST be multi-line, markdown formatted list.

===
Examples:\
"""

dynamic_prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix=prompt_prefix,
    suffix="===\nRequested Area:\n{instruction}\n\nOutput:",
    input_variables=["instruction"],
)

instruct = sys.argv[1]
prompt = dynamic_prompt.format(instruction=instruct)

print(prompt)

response = ollama.generate(
    prompt=prompt,
    model='tinydolphin:1.1b',
    # model='tinyllama:1.1b',
    # model='phi3:3.8b',
    options={
        'temperature': 0.01,
        'num_predict': 64,
    })

print(response['response'])
