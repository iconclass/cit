from openpyxl import load_workbook, Workbook
from jinja2 import Markup
from functools import partial
import sys
import json

TRANS_XLS_FILEPATH = "translations.xlsx"
TRANS_JSON_FILEPATH = "translations.json"
TRANS_DMP_FILEPATH = "translations.dmp"

texts = json.load(open(TRANS_JSON_FILEPATH))


def T(lang: str, token: str):
    return Markup(texts.get(token, {}).get(lang, ""))


def get_T(lang: str):
    return partial(T, lang)


if __name__ == "__main__":
    if sys.argv[1] == "write":
        by_id = json.load(open(TRANS_JSON_FILEPATH))

        with open(TRANS_DMP_FILEPATH, "w") as TDMP:
            for anid, item in by_id.items():
                TDMP.write(f"ID {anid}\n")
                for k, v in item.items():
                    vv = "\n ".join(v.split("\n"))
                    TDMP.write(f"{k} {vv}\n")
                TDMP.write("$\n")
    if sys.argv[1] == "read":
        by_id = {}
        wb = load_workbook(filename=TRANS_XLS_FILEPATH)
        sheet = wb.worksheets[0]
        for i, row in enumerate(sheet.rows):
            if i == 0:
                continue
            idx = row[0].value
            en = row[1].value
            if en:
                by_id.setdefault(idx, {})["en"] = en
            zh_hant = row[2].value
            if zh_hant:
                by_id.setdefault(idx, {})["zh_hant"] = zh_hant
            zh_hans = row[3].value
            if zh_hans:
                by_id.setdefault(idx, {})["zh_hans"] = zh_hans
        open(TRANS_JSON_FILEPATH, "w").write(json.dumps(by_id, indent=2))
