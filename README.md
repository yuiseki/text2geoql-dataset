# `text2geoql`

- I have defined a natural language processing task named `text2geoql` and am in the process of building a dataset for it
- `text2geoql` is a task that translates arbitrary natural language into reasonable `geoql` based on the intent
- `geoql` is an abbreviation for "Geospatial data query languages"
  - Off course, `geoql` contains `overpassql`

## `text2geoql-dataset`
- https://github.com/yuiseki/text2geoql-dataset
  - This repository publishes over 1000 Overpass QLs that are paired with the `TRIDENT intermediate language`
  - These Overpass QLs, except for the original 100 Overpass QLs, were automatically generated by TinyDolphin, an very tiny LLM fine-tuned from TinyLlama
    - https://huggingface.co/cognitivecomputations/TinyDolphin-2.8-1.1b
  - These Overpass QLs have been verified to send actual requests to the Overpass API and obtain correct results
- This dataset is may be the first ever `synthetic dataset` generated by LLM in the field of GIS
