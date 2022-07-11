from openpyxl import load_workbook, Workbook
from jinja2 import Markup
from functools import partial
import sys
import json
import textbase

TRANS_DMP_FILEPATH = "translations.dmp"

texts = {}

for x in textbase.parse(TRANS_DMP_FILEPATH):
    anid = x.get("ID", [None])[0]
    if anid:
        texts[anid] = {}
        for k, v in x.items():
            texts[anid][k] = v[0]


def T(lang: str, token: str):
    return Markup(texts.get(token, {}).get(lang, ""))


def get_T(lang: str):
    return partial(T, lang)
