#/usr/bin/env python

import os
import html
from operator import methodcaller

from bs4 import BeautifulSoup
from lingua import LanguageDetectorBuilder, Language
from tqdm import tqdm

import cafs
from trace_attrs import lang


if __name__ == '__main__':
    det = LanguageDetectorBuilder.from_all_spoken_languages().build()
    cafs_records = cafs.walk()
    for cafs_record in tqdm(cafs_records, total=2880737):
        cid = os.path.basename(cafs_record)
        record = cafs.get(cid)
        html_source = methodcaller('get', 'description')(record)
        if html_source is None:
            continue
        unescaped_source = html.unescape(html_source)
        soup = BeautifulSoup(unescaped_source, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()    
        clean_text = soup.get_text(separator=" ", strip=True)
        detected_language = det.detect_language_of(clean_text)
        if detected_language is None:
            continue
        lang.put(detected_language.name, cid)
    lang.build()
    pass
