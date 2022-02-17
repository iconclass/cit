import os, sys
from urllib.parse import quote_plus
import textbase
from rich import print
from rich.progress import track
from rdflib import Namespace
from rdflib.namespace import SKOS, RDF, RDFS, DCTERMS
from rdflib import Graph, URIRef, Literal, BNode


def terminology():

    g = Graph()
    CIT = Namespace("https://cit.iconclass.org/id/")
    CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
    AAT = Namespace("http://vocab.getty.edu/aat/")
    LA = Namespace("https://linked.art/ns/terms/")
    DIG = Namespace("http://www.ics.forth.gr/isl/CRMdig/")

    g.bind("la", LA)
    g.bind("cit", CIT)
    g.bind("rdf", RDF)
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    g.bind("crm", CRM)
    g.bind("aat", AAT)
    g.bind("dig", DIG)

    def ga(*kw):
        s, p, o = kw
        g.add((s, p, o))

    for obj in track(textbase.parse("CIT.dmp")):
        n = obj["ID"][0]

        N = URIRef(CIT[n])
        ga(N, RDF.type, SKOS.Concept)
        ga(N, RDF.type, CRM["E55_Type"])
        ga(N, SKOS.notation, Literal(n))
        ga(N, SKOS.inScheme, URIRef("https://chineseiconography.org/rdf/2021/10/"))

        if "TERM_EN" in obj:
            ga(N, SKOS.prefLabel, Literal(obj["TERM_EN"][0], lang="en"))
        if "TERM_ZH" in obj:
            ga(N, SKOS.prefLabel, Literal(obj["TERM_ZH"][0], lang="zh"))
        if "TERM_PINYIN" in obj:
            ga(N, SKOS.altLabel, Literal(obj["TERM_PINYIN"][0], lang="zh-Latn"))

        b = obj.get("BROADER")
        if b:
            ga(N, SKOS.broader, CIT[b[0]])
        for c in obj.get("C.INV", []):
            ga(N, SKOS.narrower, CIT[c])
        for r in obj.get("R", []):
            ga(N, SKOS.related, CIT[r])
        for kw_en in obj.get("KW_EN", []):
            ga(N, DCTERMS.subject, Literal(kw_en, lang="en"))
        for kw_zh in obj.get("KW_ZH", []):
            ga(N, DCTERMS.subject, Literal(kw_zh, lang="zh"))

    ga(CIT["VANDA"], RDFS.label, Literal("Victoria and Albert Museum, London"))
    ga(CIT["VANDA"], CRM["P2_has_type"], AAT["300312281"])

    ga(CIT["CMA"], RDFS.label, Literal("Cleveland Museum of Art, Cleveland"))
    ga(CIT["CMA"], CRM["P2_has_type"], AAT["300312281"])

    ga(CIT["MET"], RDFS.label, Literal("Metropolitan Museum of Art, New York, NY"))
    ga(CIT["MET"], CRM["P2_has_type"], AAT["300312281"])

    ga(CIT["NPM"], RDFS.label, Literal("National Palace Museum, Taipei"))
    ga(CIT["NPM"], CRM["P2_has_type"], AAT["300312281"])

    # Some Linked Art compliancy
    ga(AAT["300133025"], RDF.type, CRM["E55_Type"])
    ga(AAT["300133025"], RDFS.label, Literal("Artwork", lang="en"))

    for obj in track(textbase.parse("CATALOG.dmp")):
        n = obj["ID"][0]

        N = URIRef(CIT[n])
        ga(N, RDF.type, CRM["E22_Human-Made_Object"])
        ga(N, CRM["P2_has_type"], AAT["300133025"])

        for h in obj.get("HIM", []):
            if h == "CIT":
                continue
            ga(N, CRM["P52_has_current_owner"], CIT[h])

        shows = BNode()
        ga(N, CRM["P65_shows_visual_item"], shows)

        imgurl = obj.get("URL.IMAGE")[0]
        shownby = BNode()
        ga(shows, LA["digitally_shown_by"], shownby)
        ga(shownby, RDF.type, DIG["D1_Digital_Object"])
        ga(
            shownby,
            LA["access_point"],
            URIRef(f"https://cit.iconclass.org/iiif/3/{imgurl}/full/max/0/default.jpg"),
        )
        dav = BNode()
        ga(shownby, LA["digitally_available_via"], dav)
        ga(dav, RDF.type, LA["DigitalService"])
        ga(dav, DCTERMS.conformsTo, URIRef("http://iiif.io/api/image"))
        ga(
            dav,
            LA["access_point"],
            URIRef(f"https://cit.iconclass.org/iiif/3/{imgurl}"),
        )

        for cits in obj.get("CIT.ID", []):
            ga(shows, DCTERMS.subject, CIT[cits])

        if "DESCRIPTION" in obj:
            ga(N, RDFS.label, Literal(obj["DESCRIPTION"][0], lang="en"))
        if "TITLE" in obj:
            ga(N, DCTERMS.title, Literal(obj["TITLE"][0]))
        if "URL.WEBPAGE" in obj:
            ga(N, LA["access_point"], URIRef("https://www.eg.museum/edu/page1.html"))
            ga(
                URIRef(obj["URL.WEBPAGE"][0]),
                RDF.type,
                DIG["D1_Digital_Object"],
            )

        prdctn = BNode()
        ga(N, CRM["P108i_was_produced_by"], prdctn)
        ga(prdctn, RDF.type, CRM["E12_Production"])

        if "DATE" in obj:
            timespan = BNode()
            ga(prdctn, CRM["P4_has_time-span"], timespan)
            ga(timespan, RDF.type, CRM["E52_Time-Span"])
            ga(timespan, CRM["P78_is_identified_by"], Literal(obj["DATE"][0]))
        artist = obj.get("PERSON.ARTIST")
        if artist and artist[0].lower() != "unknown":
            prodperson = BNode()
            ga(prdctn, CRM["P14_carried_out_by"], prodperson)
            ga(prodperson, RDF.type, CRM["E21_Person"])
            ga(prodperson, RDFS.label, Literal(artist[0]))

    return g


if __name__ == "__main__":
    thegraph = terminology()

    open("cit.ttl", "w").write(thegraph.serialize())
