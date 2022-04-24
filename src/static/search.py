from ui_util import *


async def tree_clicker(event):
    anid = find_attr_parents(event.target, "anid")
    if len(anid) > 0:
        focus_node(anid)


async def focus_node(desired):
    if desired not in NODE_MAP:
        return

    node = NODE_MAP[desired]

    for notationtext in document.querySelectorAll(".notationtext"):
        notationtext.classList.remove("focussed")
    node.text_element.classList.add("focussed")

    topstatus = document.getElementById("topstatus")
    topstatus.innerHTML = node["OBJS_PATH"][0]

    kids_element = document.getElementById("kids" + desired)
    icon_element = document.getElementById("icon" + desired)
    if len(node["C_INV"]) > 0:
        kind_icon = None
    else:
        kind_icon = dot
    if kids_element.style.display == "none":
        kids_element.style.display = "block"
        icon_element.innerHTML = kind_icon or caret_down_fill
        if node.fragment is None:
            furi = "/fragments/search/image?f=A_CIT_{}".format(
                encodeURIComponent(desired)
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


async def results_clicker(event):
    anid = find_attr_parents(event.target, "anid")
    if anid and len(anid) > 0:
        document.location = "/items/" + anid


async def filters_clicker(event):
    event.preventDefault()
    action_needed = False

    data_remove = find_attr_parents(event.target, "data-remove")
    if data_remove and len(data_remove) > 0:
        vals = data_remove.split("_")
        if len(vals) == 3:
            op, field, val = vals
            fields = document.PARAMS.get(op, {})
            values = fields.get(field, [])
            document.PARAMS[op][field] = [aval for aval in values if aval != val]
            action_needed = True
    data_add = find_attr_parents(event.target, "data-add")
    if data_add and len(data_add) > 0:
        vals = data_add.split("_")
        if len(vals) == 3:
            op, field, val = vals
            fields = document.PARAMS.get(op, {})
            values = fields.get(field, [])
            values.append(val)
            document.PARAMS.setdefault(op, {})[field] = values
            action_needed = True
    if action_needed == True:
        search_url = "/search/?" + make_searchparams()
        document.location = search_url


async def termsused_clicker(event):
    anid = find_attr_parents(event.target, "anid")
    vals = document.PARAMS.get("A", {}).get("CIT", [])
    if anid not in vals:
        vals.append(anid)
    document.PARAMS.setdefault("A", {})["CIT"] = vals
    search_url = "/search/?" + make_searchparams()
    document.location = search_url


async def collections_clicker(event):
    anid = find_attr_parents(event.target, "data-coll")
    vals = document.PARAMS.get("A", {}).get("COL", [])
    if anid not in vals:
        vals.append(anid)
    document.PARAMS.setdefault("A", {})["COL"] = vals
    search_url = "/search/?" + make_searchparams()
    document.location = search_url


async def do_search():
    q = searchbox.value
    search_url = "/search/?q=" + encodeURIComponent(q)
    document.location = search_url


async def searchbox_keyup(event):
    if event.keyCode == 13:
        do_search()


async def searchbutton_clicker(event):
    event.preventDefault()
    do_search()


document.PARAMS = {}
document.Q = ""


def make_searchparams():
    buf = []
    for op, fields in document.PARAMS.items():
        for field, vals in fields.items():
            for val in vals:
                buf.append("f=" + op + "_" + field + "_" + val)
    if len(document.Q) > 0:
        buf.append("q=" + encodeURIComponent(document.Q))
    return "&".join(buf)


async def init():
    searchbutton.addEventListener("click", searchbutton_clicker)
    searchbox.addEventListener("keyup", searchbox_keyup)
    results_element.addEventListener("click", results_clicker)
    termsused_element = document.getElementById("termsused")
    termsused_element.addEventListener("click", termsused_clicker)
    filters_element = document.getElementById("filters")
    if filters_element:
        filters_element.addEventListener("click", filters_clicker)
    collections_element = document.getElementById("collections")
    if collections_element:
        collections_element.addEventListener("click", collections_clicker)

    sp = __new__(URL(document.location)).searchParams
    for param in sp.entries():
        if param[0] == "q":
            document.Q = param[1]
        if param[0] == "f":
            vals = param[1].split("_")
            if len(vals) == 3:
                op, field, val = vals
                document.PARAMS.setdefault(op, {}).setdefault(field, []).append(val)


window.addEventListener("load", init)


def initmsnry():
    msnry = __new__(
        Masonry(grid, {"columnWidth": ".grid-item", "itemSelector": ".grid-item"})
    )
    msnry.layout()


grid = document.querySelector(".grid")
imagesLoaded(grid, initmsnry)
