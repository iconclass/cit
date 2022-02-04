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
            furi = "/fragments/search/image/?cit={}".format(encodeURIComponent(desired))
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


async def termsused_clicker(event):
    anid = find_attr_parents(event.target, "anid")
    if anid not in NODE_MAP:
        node = await get_obj(anid)
        await build(document.ROOT_ID, tree_element, node["P"])
    focus_node(anid)


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


async def init():
    searchbutton.addEventListener("click", searchbutton_clicker)
    searchbox.addEventListener("keyup", searchbox_keyup)
    results_element.addEventListener("click", results_clicker)
    tree_element.addEventListener("click", tree_clicker)
    termsused_element = document.getElementById("termsused")
    termsused_element.addEventListener("click", termsused_clicker)
    await build(document.ROOT_ID, tree_element)


window.addEventListener("load", init)


def initmsnry():
    msnry = __new__(
        Masonry(grid, {"columnWidth": ".grid-item", "itemSelector": ".grid-item"})
    )
    msnry.layout()


grid = document.querySelector(".grid")
imagesLoaded(grid, initmsnry)
