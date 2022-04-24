from ui_util import *


async def tree_clicker(event):
    anid = find_attr_parents(event.target, "anid")
    if anid and len(anid) > 0:
        document.location = "/search/?f=A_CIT_" + anid


async def results_clicker(event):
    anid = find_attr_parents(event.target, "anid")
    if anid and len(anid) > 0:
        document.location = "/items/" + anid


async def do_search():
    q = searchbox.value
    search_url = "/fragments/search/image?q=" + encodeURIComponent(q)
    result = await fetch(search_url)
    response = await result.text()
    results_element.innerHTML = response


async def searchbox_keyup(event):
    if event.keyCode == 13:
        do_search()


async def mirador_clicker(event):
    a = inLightbox.getAttribute("checked")
    if a == "":
        inLightbox.removeAttribute("checked")
        document.lightbox = [x for x in document.lightbox if x != document.anid]
        window.localStorage.setItem("lightbox_1", JSON.stringify(document.lightbox))
    else:
        inLightbox.setAttribute("checked", "")
        document.lightbox.push(document.anid)
        window.localStorage.setItem("lightbox_1", JSON.stringify(document.lightbox))


async def init():
    searchbox.addEventListener("keyup", searchbox_keyup)
    results_element.addEventListener("click", results_clicker)
    tree_element.addEventListener("click", tree_clicker)
    mirador_button = document.getElementById("mirador_button")

    inLightbox = document.getElementById("inLightbox")
    inLightbox.addEventListener("click", mirador_clicker)
    # Check to see if this item is in the lightbox localstorage
    lightbox = window.localStorage.getItem("lightbox_1")
    if lightbox:
        document.lightbox = JSON.parse(lightbox)
        if document.anid in lightbox:
            inLightbox.setAttribute("checked", "")
        else:
            inLightbox.removeAttribute("checked")
    else:
        document.lightbox = []


window.addEventListener("load", init)
