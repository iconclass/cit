from fastapi import Depends, FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from .config import ORIGINS, DATABASE_URL, ROOT_ID, HELP_PATH, SITE_URL
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .translations import texts
from functools import partial
from jinja2 import Markup
import databases
import markdown
import sqlite3
import random
import json
import os
from typing import List
import httpx

database = databases.Database(DATABASE_URL)
app = FastAPI(openapi_url="/openapi")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def T(lang: str, token: str):
    return texts.get(lang, {}).get(token, "")


def get_T(lang: str):
    return partial(T, lang)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def homepage(request: Request, lang: str = Query(None)):
    set_language = False
    if lang == None:
        lang = request.cookies.get("lang")
    else:
        set_language = True
    if lang is None:
        lang = "en"

    obj = await get_obj(ROOT_ID, {"C": "C_INV"})

    response = templates.TemplateResponse(
        "homepage.html",
        {"request": request, "lang": lang[:2], "obj": obj, "T": get_T(lang)},
    )
    if set_language:
        response.set_cookie(key="lang", value=lang)

    return response


@app.get("/id/{anid:str}.json", response_class=JSONResponse)
async def id_json(request: Request, anid: str):
    obj = await get_obj(anid)
    return obj


async def do_search_(q: str, tipe: str, cit=[]):
    if tipe == "image":
        return await search_images(q, cit)
    else:
        return await search_terms(q)


async def search_terms(q: str):
    query = "SELECT objs.obj FROM objs INNER JOIN txt_idx ON txt_idx.id = objs.id, json_each(objs.obj, '$.TYPE[0]') WHERE json_each.value = 'CIT'"
    query += " AND txt_idx.text MATCH :q"

    results = await database.fetch_all(query, values={"q": q})
    return results


async def search_images(q: str, cit=[]):
    if q:
        query = "SELECT objs.obj FROM objs INNER JOIN txt_idx ON txt_idx.id = objs.id, json_each(objs.obj, '$.TYPE[0]') WHERE json_each.value = 'image'"
        query += " AND txt_idx.text MATCH :q"
        if cit:
            query += " AND objs.id IN (SELECT obj_id FROM objs_cit WHERE cit_id = :cit)"
            results = await database.fetch_all(query, values={"q": q, "cit": cit[0]})
        else:
            results = await database.fetch_all(query, values={"q": q})
    else:
        query = "SELECT objs.obj FROM objs, json_each(objs.obj, '$.TYPE[0]') WHERE json_each.value = 'image'"
        if cit:
            query += " AND objs.id IN (SELECT obj_id FROM objs_cit WHERE cit_id = :cit)"
            results = await database.fetch_all(query, values={"cit": cit[0]})
        else:
            query += " ORDER BY RANDOM() LIMIT 20"
            results = await database.fetch_all(query)
    return results


async def do_search(q: str, tipe: str = None, cit=[]):
    try:
        results = await do_search_(q, tipe, cit)
    except sqlite3.OperationalError:
        try:
            results = await do_search_(
                f'"{q}"', tipe
            )  # Try it with an exact match to circumvent problems with punctuation
        except sqlite3.OperationalError:
            return []

    return [json.loads(row[0]) for row in results]


async def get_objs_for_term(term: str):
    query = "SELECT DISTINCT objs.obj FROM objs, json_each(objs.obj, '$.CIT_ID') WHERE json_each.value = :term"
    try:
        results = await database.fetch_all(query, values={"term": term})
    except sqlite3.OperationalError:
        return []
    return [json.loads(row[0]) for row in results]


async def get_obj_count_for_term(term: str, exact: bool = False):
    if exact:
        query = "SELECT COUNT(*) from objs_cit where cit_id = :term AND exact = 1"
    else:
        query = "SELECT COUNT(*) from objs_cit where cit_id = :term"
    try:
        results = await database.fetch_all(query, values={"term": term})
    except sqlite3.OperationalError:
        return 0
    return results[0][0]


