# task9
Evaluating ABClf on all bilingual data

I prepared uncompressed .txt files here: `/data1/peterr/bilingual_data_for_ABClf` (Crawl 1). For now I'll look at these and not expand the analysis to Crawl2.

The .txt files have the same schema as the ones I've studied previously, which is nice. MK file raises some questions.

## Temporal complexity
For sl dataset I needed 12 minutes to parse 595067 documents.
## First results
|variant|ratio   |
|-------|--------|
|UNK    |0.699891|
|B      |0.173767|
|A      |0.103519|
|MIX    |0.022823|