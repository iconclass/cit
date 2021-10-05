import textbase
import sqlite3
import json

CIT = textbase.parse("CIT.dmp")

objs = {}

for term in CIT:
    obj = {}
    for k in ("N", "P", "C"):
        if k not in term:
            continue
        obj[k.lower()] = term[k]
    obj["txt"] = {}
    if "TERM_EN" in term:
        obj["txt"]["en"] = term.get("TERM_EN")[0]
    if "TERM_ZH" in term:
        obj["txt"]["zh"] = term.get("TERM_ZH")[0]
    if "TERM_PINYIN" in term:
        obj["txt"]["pinyin"] = term.get("TERM_PINYIN")[0]
    if "KW_ZH" in term:
        obj.setdefault("kw", {})["zh"] = term["KW_ZH"]
    if "KW_EN" in term:
        obj.setdefault("kw", {})["en"] = term["KW_EN"]
    obj["n"] = term["CIT"][0]
    objs[obj["n"]] = obj

# But it would also be good to write out the entries to a sqlite db, so that we can easily query them.
db = sqlite3.connect("CIT.sqlite3")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS terms (term, termzh, obj)")
cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS terms_term ON terms (term)")
cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS terms_termzh ON terms (termzh)")
cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS term_search USING fts5(term, text)")
cursor.execute("DELETE FROM terms")
batch = [(k, v["txt"]["zh"], json.dumps(v)) for k, v in objs.items()]
cursor.executemany("INSERT INTO terms VALUES (?, ?, ?)", batch)
cursor.execute
db.commit()

