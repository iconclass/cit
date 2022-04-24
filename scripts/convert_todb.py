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


def extract_notations(obj):
    buf = []
    ID = obj.get("ID")[0]
    paths = set()
    for cit_id in obj.get("CIT_ID", []):
        buf.append((ID, cit_id, 1))
        cit_obj = objs.get(cit_id) or {}
        for cit_path in cit_obj.get("P", []):
            if cit_path != cit_id:
                paths.add(cit_path)
    for p in paths:
        buf.append((ID, p, 0))
    return buf


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
notations = []
for the_id, obj in objs.items():
    t1 = extract_texts(obj)
    t2 = add_term_test(obj)
    searchtxt_en[the_id] = t1 + t2
    notations.extend(extract_notations(obj))


db = sqlite3.connect("CIT.sqlite")
cursor = db.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS objs 
    (  id, obj, 
       type text AS (json_extract(obj, '$.TYPE[0]')),
       collection text as (json_extract(obj, '$.COL[0]'))
    )
    """
)
cursor.execute(
    "CREATE VIEW IF NOT EXISTS images AS SELECT * FROM objs WHERE type = 'image'"
)
cursor.execute(
    "CREATE VIEW IF NOT EXISTS terms AS SELECT * FROM objs WHERE type = 'CIT'"
)
cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS objs_id ON objs (id)")
cursor.execute("CREATE INDEX IF NOT EXISTS objs_type ON objs (type)")
cursor.execute("CREATE INDEX IF NOT EXISTS objs_collection ON objs (collection)")
cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS txt_idx USING fts5(id, text)")
cursor.execute("CREATE TABLE IF NOT EXISTS objs_cit (obj_id, cit_id, exact)")
cursor.execute("CREATE INDEX IF NOT EXISTS objs_cit_idx ON objs_cit (cit_id)")
batch = [(k, v) for k, v in searchtxt_en.items()]
cursor.executemany("INSERT INTO txt_idx VALUES (?, ?)", batch)
batch = [(k, json.dumps(v)) for k, v in objs.items()]
cursor.executemany("INSERT INTO objs VALUES (?, ?)", batch)
cursor.executemany("INSERT INTO objs_cit VALUES (?, ?, ?)", notations)
db.commit()
