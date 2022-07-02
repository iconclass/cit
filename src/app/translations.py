from openpyxl import load_workbook, Workbook
from jinja2 import Markup
from functools import partial
import sys
import json

TRANS_XLS_FILEPATH = "translations.xlsx"
TRANS_JSON_FILEPATH = "translations.json"

texts = json.load(open(TRANS_JSON_FILEPATH))


def T(lang: str, token: str):
    return Markup(texts.get(token, {}).get(lang, ""))


def get_T(lang: str):
    return partial(T, lang)


if __name__ == "__main__":
    if sys.argv[1] == "write":
        by_id = json.load(open(TRANS_JSON_FILEPATH))

        workbook = Workbook()
        ws = workbook.active
        ws.cell(row=1, column=2, value="en")
        ws.cell(row=1, column=3, value="zh_hant")
        ws.cell(row=1, column=4, value="zh_hans")
        row = 2
        for id, by_lang in by_id.items():
            ws.cell(row=row, column=1, value=id)
            col = 2
            for lang in ("en", "zh_hant", "zh_hans"):
                ws.cell(row=row, column=col, value=by_lang.get(lang, ""))
                col += 1
            row += 1
        workbook.save(filename=TRANS_XLS_FILEPATH)
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
