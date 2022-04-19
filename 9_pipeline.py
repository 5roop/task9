# %%

import argparse

parser = argparse.ArgumentParser(
    description="Pipeline for assigning domain- and document- level english variant"
)
parser.add_argument(
    "-i",
    "--inputfile",
    required=True,
    help="Full path to input file (txt format). Expects filename like en-{lang}.dedup.txt",
)
parser.add_argument(
    "-o", "--outfile", required=True, help="Full path to desired output file."
)
parser.add_argument(
    "-p",
    "--processes",
    required=False,
    default=1,
    type=int,
    help="How many processes to use. If 0, use aggregation instead of recalculation (faster).",
)

args = parser.parse_args()

import os
import logging

logging.basicConfig(level=logging.DEBUG)
outdir = os.path.dirname(args.outfile)
file = os.path.basename(args.inputfile)

try:
    from ABClf import load_lexicon, get_variant, count_variants, counts_to_category
except Exception as e:
    os.system("wget https://raw.githubusercontent.com/5roop/task9/main/ABClf.py")
    os.system("wget https://raw.githubusercontent.com/5roop/task9/main/lexicon.pickle")
    from ABClf import load_lexicon, get_variant, count_variants, counts_to_category
except:
    logging.error("Encountered problems with importing ABCLf.py and lexicon.pickle.")


import pandas as pd

cols = "URL_en    URL_is    sent_en    sent_is    bleualign_score    paragraph_id_en    paragraph_id_is    deferred_hash_en    deferred_hash_is          bifixer_hash    bifixer_score    bicleaner_ai_score".split()
lex = load_lexicon()

if not os.path.exists(outdir):
    os.mkdir(outdir)

import parse


def get_domain(url: str) -> str:
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

csv.field_size_limit(131072 << 4)


p = parse.compile("en-{lang}.deduped.txt")
parse_results = p.parse(file)
lang = parse_results["lang"]
if not lang:
    logging.error("Got nonstandard input filename, could not infer language!")
logging.info(f"Identified second language: {lang}")


endpath = os.path.join(
    outdir,
    file.replace(".txt", ".ABClf_output.txt"),
)
logging.info("Reading file " + file)
df = pd.read_csv(
    args.inputfile,
    sep="\t",
    engine="python",
    quoting=3,
    header=None,
    on_bad_lines="warn",
).dropna()

df.columns = [col.replace("_is", f"_{lang}") for col in cols]


s = df.groupby("URL_en")["sent_en"].apply(" ".join)
ndf = pd.DataFrame(s)
ndf["en_document_level_variant"] = ndf.sent_en.apply(lambda s: get_variant(s, lex=lex))
ndf["per_token_unbalanced"] = ndf.sent_en.apply(lambda s: count_variants(s, lex)[1])
ndf["domain_en"] = [get_domain(url) for url in ndf.index.values]
ndf["URL_en"] = ndf.index
logging.info("Finished assigning document level variants. Merging...")
df = pd.merge(
    df,
    ndf[
        [
            "en_document_level_variant",
            "per_token_unbalanced",
            "domain_en",
        ]
    ],
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


logging.info("Ok, assigning variants...")
l = len(suitable_domains)
logging.info(f"Nr of domains to process: {l}")


if args.processes > 0:
    logging.info(f"Using multiprocessing with {args.processes} max workers.")
    logging.info(
        "Domain-level variant will be done by reassessing all significant words."
    )
    from concurrent.futures import ProcessPoolExecutor

    with ProcessPoolExecutor(max_workers=args.processes) as executor:
        variants = list(executor.map(get_variant, suitable_domains))
    logging.info("Calculation finished. Assigning.")
    for domain, variant in zip(suitable_domains, variants):
        df.loc[df.domain_en == domain, "en_domain_level_variant"] = variant
    logging.info("Variant assigned, saving to ", endpath)
if args.processes == 0:
    logging.info("Aggregating document-level results...")
    gb = df.groupby("domain_en").en_document_level_variant.agg(
        lambda x: pd.Series.mode(x).iloc[0]
    )
    df = pd.merge(
        df,
        gb,
        how="left",
        left_on="domain_en",
        right_index=True,
        sort=False,
    )
    df["en_document_level_variant"] = df.en_document_level_variant_y
    df = df.drop(columns=["en_document_level_variant_y", "en_document_level_variant_x"])
logging.info(f"Variant assigned, saving to {endpath}")
df = df.drop(columns="per_token_unbalanced")
df.to_csv(endpath, index=False, sep="\t")