async def get_obj(anid: str, filled={}):
    query = "SELECT obj FROM objs WHERE id = :anid"
    results = await database.fetch_one(query, values={"anid": anid})
    if not results:
        raise HTTPException(status_code=404)
    obj = json.loads(results[0])
    obj["OBJS_PATH"] = [await get_obj_count_for_term(anid)]
    obj["OBJS_EXACT"] = [await get_obj_count_for_term(anid, True)]

    for k, v in filled.items():
        thelist = [await get_obj(kind) for kind in obj.get(v, [])]
        obj[k] = sorted(
            thelist,
            key=lambda x: [int(oo) for oo in x.get("CIT", ["0"])[0].split(".")],
        )
    return obj


@app.get("/terms/{anid:path}", response_class=HTMLResponse, include_in_schema=False)
async def terms(request: Request, anid: str):
    lang = request.cookies.get("lang") or "en"
    anid = anid or ROOT_ID
    obj = await get_obj(anid)

    return templates.TemplateResponse(
        "terms.html",
        {
            "request": request,
            "lang": lang[:2],
            "anid": anid,
            "path": json.dumps(obj.get("P", [obj["ID"]])),
            "obj": obj,
            "T": get_T(lang),
            "ROOT_ID": ROOT_ID,
        },
    )


async def get_terms_from_results(results: list, sort_by: str = "freq"):
    terms_buf = {}
    for obj in results:
        for term in obj.get("CIT_ID", []):
            terms_buf.setdefault(term, set()).add(obj["ID"][0])
    terms = [(len(y), await get_obj(x)) for x, y in terms_buf.items()]
    for term_buf_len, term in terms:
        term["OBJ_COUNT"] = [term_buf_len]

    if sort_by == "freq":
        terms.sort(key=lambda x: x[0])
        return reversed([t for l, t in terms])
    else:
        return sorted(
            [t for l, t in terms],
            key=lambda x: [int(oo) for oo in x.get("CIT", ["0"])[0].split(".")],
        )


