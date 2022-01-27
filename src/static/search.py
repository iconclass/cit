from ui_util import *


async def tree_clicker(event):
    anid = find_attr_parents(event.target, "anid")
    if anid and len(anid) > 0:
        document.location = "/terms/" + anid


async def results_clicker(event):
    anid = find_attr_parents(event.target, "anid")
    if anid and len(anid) > 0:
        document.location = "/items/" + anid


async def do_search():
    q = searchbox.value
    search_url = "/search/?q=" + encodeURIComponent(q)
    document.location = search_url


async def searchbox_keyup(event):
    if event.keyCode == 13:
        do_search()


async def init():
    searchbox.addEventListener("keyup", searchbox_keyup)
    results_element.addEventListener("click", results_clicker)
    tree_element.addEventListener("click", tree_clicker)


window.addEventListener("load", init)
