# %%
mydatadir = "/data1/peterr/bilingual_data_for_ABClf/"
files_to_be_moved = ["/data1/lpla/macocu/permanent/bitextor-mt-output-en-mt-paragraph-and-loomchild-and-bicleanerai/en-mt.deduped.txt.gz",
"/data1/lpla/macocu/permanent/bitextor-mt-output-en-is-paragraph-and-loomchild-and-bicleanerai/en-is.deduped.txt.gz",
"/data1/lpla/macocu/permanent/bitextor-mt-output-en-tr-paragraph-and-loomchild-and-bicleanerai/en-tr.deduped.txt.gz",]
import os
for file in files_to_be_moved:
    os.system(f'rsync -e "ssh" -avz peterr@macocu-crawl2.ijs.si:{file} {mydatadir}')



# %%
