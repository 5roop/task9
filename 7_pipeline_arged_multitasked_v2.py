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

print("Starting the pipeline.")

import sys
file = sys.argv[1]
# for file in [
# '/data1/peterr/bilingual_data_for_ABClf/en-mk.deduped.txt',  '/data1/peterr/bilingual_data_for_ABClf/en-bg.deduped.txt',
# '/data1/peterr/bilingual_data_for_ABClf/en-is.deduped.txt',  '/data1/peterr/bilingual_data_for_ABClf/en-hr.deduped.txt',
# '/data1/peterr/bilingual_data_for_ABClf/en-mt.deduped.txt',  '/data1/peterr/bilingual_data_for_ABClf/en-tr.deduped.txt',
# '/data1/peterr/bilingual_data_for_ABClf/en-sl.deduped.txt'
# ]:
# file = "en-mk.deduped.txt"
for file in [file]:
    print("Whooo, working on file", file)
    if not file.endswith(".txt"):
        continue
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
        on_bad_lines="warn",
        ).dropna()
    
    df.columns = [col.replace("_is", f"_{lang}") for col in cols]


    s = df.groupby("URL_en")["sent_en"].apply(" ".join)
    ndf = pd.DataFrame(s)
    ndf["en_document_level_variant"] = ndf.sent_en.apply(lambda s: get_variant(s, lex=lex))
    ndf["per_token_unbalanced"] = ndf.sent_en.apply(lambda s: count_variants(s, lex)[1])
    ndf["domain_en"] = [get_domain(url) for url in ndf.index.values]
    ndf["URL_en"] = ndf.index
    print("Document grouping done, merging")
    df = pd.merge(
            df,
            ndf[['en_document_level_variant', 'per_token_unbalanced', 'domain_en',]],
            how="left",
            left_on="URL_en",
            right_index=True,
            sort=False,
            suffixes=("_x", "_y"),
            copy=True,
            indicator=False,
            validate=None,
            )
    del ndf
    df["en_domain_level_variant"] = "UNK"
    counts = df.domain_en.value_counts()
    suitable_domains = counts[counts >= 3].index.values
    l = len(suitable_domains)
    pruned_df = df.loc[:, ["per_token_unbalanced", "domain_en"]].copy()
    def get_variant(domain):
        subset = pruned_df.loc[pruned_df.domain_en == domain, :]
        d = dict()
        for line in subset.per_token_unbalanced.values:
            if not line:
                continue
            for word, payload in line.items():
                variant, count = payload.get("variant"), payload.get("count")
                d[variant] = d.get(variant, 0) + 1
        variant = counts_to_category(d)
        return variant
    
    print("Ok, assigning variants...")
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=60) as executor:
        variants = list(executor.map(get_variant, suitable_domains))
    for domain, variant in zip(suitable_domains, variants):
        df.loc[df.domain_en == domain, "en_domain_level_variant"] = variant
    print("Variant assigned, saving to ", endpath)
    df = df.drop(columns="per_token_unbalanced")
    df.to_csv(
        endpath,
        index=False,
        sep="\t"
    )

