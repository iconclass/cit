from ui_util import *


def toggle_visibility(anelement):
    if anelement.style.display == "block":
        anelement.style.display = "none"
    else:
        anelement.style.display = "block"


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

    for notationtext in document.querySelectorAll(".notationtext"):
        notationtext.classList.remove("focussed")
    node.text_element.classList.add("focussed")

    kids_element = document.getElementById("kids" + desired)
    icon_element = document.getElementById("icon" + desired)
    if len(node["C"]) > 0:
        kind_icon = None
    else:
        kind_icon = dot
    if kids_element.style.display == "none":
        kids_element.style.display = "block"
        icon_element.innerHTML = kind_icon or caret_down_fill
        if node.fragment is None:
            furi = "/fragments/focus/{}/{}".format(
                document.LANG, encodeURIComponent(desired)
            )
            result = await fetch(furi)
            response = await result.text()
            node.fragment = response
            if len(node["C"]) > 0:
                await build(desired, kids_element)
    else:
        kids_element.style.display = "none"
        icon_element.innerHTML = kind_icon or caret_right_fill
    results_element.innerHTML = node.fragment


async def do_search():
    q = searchbox.value
    search_url = "/fragments/search/CIT?q=" + encodeURIComponent(q)
    result = await fetch(search_url)
    response = await result.text()
    results_element.innerHTML = response


async def searchbox_keyup(event):
    if event.keyCode == 13:
        do_search()


async def searchbutton_clicker(event):
    event.preventDefault()
    do_search()


async def init():
    searchbutton.addEventListener("click", searchbutton_clicker)
    searchbox.addEventListener("keyup", searchbox_keyup)
    results_element.addEventListener("click", result_clicker)
    tree_element.addEventListener("click", tree_clicker)
    await build(document.ROOT_ID, tree_element, document.PATH)
    if document.anid != document.ROOT_ID:
        focus_node(document.anid)


window.addEventListener("load", init)
