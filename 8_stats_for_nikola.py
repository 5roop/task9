# %%
mydatadir = "/data1/peterr/bilingual_data_for_ABClf"
outdir = "/data1/peterr/bilingual_data_for_ABClf_output/tsv"
import os
import pandas as pd
from ABClf import load_lexicon, get_variant, count_variants, counts_to_category
cols = "URL_en    URL_is    sent_en    sent_is    bleualign_score    paragraph_id_en    paragraph_id_is    deferred_hash_en    deferred_hash_is          bifixer_hash    bifixer_score    bicleaner_ai_score".split()
lex = load_lexicon()


import parse
def get_domain(url:str) -> str:
    pattern = "{protocol}://{domain}/{rest}"
    p = parse.compile(pattern)
    modified_pattern = "{protocol}://{domain}/"
    mp = parse.compile(modified_pattern)
    try:
        parse_result = p.parse(url)
        domain = parse_result["domain"]
    except TypeError:
        parse_result = mp.parse(url)
        domain = parse_result["domain"]
    return domain



import sys
import csv

csv.field_size_limit(131072<<4)


# %%

file = 'en-hr.deduped.txt'

lang = file[3:5]
print(lang)

endpath = os.path.join(
        outdir,
        file+".ABClf_output.txt",
    )
print(file)
df = pd.read_csv(
    os.path.join(
        mydatadir,
        file),
    sep="\t",
    engine="python",
    quoting=3,
    on_bad_lines="warn"
    )

df.columns = [col.replace("_is", f"_{lang}") for col in cols]
df["domain_en"] = df.URL_en.apply(get_domain)
df["domain_hr"] = df.URL_hr.apply(get_domain)

condition1 = df.domain_en == df.domain_en
condition2 = df.bicleaner_ai_score > 0.5

df = df[condition1 & condition2]

gb = df.groupby("domain_hr").count()["sent_en"]

# %%
gb.sort_values(ascending=False).to_csv("8_sentences_per_domain_en-hr.csv", sep="\t")



