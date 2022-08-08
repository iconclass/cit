import xml.etree.ElementTree as ET
from rich.progress import track
import sys

def getpath(data, obj):
    parent = obj.get("broader")
    if parent:
        for p in getpath(data, data.get(parent)):
            yield p
        yield data.get(parent)


def gettit(elem, xpath, dest, field):
    d = elem.find(xpath)
    if d is not None and d.text:
        dest[field] = d.text


def read_xml(filepath="CIT.xml"):
    # Note, parsing file: CIT 20190312 gives error in XML
    # encountering character  '\x02' embedded in file.
    # Looks like all the source have this so do a search and replace to fix it.
    filecontents = open(filepath, encoding="utf8").read().replace("\x02", "")
    doc = ET.fromstring(filecontents)
    return doc


def clean_TBC(data):
    # There is a "holding" entry named TBC which the CIT editors used for WIP items
    # these need to be checked for and deleted
    # This sytep also adds a "p" key to objects
    TBC = []
    for k, x in data.items():
        pad = list(getpath(data, x))
        for pobj in pad:
            if pobj["n"] == "TBC":
                TBC.append(k)
        x["p"] = list(
            reversed([pobj["id"] for pobj in pad])
        )  # the generator yields parents backwards, so reverse it.
    for k_todelete in TBC:
        del data[k_todelete]
    if "TBC" in data["<CIT>"]["c"]:
        data["<CIT>"]["c"].remove("TBC")
    if "TBC" in data:
        del data["TBC"]


def dump(data, filepath="CIT.dmp"):
    with open(filepath, "w", encoding="utf8") as OUT:
        for obj in data.values():
            for k, v in obj.items():
                if v:
                    if type(v) is list:
                        new_v = " " + "\n; ".join(v)
                    else:
                        v = str(v)
                        new_v = "\n".join([f" {vv}" for vv in v.split("\n")])
                    OUT.write(f"{k.upper()}{new_v}\n")
            OUT.write("$\n")


def main():
    data = read_entries()

    # fill in the children for parents using broader
    for x in data.values():
        parent = data.get(x.get("broader"))
        if parent:
            parent.setdefault("c", []).append(x["id"])

    clean_TBC(data)

    # We record the term_zh as 'n' initially, as it is used for reference in the V&A CMS
    # But now update the field values, also fix the broader and related
    for obj in data.values():
        obj["term_zh"] = obj["n"]
        for field in ("n", "discrim"):
            if field in obj:
                del obj[field]
        if "broader" in obj:
            obj["broader"] = data.get(obj["broader"], {}).get("id")
        if "r" in obj:
            obj["r"] = list(
                filter(None, [data.get(rr, {}).get("id") for rr in obj["r"]])
            )

    dump(data, filepath="../data/CIT.dmp")
    return data


def read_entries():
    data = {}
    seq = 0
    doc = read_xml(sys.argv[1])
    for entry in track(doc.findall(".//mus_ixthes")):
        seq += 1
        tmp = {"seq": seq, "type": "CIT"}
        tmp["n"] = entry.find(".//mus_auth_thes_term").text
        gettit(entry, "mus_auth_thes_b_term", tmp, "broader")
        gettit(entry, "mus_auth_thes_term_discrim", tmp, "discrim")
        gettit(entry, "sys_id", tmp, "id")
        related = [
            r_term.text for r_term in entry.findall(".//mus_auth_thes_r_terms/_")
        ]
        if related:
            tmp["r"] = related

        # Get the Chinese keywords stored in use_for
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
    return data


if __name__ == "__main__":
    data = main()
