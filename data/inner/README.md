# Inner layer pairs

Human utterance -> TRIDENT intermediate language. Built 2026-08-27/28 on the
mothership, 1000 seeds in 554 minutes.

| file | what it is |
|---|---|
| `generated-pairs.jsonl` | the generator's record. Every utterance it made, the reading, the query built from it, the element count, and a verdict |
| `generation.log` | the run that produced it |
| `train.jsonl` / `valid.jsonl` | the assembled pairs, split by hash of the utterance |
| `report.json` | what was kept, what was dropped, and why |

## How they were made

Backwards. Forward generation asks a model to invent utterances and hope they
describe something real; this starts from a validated pair in `data/concerns`
(an area and a concern that a working Overpass query already returns results
for), asks the 35B to write the human sentences that would lead to it, and
then checks each one by running it through the real inner and deep layers.

A pair is kept when the place the utterance names resolves to the place the
seed names, and the concern survives.

## The record's verdicts

| verdict | n | % |
|---|---:|---:|
| accepted | 5430 | 68.8 |
| invented_name | 745 | 9.4 |
| wrong_area | 714 | 9.0 |
| deep_gap | 622 | 7.9 |
| zero_results | 199 | 2.5 |
| no_area_line | 179 | 2.3 |

`zero_results` is a correct reading of a real place that OSM has no instance
of. `deep_gap` is a net for readings that drifted; 54% keep the concern.
`wrong_area` is a different place — Chuo-ku resolving to Tokyo when the seed
is Niigata — and is not a checker being too strict.

## What the training set does with them

`accepted` and `zero_results` are taken. `deep_gap` is taken when the concern
survived. The rest are dropped.

**The target is not the golden model's reply.** 41% of accepted rows name
fewer levels than the seed: `Higashi Ward, Niigata, Niigata Prefecture, Japan`
comes back as `Higashi-ku, Niigata`. Overpass still finds something, so the
verdict is accepted, but the seed is the validated form and the shortened one
is the weakness being trained out. The target carries the seed's area and
concern and keeps the model's title, emoji and colour.

The confirmation line is repaired rather than dropped where its language
drifted (1188 rows answer Japanese input in Korean, Chinese or English).

    uv run python src/build_inner_trainset.py data/inner/generated-pairs.jsonl

5875 pairs: 2482 Japanese, 3393 English, 2286 naming four levels.