@app.get(
    "/search/",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def search(
    request: Request, q: str = "", page: int = 1, cit: List[str] = Query(None)
):
    SIZE = 20
    lang = request.cookies.get("lang") or "en"
    results = await do_search(q, "image", cit)
    terms = await get_terms_from_results(results)
    total = len(results)
    start = (page - 1) * SIZE
    stop = start + SIZE
    paged = results[start:stop]
    pages = round(total / SIZE)

    if total == 1:
        anid = results[0].get("ID")[0]
        return RedirectResponse("/items/" + anid)

    return templates.TemplateResponse(
        f"search.html",
        {
            "request": request,
            "lang": lang[:2],
            "q": q,
            "cit": cit,
            "page": page,
            "results": results,
            "terms": terms,
            "paged": paged,
            "pages": pages,
            "total": total,
            "T": get_T(lang),
            "ROOT_ID": ROOT_ID,
        },
    )


@app.get(
    "/fragments/search/{tipe:str}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def fragments_search(
    request: Request,
    tipe: str,
    q: str = "",
    page: int = 1,
    cit: List[str] = Query(None),
):
    lang = request.cookies.get("lang") or "en"
    results = await do_search(q, tipe, cit)

    return templates.TemplateResponse(
        f"search_{tipe}.html",
        {
            "request": request,
            "lang": lang[:2],
            "q": q,
            "results": results,
            "T": get_T(lang),
        },
    )


@app.get(
    "/fragments/focus/{lang:str}/{anid:str}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def focus(request: Request, lang: str, anid: str):
    SAMPLE_SIZE = 9
    lang = request.cookies.get("lang") or "en"
    obj = await get_obj(anid, {"C": "C_INV", "R": "R"})

    return templates.TemplateResponse(
        "focus.html",
        {
            "request": request,
            "lang": lang[:2],
            "anid": anid,
            "obj": obj,
            "T": get_T(lang),
        },
    )


@app.get(
    "/items/{anid:str}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def items(request: Request, anid: str = "", q: str = ""):
    lang = request.cookies.get("lang") or "en"

    return templates.TemplateResponse(
        "item.html",
        {
            "request": request,
            "lang": lang[:2],
            "anid": anid,
            "obj": await get_obj(anid, {"CIT": "CIT_ID"}),
            "T": get_T(lang),
        },
    )


@app.get(
    "/help/{page:str}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def help(request: Request, page: str):
    lang = request.cookies.get("lang") or "en"
    lang = lang.split("_")[0]

    infilepath = os.path.join(HELP_PATH, f"{lang}_{page}.md")
    if not os.path.exists(infilepath):
        raise HTTPException(status_code=404, detail=f"Page [{page}] not found")
    md = markdown.Markdown(
        output_format="html5", extensions=["nl2br", "meta", "attr_list"]
    )
    html = md.convert(open(infilepath).read())

    return templates.TemplateResponse(
        "help.html",
        {
            "request": request,
            "lang": lang[:2],
            "page": page,
            "content": Markup(html),
            "T": get_T(lang),
        },
    )


@app.get(
    "/mirador/",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def mirador(request: Request):
    lang = request.cookies.get("lang") or "en"
    return templates.TemplateResponse(
        "mirador.html",
        {
            "request": request,
            "SITE_URL": SITE_URL,
            "T": get_T(lang),
        },
    )


@app.get(
    "/chord/",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def chord(request: Request):
    lang = request.cookies.get("lang") or "en"
    return templates.TemplateResponse(
        "chord.html",
        {
            "request": request,
            "lang": lang,
            "SITE_URL": SITE_URL,
            "T": get_T(lang),
        },
    )


@app.get("/api/iiif/presentation/{anid:str}/info.json", response_class=JSONResponse)
async def iiif_presentation(anid: str):
    obj = await get_obj(anid)
    # fetch the image details from the IIIF image API
    url_image = obj.get("URL_IMAGE", [None])[0]
    with httpx.Client() as client:
        r = client.get(f"https://cit.iconclass.org/iiif/3/{url_image}/info.json")
        iiif_json = r.json()
    resp = {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@id": f"{SITE_URL}/api/iiif/presentation/{anid}/manifest",
        "@type": "sc:Manifest",
        "label": obj.get("ID")[0],
        "viewingDirection": "left-to-right",
        "metadata": [
            {"label": "URI", "value": "<a href='/items/" + anid + "'>View in CIT</a>"},
            {"label": "Title", "value": obj.get("TITLE", ["- untitled -"])[0]},
            {
                "label": "Description",
                "value": obj.get("DESCRIPTION", ["- no description - "])[0],
            },
            {"label": "Terms English", "value": " ".join(obj.get("CIT", []))},
            {
                "label": "Holding Institution",
                "value": obj.get("LOCATION_INV", ["unknown"])[0],
            },
            {
                "label": "Date",
                "value": obj.get("DATE", ["unknown"])[0],
            },
            {
                "label": "Artist",
                "value": obj.get("PERSON_ARTIST", ["unknown"])[0],
            },
        ],
        "thumbnail": {
            "@id": f"https://cit.iconclass.org/iiif/2/{url_image}/full/256,/0/default.jpg",
            "@type": "dctypes:Image",
            "format": "image/jpeg",
            "service": {
                "@context": "http://iiif.io/api/image/2/context.json",
                "profile": "http://iiif.io/api/image/2/level1.json",
                "@id": f"https://cit.iconclass.org/iiif/2/{url_image}",
            },
        },
        "sequences": [
            {
                "@type": "sc:Sequence",
                "canvases": [
                    {
                        "@id": f"{SITE_URL}/api/iiif/presentation/{anid}/canvas0",
                        "@type": "sc:Canvas",
                        "label": anid,
                        "height": iiif_json["height"],
                        "width": iiif_json["width"],
                        "images": [
                            {
                                "@id": f"{SITE_URL}/id/{anid}/annotation",
                                "@type": "oa:Annotation",
                                "motivation": "sc:painting",
                                "resource": {
                                    "@id": f"https://cit.iconclass.org/iiif/2/{url_image}/full/full/0/default.jpg",
                                    "@type": "dctypes:Image",
                                    "format": "image/jpeg",
                                    "height": iiif_json["height"],
                                    "width": iiif_json["width"],
                                    "service": {
                                        "@context": "http://iiif.io/api/image/2/context.json",
                                        "@id": f"https://cit.iconclass.org/iiif/2/{url_image}",
                                        "profile": "level2",
                                    },
                                },
                                "on": f"{SITE_URL}/api/iiif/presentation/{anid}/canvas0",
                            }
                        ],
                    }
                ],
            }
        ],
    }
    return resp
