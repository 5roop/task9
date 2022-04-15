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

MK language is the only file to not parse correctly. I solved that by limiting the number of rows I read.

I moved the rest of the files to crawl1 and continued.

## Parser error:
en-mk and en-mt had problems. I tried converting the tmx files to txt, but the problems persisted. I capped the rows of en-mk to 1200000 and of en-mt to 2514881. Didn't work.




 /data1/lpla/macocu/permanent/bitextor-mt-output-en-mk-paragraph-and-loomchild-and-bicleanerai/en-mk.deduped.tmx.gz
 /data1/lpla/macocu/permanent/bitextor-mt-output-en-bg-paragraph-and-loomchild-and-bicleanerai/
 /data1/lpla/macocu/permanent/bitextor-mt-output-en-hr-paragraph-and-loomchild-and-bicleanerai/
 /data1/lpla/macocu/permanent/bitextor-mt-output-en-sl-paragraph-and-loomchild-and-bicleanerai/

 for lang in {mk,bg,hr,sl};
 do
cp "/data1/lpla/macocu/permanent/bitextor-mt-output-en-$lang-paragraph-and-loomchild-and-bicleanerai/en-$lang.deduped.tmx.gz" "/data1/peterr/bilingual_data_for_ABClf/en-$lang.deduped.tmx.gz";
 done;

 # Update
It turned out that only turkish had problems with the parsing that I could not repair. The main problem was with fields being too long. I can partially fix that, but not without rendering the processing perversely long. I increased the field maximum length until the code would run without problems.


# Meeting notes - Nikola

* https://github.com/macocu/crawling-documentation : document the pipeline for posterity and reproducibility
* for {en-mk,en-sl} calculate domain level predictions in two ways: from the doc level input and from the doc level predictions, produce a table `domain|counts|domain-level-prediction-1|domain-level-prediction-2`
* check the data a bit. A lot of the pairs are wonky.


# Meeting notes:
Prepare a overview for Taja:
for en-sl pair:
    for instances where bicleaner score > 0.5 and domain_en == domain_other:
        count number of instances in a specific domain and generate a list for Taja