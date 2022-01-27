from htmltree import *
from ui_util import *


NODE_MAP = {}

caret_right_fill = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-caret-right-fill" viewBox="0 0 16 16">
  <path d="m12.14 8.753-5.482 4.796c-.646.566-1.658.106-1.658-.753V3.204a1 1 0 0 1 1.659-.753l5.48 4.796a1 1 0 0 1 0 1.506z"/>
</svg>"""
caret_down_fill = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-caret-down-fill" viewBox="0 0 16 16">
  <path d="M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z"/>
</svg>"""
dot = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-dot" viewBox="0 0 16 16">
  <path d="M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z"/>
</svg>"""


def toggle_visibility(anelement):
    if anelement.style.display == "block":
        anelement.style.display = "none"
    else:
        anelement.style.display = "block"


async def get_obj(anid):
    if anid in NODE_MAP:
        return NODE_MAP[anid]
    result = await fetch("/id/" + anid + ".json")
    response = await result.json()
    obj = dict(response)
    NODE_MAP[anid] = obj
    return obj


async def result_clicker(event):
    anid = find_attr_parents(event.target, "anid")
    atipe = find_attr_parents(event.target, "atipe")
    if atipe and len(atipe) > 0:
        document.location = "/items/" + anid
    node = await get_obj(anid)
    await build(document.ROOT_ID, tree_element, node["P"])


async def tree_clicker(event):
    anid = find_attr_parents(event.target, "anid")
    if len(anid) > 0:
        focus_node(anid)


async def focus_node(desired):
    if desired not in NODE_MAP:
        return
    history.pushState({}, "", "/terms/" + encodeURIComponent(desired))
    node = NODE_MAP[desired]
    kids_element = document.getElementById("kids" + desired)
    icon_element = document.getElementById("icon" + desired)
    if len(node["C_INV"]) > 0:
        kind_icon = None
    else:
        kind_icon = dot
    if kids_element.style.display == "none":
        kids_element.style.display = "block"
        icon_element.innerHTML = kind_icon or caret_down_fill
        caret_down_fill
        if node.fragment is None:
            furi = "/fragments/focus/{}/{}".format(
                document.LANG, encodeURIComponent(desired)
            )
            result = await fetch(furi)
            response = await result.text()
            node.fragment = response
            if len(node["C_INV"]) > 0:
                await build(desired, kids_element)
    else:
        kids_element.style.display = "none"
        icon_element.innerHTML = kind_icon or caret_right_fill
    results_element.innerHTML = node.fragment


async def build(anid, an_element, path=[]):
    node = await get_obj(anid)

    for kind in node.get("C_INV", []):
        kind_node = await get_obj(kind)

        if kind in path:
            kids_display = "block"
        else:
            kids_display = "none"

        if kind_node.kids_element:
            # We have already added this child
            kind_node.kids_element.style.display = "block"
        else:

            if len(kind_node["C_INV"]) > 0:
                kind_icon = caret_right_fill
            else:
                kind_icon = dot
            txt = kind_node["TERM_" + document.LANG.upper()][0]
            an_element.insertAdjacentHTML(
                "beforeend",
                Div(
                    Span(
                        kind_icon,
                        id="icon" + kind,
                        anid=kind,
                        style={"margin-right": "0.6ch"},
                    ),
                    Span(txt, anid=kind),
                    Div(id="kids" + kind, style={"display": kids_display}),
                    id=kind,
                    style={"padding-left": "1ch", "cursor": "pointer"},
                    anid=kind,
                    title=kind_node["CIT"],
                ).render(),
            )
            kind_node.fragment = None
            kind_node.element = document.getElementById(kind)
            kind_node.kids_element = document.getElementById("kids" + kind)
        if kind in path:
            await build(kind, kind_node.kids_element, path)


async def do_search():
    q = searchbox.value
    search_url = "/fragments/search/CIT?q=" + encodeURIComponent(q)
    result = await fetch(search_url)
    response = await result.text()
    results_element.innerHTML = response


async def searchbox_keyup(event):
    if event.keyCode == 13:
        do_search()


async def init():
    searchbox.addEventListener("keyup", searchbox_keyup)
    results_element.addEventListener("click", result_clicker)
    tree_element.addEventListener("click", tree_clicker)
    await build(document.ROOT_ID, tree_element, document.PATH)
    if document.anid != document.ROOT_ID:
        focus_node(document.anid)


window.addEventListener("load", init)
