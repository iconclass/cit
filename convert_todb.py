import textbase
import sqlite3
import json
import sys


def add_term_test(obj):
    txtbuf = []
    for cit_id in obj.get("CIT_ID", []):
        cit_obj = objs.get(cit_id, {})
        txtbuf.append("\n")
        txtbuf.append(extract_texts(cit_obj))
        for cit_obj_p in cit_obj.get("P", []):
            cit_obj_p_obj = objs.get(cit_obj_p, {})
            txtbuf.append("\n")
            txtbuf.append(extract_texts(cit_obj_p_obj))
    return "\n".join(txtbuf)


def extract_texts(obj):
    # We also want the ZH texts to be matched with the unbicode searcher as seprate ideograms
    zh_fieldnames = ["TERM_ZH", "KW_ZH"]
    txtbuf = []
    for k, kk in obj.items():
        if len(kk) > 0:
            kk = "\t".join(kk)
            txtbuf.append(f"{k} {kk}")
            if k in zh_fieldnames:
                kkk = [" ".join(ideo.split()) for ideo in kk]
                txtbuf.append(f"{kkk}")

    return "\n".join(txtbuf)


def read_dmp(filename):
    objs = {}
    for obj in textbase.parse(filename):
        the_id = obj.get("ID", [None])[0]
        if the_id:
            # make sure all the fieldnames are uppercase and do not have dots
            tmp = {}
            for k, v in obj.items():
                tmp[k.upper().replace(".", "_")] = v
            objs[the_id] = tmp
    return objs


objs = {}
for filename in sys.argv[1:]:
    for k, v in read_dmp(filename).items():
        objs[k] = v

searchtxt_en = {}
for the_id, obj in objs.items():
    t1 = extract_texts(obj)
    t2 = add_term_test(obj)
    searchtxt_en[the_id] = t1 + t2

db = sqlite3.connect("CIT.sqlite")
cursor = db.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS objs (id, obj)")
cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS objs_id ON objs (id)")
cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS txt_idx USING fts5(id, text)")
batch = [(k, v) for k, v in searchtxt_en.items()]
cursor.executemany("INSERT INTO txt_idx VALUES (?, ?)", batch)
batch = [(k, json.dumps(v)) for k, v in objs.items()]
cursor.executemany("INSERT INTO objs VALUES (?, ?)", batch)
db.commit()


# "CREATE INDEX IF NOT EXISTS objs_cit ON objs ( json_extract(obj, '$.CIT_ID') COLLATE NOCASE )"
