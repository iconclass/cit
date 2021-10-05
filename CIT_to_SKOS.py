import textbase
import ndjson, json
import random
import rich

data = []
CIT_URI = "https://chineseiconography.org/"

for o in textbase.parse("CIT.dmp"):
    if o["N"][0] == "<CIT>":
        continue
    obj_template = {
        "@context": {
            "skos": "http://www.w3.org/2004/02/skos/core#",
            "dc": "http://purl.org/dc/elements/1.1/",
            "uri": "@id",
            "lang": "@language",
            "value": "@value",
        }
    }
    tmp_graph = {
        "uri": f"{CIT_URI}rdf/{o['N'][0]}",
        "@type": "skos:Concept",
        "skos:inScheme": f"{CIT_URI}rdf/2021/10/",
    }
    if len(o.get("C", [])) > 0:
        tmp_graph["skos:narrower"] = [
            {"uri": f"{CIT_URI}rdf/{c}"} for c in o.get("C", [])
        ]
    if "TERM_ZH" in o:
        tmp_graph["skos:prefLabel"] = [{"lang": "zh", "value": o["TERM_ZH"][0]}]
    if "TERM_EN" in o:
        tmp_graph.setdefault("skos:prefLabel", []).append(
            {"lang": "en", "value": o["TERM_EN"][0]}
        )
    if len(o.get("KW_EN", [])) > 0:
        tmp_graph["dc:subject"] = [
            {"lang": "en", "value": kw} for kw in o.get("KW_EN", [])
        ]
    if len(o.get("KW_ZH", [])) > 0:
        tmp_graph["dc:subject"] = [
            {"lang": "zh", "value": kw} for kw in o.get("KW_ZH", [])
        ]
    obj_template["@graph"] = [tmp_graph]
    data.append(obj_template)

with open("CIT-SKOS.ndjson", "w") as f:
    ndjson.dump(data, f)

rich.print(
    f"\nA sample entry from the {len(data)} [bold red]CIT[/bold red] entries dataset:"
)
rich.print(json.dumps(random.choice(data), indent=2))
