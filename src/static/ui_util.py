from htmltree import *

searchbox = document.getElementById("searchbox")
searchbutton = document.getElementById("searchbutton")
results_element = document.getElementById("results")
tree_element = document.getElementById("thetree")
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


async def get_obj(anid):
    if anid in NODE_MAP:
        return NODE_MAP[anid]
    result = await fetch("/id/" + anid + ".json")
    response = await result.json()
    obj = dict(response)
    NODE_MAP[anid] = obj
    return obj


async def build(anid, an_element, path=[]):
    node = await get_obj(anid)

    for kind in node.get("C", []):
        kind_node = await get_obj(kind)

        if kind in path:
            kids_display = "block"
        else:
            kids_display = "none"

        if kind_node.kids_element:
            # We have already added this child
            kind_node.kids_element.style.display = "block"
        else:

            if len(kind_node["C"]) > 0:
                kind_icon = caret_right_fill
            else:
                kind_icon = dot
            try:
                txt = kind_node["TERM_" + document.LANG.upper()][0]
            except:
                txt = "‡"
            an_element.insertAdjacentHTML(
                "beforeend",
                Div(
                    Span(
                        kind_icon,
                        id="icon" + kind,
                        anid=kind,
                        style={"margin-right": "0.6ch"},
                    ),
                    Span(txt, anid=kind, id="text" + kind, _class="notationtext"),
                    Div(id="kids" + kind, style={"display": kids_display}),
                    id=kind,
                    style={"padding-left": "1ch", "cursor": "pointer"},
                    anid=kind,
                    title=kind_node["ID"][0],
                    obj_count=node["OBJS_PATH"],
                ).render(),
            )
            kind_node.fragment = None
            kind_node.element = document.getElementById(kind)
            kind_node.kids_element = document.getElementById("kids" + kind)
            kind_node.text_element = document.getElementById("text" + kind)
        if kind in path:
            await build(kind, kind_node.kids_element, path)


def find_attr_parents(element, attr):
    val = element.getAttribute(attr)
    if val and len(val) > 0:
        return val
    parent = element.parentElement
    if parent:
        return find_attr_parents(parent, attr)
