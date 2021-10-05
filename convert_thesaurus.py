import sys
import xml.etree.ElementTree as ET
import json


def getpath(obj):
    parent = obj.get("broader")
    if parent:
        for p in getpath(data.get(parent)):
            yield p
        yield data.get(parent)


def gettit(elem, xpath, dest, field):
    d = elem.find(xpath)
    if d is not None:
        dest[field] = d.text


# Note, parsing file: CIT export_inOrder_04.03.2019.xml 20190312 gives error in XML on lines 781763 and 781765 encountering character  '\x02' embedded in file.
# Looks like all the source have this so do a search and replace to fix it.
filecontents = open("CIT.xml", encoding="utf8").read().replace("\x02", "")
doc = ET.fromstring(filecontents)

data = {}
seq = 0
for entry in doc.findall(".//mus_ixthes"):
    seq += 1
    tmp = {"seq": seq}
    tmp["n"] = entry.find(".//mus_auth_thes_term").text
    gettit(entry, "mus_auth_thes_b_term", tmp, "broader")
    gettit(entry, "mus_auth_thes_term_discrim", tmp, "discrim")
    # For now, we are going to ignore the scopenote and source again
    # Until further notice from Hongxing
    # gettit(entry, "mus_auth_thes_scope_note", tmp, "scopenote")
    # gettit(entry, "mus_auth_thes_source", tmp, "source")
    gettit(entry, "sys_id", tmp, "ID.INV")

    # Retrieve the related terms
    related = [r_term.text for r_term in entry.findall(".//mus_auth_thes_r_terms/_")]
    if related:
        tmp["r"] = related

    # Get the Chinese use_for
    tmp["kw_zh"] = [
        use_for.text for use_for in entry.findall(".//mus_auth_thes_use_for/_")
    ]

    # Find the _ elements under mus_auth_thes_a_terms_alias to extract the English display terms
    terms_alias = entry.find(".//mus_auth_thes_a_terms_alias")
    if terms_alias is None:
        continue

    for term in terms_alias.findall(".//_"):
        term_type = term.find(".//mus_auth_thes_a_terms_type_val")
        if term_type is None:
            continue
        term_val = term.find(".//mus_auth_thes_a_terms")
        if term_val is None:
            continue

        if not term_type.text:
            continue
        if term_type.text == "English display term":
            tmp.setdefault("term_en", []).append(term_val.text)
        elif term_type.text.startswith("English"):
            tmp.setdefault("kw_en", []).append(term_val.text)
        elif term_type.text == "Pinyin":
            tmp.setdefault("term_pinyin", []).append(term_val.text)
        else:
            tmp.setdefault("kw_zh", []).append(term_val.text)

    disc = tmp.get("discrim")
    if disc:
        tmpid = f"{tmp['n']} ({disc})"
    else:
        tmpid = tmp["n"]
    tmp["n"] = tmpid
    data[tmpid] = tmp

# And also run through all the data and update the children before pickling
for x in data.values():
    parent = data.get(x.get("broader"))
    if parent:
        parent.setdefault("c", []).append(x["n"])

TBC = []
for k, x in data.items():
    print("%s | %s", k, x)
    pad = list(getpath(x))
    x["p"] = [pobj["n"] for pobj in pad]
    if "TBC" in x["p"]:
        TBC.append(k)
for k_todelete in TBC:
    del data[k_todelete]

if "TBC" in data["<CIT>"]["c"]:
    data["<CIT>"]["c"].remove("TBC")
if "TBC" in data:
    del data["TBC"]

# Add "notation" numeric codes
def fix_nums(obj):
    nn = 1
    for kid in sorted([data[k] for k in obj.get("c", [])], key=lambda x: x.get("seq")):
        kid["nn"] = nn
        nn += 1
        fix_nums(kid)


fix_nums(data["<CIT>"])

for obj in data.values():
    pad = list(getpath(obj))
    pad_n = [str(pobj.get("nn", "")) for pobj in pad[1:]]
    pad_n.append(str(obj.get("nn", "")))
    obj["nnn"] = ".".join(pad_n)

# And now update the children items to have the numeric kids
for obj in data.values():
    if "c" in obj:
        obj["c"] = [data[k].get("nnn") for k in obj.get("c", [])]

data["<CIT>"]["nnn"] = "<CIT>"

with open("CIT.dmp", "w", encoding="utf8") as OUT:
    for obj in data.values():
        obj["type"] = "CIT"
        obj["id"] = f"cit_{obj['nnn'].replace('.', '_')}"
        obj["term_zh"] = obj["n"]
        if "nn" in obj:
            del obj["nn"]
        if "nnn" in obj:
            obj["cit"] = obj["nnn"]
            del obj["nnn"]
        obj["n"] = obj["cit"]
        if "seq" in obj:
            del obj["seq"]
        if "p" in obj:
            del obj["p"]
        for k, v in obj.items():
            if v:
                if type(v) is list:
                    new_v = " " + "\n; ".join(v)
                else:
                    v = str(v)
                    new_v = "\n".join([f" {vv}" for vv in v.split("\n")])
                OUT.write(f"{k.upper()}{new_v}\n")
        OUT.write("$\n")
